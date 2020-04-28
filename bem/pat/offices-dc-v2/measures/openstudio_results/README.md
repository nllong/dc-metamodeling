

###### (Automatically generated documentation)

# OpenStudio Results

## Description
This measure creates high level tables and charts pulling both from model inputs and EnergyPlus results. It has building level information as well as detail on space types, thermal zones, HVAC systems, envelope characteristics, and economics. Click the heading above a chart to view a table of the chart data.

## Modeler Description
For the most part consumption data comes from the tabular EnergyPlus results, however there are a few requests added for time series results. Space type and loop details come from the OpenStudio model. The code for this is modular, making it easy to use as a template for your own custom reports. The structure of the report uses bootstrap, and the graphs use dimple js.

## Measure Type
ReportingMeasure

## Taxonomy


## Arguments


### Model Summary

**Name:** building_summary_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Annual Overview

**Name:** annual_overview_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Monthly Overview

**Name:** monthly_overview_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Utility Bills/Rates

**Name:** utility_bills_rates_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Envelope

**Name:** envelope_section_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Space Type Breakdown

**Name:** space_type_breakdown_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Space Type Summary

**Name:** space_type_details_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Interior Lighting Summary

**Name:** interior_lighting_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Plug Loads Summary

**Name:** plug_loads_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Exterior Lighting

**Name:** exterior_light_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Water Use Equipment

**Name:** water_use_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### HVAC Load Profiles

**Name:** hvac_load_profile,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Zone Conditions

**Name:** zone_condition_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Zone Overview

**Name:** zone_summary_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Zone Equipment Detail

**Name:** zone_equipment_detail_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Air Loops Detail

**Name:** air_loops_detail_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Plant Loops Detail

**Name:** plant_loops_detail_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Outdoor Air

**Name:** outdoor_air_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Cash Flow

**Name:** cost_summary_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Site and Source Summary

**Name:** source_energy_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false

### Schedule Overview

**Name:** schedules_overview_section,
**Type:** Boolean,
**Units:** ,
**Required:** true,
**Model Dependent:** false





## Outputs






























electricity_ip, natural_gas_ip, additional_fuel_ip, district_heating_ip, district_cooling_ip, total_site_eui, eui, net_site_energy, annual_peak_electric_demand, unmet_hours_during_occupied_cooling, unmet_hours_during_occupied_heating, first_year_capital_cost, annual_utility_cost, total_lifecycle_cost


## Contributors
 - Primary development by the commercial buildings team at NREL
 - Support for SI units reporting developed by Julien Marrec with EffiBEM and Julien Thirifays with IGRETEC