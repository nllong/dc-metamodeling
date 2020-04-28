require 'date'
require 'erb'

# start the measure
class DcTimeseriesReports < OpenStudio::Measure::ReportingMeasure
  # human readable name
  def name
    # Measure name should be the title case of the class name.
    return 'DC Timeseries Reports'
  end

  # human readable description
  def description
    return 'Timeseries data for DC metamodels'
  end

  # human readable description of modeling approach
  def modeler_description
    return ''
  end

  def log(str)
    puts "#{Time.now}: #{str}"
  end

  # define the arguments that the user will input
  def arguments
    args = OpenStudio::Measure::OSArgumentVector.new

    # this measure does not require any user arguments, return an empty list

    return args
  end
  
  # define the outputs that the measure will create
  def outputs
    outs = OpenStudio::Measure::OSOutputVector.new
  
    outs << OpenStudio::Measure::OSOutput.makeDoubleOutput('energyplus_runtime')
    
    return outs
  end
  
  # return a vector of IdfObject's to request EnergyPlus objects needed by the run method
  def energyPlusOutputRequests(runner, user_arguments)
    super(runner, user_arguments)

    result = OpenStudio::IdfObjectVector.new

    # use the built-in error checking
    return result unless runner.validateUserArguments(arguments, user_arguments)

    # Output:Variable,*,Facility Heating Setpoint Not Met Time,hourly; !- Zone Sum [hr]
    # Output:Variable,*,Facility Cooling Setpoint Not Met Time,hourly; !- Zone Sum [hr]
    # Output:Variable,*,Facility Heating Setpoint Not Met While Occupied Time,hourly; !- Zone Sum [hr]
    # Output:Variable,*,Facility Cooling Setpoint Not Met While Occupied Time,hourly; !- Zone Sum [hr]

    result << OpenStudio::IdfObject.load('Output:Variable,,Site Mains Water Temperature,hourly;').get
    result << OpenStudio::IdfObject.load('Output:Variable,,Site Outdoor Air Drybulb Temperature,hourly;').get
    result << OpenStudio::IdfObject.load('Output:Variable,,Site Outdoor Air Relative Humidity,hourly;').get
    result << OpenStudio::IdfObject.load('Output:Meter,Cooling:Electricity,hourly;').get
    result << OpenStudio::IdfObject.load('Output:Meter,Heating:Electricity,hourly;').get
    result << OpenStudio::IdfObject.load('Output:Variable,*,Zone Predicted Sensible Load to Setpoint Heat Transfer Rate,hourly;').get
    result << OpenStudio::IdfObject.load('Output:Meter,Heating:Gas,hourly;').get
    result << OpenStudio::IdfObject.load('Output:Meter,InteriorLights:Electricity,hourly;').get
    result << OpenStudio::IdfObject.load('Output:Meter,Fans:Electricity,hourly;').get
    result << OpenStudio::IdfObject.load('Output:Meter,InteriorEquipment:Electricity,hourly;').get
    result << OpenStudio::IdfObject.load('Output:Meter,ExteriorLighting:Electricity,hourly;').get
    result << OpenStudio::IdfObject.load('Output:Meter,Electricity:Facility,hourly;').get
    result << OpenStudio::IdfObject.load('Output:Meter,Gas:Facility,hourly;').get

    return result
  end

  def extract_timeseries_into_matrix(sqlfile, data, variable_name, key_value = nil, default_if_empty=0)
    log "Executing query for #{variable_name}"
    if key_value
      ts = sqlfile.timeSeries('RUN PERIOD 1', 'Hourly', variable_name, key_value)
    else
      ts = sqlfile.timeSeries('RUN PERIOD 1', 'Hourly', variable_name)
    end
    log 'Iterating over timeseries'
    column = [variable_name.delete(':')] # Set the header of the data to the variable name, removing :
  
    if ts.empty?
      log "No time series for #{variable_name}:#{key_value}... defaulting to #{default_if_empty}"
      # needs to be data.size-1 since the column name is already stored above (+=)
      column += [default_if_empty] * (data.size-1)
    else
      ts = ts.get if ts.respond_to?(:get)
      ts = ts.first if ts.respond_to?(:first)

      start = Time.now
      # Iterating in OpenStudio can take up to 60 seconds with 10min data. The quick_proc takes 0.03 seconds.
      # for i in 0..ts.values.size - 1
      #   log "... at #{i}" if i % 10000 == 0
      #   column << ts.values[i]
      # end

      quick_proc = ts.values.to_s.split(',')

      # the first and last have some cleanup items because of the Vector method
      quick_proc[0] = quick_proc[0].gsub(/^.*\(/, '')
      quick_proc[-1] = quick_proc[-1].delete(')')
      column += quick_proc

      log "Took #{Time.now - start} to iterate"
    end

    log 'Appending column to data'

    # append the data to the end of the rows
    if column.size == data.size
      data.each_index do |index|
        data[index] << column[index]
      end
    end

    log "Finished extracting #{variable_name}"
  end

  # define what happens when the measure is run
  def run(runner, user_arguments)
    super(runner, user_arguments)

    # use the built-in error checking
    return false unless runner.validateUserArguments(arguments, user_arguments)

    # get the last model and sql file
    model = runner.lastOpenStudioModel
    if model.empty?
      runner.registerError('Cannot find last model.')
      return false
    end
    model = model.get

    sqlFile = runner.lastEnergyPlusSqlFile
    if sqlFile.empty?
      runner.registerError('Cannot find last sql file.')
      return false
    end
    sqlFile = sqlFile.get
    model.setSqlFile(sqlFile)

    # create a new csv with the values and save to the reports direcoty.
    # assumptions:
    #   - all the variables exist
    #   - data are the same length

    # initialize the rows with the header
    puts 'Starting to process Timeseries data'
    rows = [
        # Initial header row
        ['Date Time', 'Month', 'Day', 'Day of Week', 'Hour', 'Minute']
    ]

    # just grab one of the variables to get the date/time stamps
    ts = sqlFile.timeSeries('RUN PERIOD 1', 'Hourly', 'Cooling:Electricity')
    unless ts.empty?
      ts = ts.first

      # Save off the date time values
      ts.dateTimes.each_with_index do |dt, _index|
        rows << [DateTime.parse(dt.to_s).strftime('%m/%d/%Y %H:%M'), dt.date.monthOfYear.value, dt.date.dayOfMonth, dt.date.dayOfWeek.value, dt.time.hours, dt.time.minutes]
      end
    end

    # add in the other variables by columns -- should really pull this from the report variables defined above
    extract_timeseries_into_matrix(sqlFile, rows, 'Site Outdoor Air Drybulb Temperature', 'Environment', 0)
    extract_timeseries_into_matrix(sqlFile, rows, 'Site Outdoor Air Relative Humidity', 'Environment', 0)
    extract_timeseries_into_matrix(sqlFile, rows, 'Heating:Electricity', nil, 0)
    extract_timeseries_into_matrix(sqlFile, rows, 'Heating:Gas', nil, 0)
    extract_timeseries_into_matrix(sqlFile, rows, 'Cooling:Electricity', nil, 0)
    extract_timeseries_into_matrix(sqlFile, rows, 'Electricity:Facility', nil, 0)
    extract_timeseries_into_matrix(sqlFile, rows, 'Gas:Facility', nil, 0)
    # extract_timeseries_into_matrix(sqlFile, rows, 'Nothing:Burger', nil, 0)
    
    # Figure out how to add this variable, probably by zone:
    # "Output:Variable,*,Zone Predicted Sensible Load to Setpoint Heat Transfer Rate,hourly,timestep;").get

    # sum up a couple of the columns and create a new column
    var_1 = nil
    var_2 = nil
    rows.each_with_index do |row, index|
      if index == 0
        runner.registerInfo(row.join(','))
        # Get the index of the columns to add
        var_1 = row.index('HeatingElectricity')
        var_2 = row.index('HeatingGas')

        if var_1 && var_2
          rows[index] << 'HeatingTotal'
          next
        else
          break
        end
      end

      # runner.registerInfo("Index #{index}, Value 1 #{row[var_1]}, Value 2 #{row[var_2]}, Class #{row[var_1]}")
      # runner.registerInfo("rows[index] class #{rows[index]}")
      rows[index] << row[var_1].to_f + row[var_2].to_f
    end

    # convert this to CSV object
    File.open('./report_timeseries.csv', 'w') do |f|
      rows.each do |row|
        f << row.join(',') << "\n"
      end
    end

    # Find the total runtime for energyplus and save it into a registerValue
    total_time = -999
    location_of_file = ['../eplusout.end', './run/eplusout.end']
    first_index = location_of_file.map {|f| File.exist?(f)}.index(true)
    if first_index
      match = File.read(location_of_file[first_index]).to_s.match(/Elapsed.Time=(.*)hr(.*)min(.*)sec/)
      total_time = match[1].to_i * 3600 + match[2].to_i * 60 + match[3].to_f
    end

    runner.registerValue('energyplus_runtime', total_time, 'sec')

    return true
  ensure
    sqlFile.close if sqlFile
  end
end

# register the measure to be used by the application
DcTimeseriesReports.new.registerWithApplication
