import glob
import json
import os

import pandas as pd

ANALYSIS_ID = "179f9bb9-dd28-4d2c-84f7-5bdfd8f4d421"
DOWNLOAD_NAME = "dc_medium_office_v3"
base_dir = os.path.join(os.path.dirname(__file__), "simulations", DOWNLOAD_NAME)
json_variable_file = os.path.join(base_dir, 'selected_json_variables.json')

if not os.path.exists(base_dir):
    raise Exception(f"Path does not exist to process {base_dir}")


def return_value(metadatum, json_results):
    """Return the value of a multilevel dictionary. Should use jsonpath-ng"""
    if metadatum["level_2"]:
        return json_results[metadatum["level_1"]][metadatum["level_2"]]
    elif metadatum["level_1"]:
        return json_results[metadatum["level_1"]]
    else:
        return ""


def process_directory(dir, json_variable_file):
    """ Process the JSON files that exist in the directory"""
    with open(json_variable_file) as f:
        vars_metadata = json.load(f)

        new_data = {}

        for var in vars_metadata:
            if os.path.exists(os.path.join(dir, var["file"])):
                # Put empty rename to at end
                metadata = sorted(
                    var["data"], key=lambda k: (k['order'], k['rename_to'] or "z", k['level_1'], k['level_2'])
                )

                # Now load the result json file (var["file"])
                with open(os.path.join(dir, var["file"])) as f2:
                    json_results = json.load(f2)

                    # save the updated data
                    for metadatum in metadata:
                        if metadatum["rename_to"]:
                            new_data[metadatum["rename_to"]] = [return_value(metadatum, json_results)]
                        elif metadatum["level_2"]:
                            new_data[f"{metadatum['level_1']}.{metadatum['level_2']}"] = [
                                return_value(metadatum, json_results)]
                        else:
                            new_data[metadatum['level_1']] = [return_value(metadatum, json_results)]

        return (new_data)


files = glob.glob(f"{base_dir}/*/*.csv")
simulation_results_file = os.path.join(base_dir, 'simulation_results.csv')
main_df = None
for index, csv_file in enumerate(files):
    dir = os.path.dirname(csv_file)
    print(f"Processing directory: {dir}")
    json_results = process_directory(dir, json_variable_file)

    # add the JSON data to the time series data. Each row gets the same data as it qualifies the simulation

    df = pd.read_csv(csv_file) #.head(100)

    # load new data and fill down the data to the same number of rows in the CSV file
    df2 = pd.DataFrame(json_results)
    df2 = pd.concat([df2] * len(df.index), ignore_index=True)

    # append the columns
    df = pd.concat([df, df2], axis=1)

    if index == 0:
        main_df = df
    else:
        # check that the columns are the same
        col_diff = list(set(main_df.columns) - set(df.columns))
        if len(col_diff) != 0:
            print(f"Uh oh, columns don't match {col_diff}, skipping dataframe")
        else:
            main_df = pd.concat([main_df, df], sort=False)

    # df.to_csv(os.path.join(dir, 'data.out'), index=False)
    # if index >= 2:
    #     break

# go through all the column names are remove any spaces
main_df.columns = df.columns.str.replace(' ', '')
main_df.to_csv(simulation_results_file, index=False)

# if there is a desire to see runtime performance of measures, then look at this gist:
#    https://gist.github.com/nllong/d17836137bc5d90b7783e1403a38e867
