import glob
import json
import os

from metamodeling.post_process.json_processor import JsonProcessorFile
from metamodeling.post_process.openstudio_server import OpenStudioServerAPI

ANALYSIS_ID = "1da39de3-dcd0-4ca9-bade-ee701240f388"
DOWNLOAD_NAME = "dc_medium_office_v2"
SERVER_URL = "http://bball-130553.nrel.gov"
# SERVER_URL = "http://localhost"
SERVER_PORT = "8080"

base_dir = os.path.join(os.path.dirname(__file__), "simulations", DOWNLOAD_NAME)
os.makedirs(base_dir, exist_ok=True)

api = OpenStudioServerAPI(SERVER_URL, SERVER_PORT)
if api.alive():
    status = api.get_analysis_status(ANALYSIS_ID, 'batch_run')

    if status in ['completed', 'started']:
        results = api.get_analysis_results(ANALYSIS_ID)
        for dp in results["data"]:
            dir = f"{base_dir}/{dp['_id']}"
            if os.path.exists(dir):
                print('Download already exists for simulation')
            else:
                print(f'Saving simulation result to {dir}')
                os.makedirs(dir, exist_ok=True)

                # save off the JSON snippet into the new directory
                with open(f"{dir}/variables.json", 'w') as f:
                    json.dump(dp, f, indent=2)

                # grab the datapoint json, and save off the results (which contain some of the resulting covariates)
                dp_results = api.get_datapoint(dp["_id"])
                with open(f"{dir}/results.json", 'w') as f:
                    json.dump(dp_results['data_point']['results'], f, indent=2)

                # save off some of the results: timeseries, datapoint json, and out.osw
                api.download_datapoint_report(dp["_id"], 'dc_timeseries_reports_report_timeseries.csv', dir)
                api.download_datapoint_report(dp["_id"], 'out.osw', dir)


# Process a single directory to create a metadata file for post processing
all_jsons = glob.glob(f"{base_dir}/*/*.json")
json_files = []
for j in all_jsons:
    if os.path.basename(j) not in [os.path.basename(f) for f in json_files]:
        json_files.append(j)

print(f"There are {len(json_files)} unique result json files to process")
jp = JsonProcessorFile(json_files)
all_vars_file = os.path.join(base_dir, 'all_json_variables.json')
r = jp.save_as(all_vars_file)
if r:
    print(f"All JSON variables are saved to {all_vars_file}")
    print("It is recommended to rename this file and cull to only the variable of desire")
else:
    print("All JSON variable file was NOT updated")



