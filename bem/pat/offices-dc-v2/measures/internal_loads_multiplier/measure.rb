class InternalLoadsMultiplier < OpenStudio::Measure::ModelMeasure
  # require all .rb files in resources folder
  Dir[File.dirname(__FILE__) + '/resources/*.rb'].each {|file| require file}

  # resource file modules
  include OsLib_HelperMethods

  # human readable name
  def name
    return "Internal Loads Multiplier"
  end

  # human readable description
  def description
    return "Multipliers for LPD, EPD, and people densities."
  end

  # human readable description of modeling approach
  def modeler_description
    return "Multipliers for LPD, EPD, and people densities."
  end

  # define the arguments that the user will input
  def arguments(model)
    args = OpenStudio::Ruleset::OSArgumentVector.new

    lpd = OpenStudio::Ruleset::OSArgument.makeDoubleArgument("lpd_multiplier", true)
    lpd.setDisplayName("LPD Multiplier")
    lpd.setDefaultValue(1.0)
    lpd.setUnits("W/ft^2") # The resulting unit
    lpd.setDescription("Multiply the LPD in the building by this multiplier. Retail LPD is typically 1.3, Small Office 1.0")
    args << lpd

    epd = OpenStudio::Ruleset::OSArgument.makeDoubleArgument("epd_multiplier", true)
    epd.setDisplayName("Electric Equipment Power Density Multiplier")
    epd.setDefaultValue(1.0)
    epd.setUnits("W/ft^2") # The resulting unit
    epd.setDescription("Multiply the EPD in the building by this value")
    args << epd

    people_per_floor_area = OpenStudio::Ruleset::OSArgument.makeDoubleArgument("people_per_floor_area_multiplier", true)
    people_per_floor_area.setDisplayName("People per floor area multipleir")
    people_per_floor_area.setDefaultValue(1.0)
    people_per_floor_area.setUnits("People/ft^2") # The resulting unit
    args << people_per_floor_area

    return args
  end

  # define what happens when the measure is run
  def run(model, runner, user_arguments)
    super(model, runner, user_arguments)

    # assign the user inputs to variables
    args = OsLib_HelperMethods.createRunVariables(runner, model, user_arguments, arguments(model))

    return false unless args

    # array of altered lighting defitinos (tracking so isn't altered twice)
    altered_light_defs = []

    ave_lpd = 0
    ave_lpd_count = 0
    ave_epd = 0
    ave_pd = 0
    ave_space_count = 0

    # loop through space types altering loads
    model.getSpaceTypes.each do |space_type|
      next if space_type.spaces.size == 0
      next if space_type.standardsSpaceType.get == 'Attic'

      # update lights
      space_type.lights.each do |light|
        light_def = light.lightsDefinition
        unless altered_light_defs.include? light_def
          light_def.setWattsperSpaceFloorArea(light_def.wattsperSpaceFloorArea.get * args['lpd_multiplier'])
          altered_light_defs << light_def
          ave_lpd += light_def.wattsperSpaceFloorArea.get
          ave_lpd_count += 1
        end
      end

      # replace electric equipment
      if space_type.electricEquipmentPowerPerFloorArea.is_initialized
        space_type.setElectricEquipmentPowerPerFloorArea(space_type.electricEquipmentPowerPerFloorArea.get * args['epd_multiplier'])
        ave_epd += space_type.electricEquipmentPowerPerFloorArea.get
      end

      # replace people
      if space_type.peoplePerFloorArea.is_initialized
        space_type.setPeoplePerFloorArea(space_type.peoplePerFloorArea.get * args['people_per_floor_area_multiplier'])
        ave_pd += space_type.peoplePerFloorArea.get
      end

      ave_space_count += 1
    end

    if ave_lpd_count > 0
      runner.registerValue('lpd_average', ave_lpd / ave_lpd_count, 'W/m2')
    end

    if ave_space_count > 0
      runner.registerValue('epd_average', ave_epd / ave_space_count, 'W/m2')
      runner.registerValue('ppl_average', ave_pd / ave_space_count, 'People/m2')
    end

    return true
  end
end

# register the measure to be used by the application
InternalLoadsMultiplier.new.registerWithApplication
