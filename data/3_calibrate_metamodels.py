from platypus import NSGAII, Problem, Real, Permutation, Subset, Integer
from platypus.operators import PCX, PMX, CompoundOperator, GAOperator, SSX, Multimethod, SBX, UNDX, \
    DifferentialEvolution
import os
import math
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from functools import partial
import random
import shutil
from jinja2 import Environment, PackageLoader
from metamodeling.metamodels import Metamodels
from metamodeling.analysis_definition.analysis_definition import AnalysisDefinition

# ------------ set values --------------
OPTIMIZE_VERSION = 'v3'
METAMODEL_VERSION = 'v3'
DOWNSAMPLE_VALUE = 0.05
random.seed(1880)

env = Environment(loader=PackageLoader('metamodel', 'analysis_definitions'))
medium_office_template = env.get_template('medium_office.json.template')
# Load in the models for analysis
metamodel = Metamodels(f'../metamodel/definitions/mediumoffice_{METAMODEL_VERSION}.json')
metamodel.set_analysis(f'mediumoffice_{METAMODEL_VERSION}')
metamodel_root_path = os.path.join(
    os.path.dirname(__file__), '..', 'metamodel', 'output', f'mediumoffice_{METAMODEL_VERSION}'
)
# Load the existing models
if metamodel.models_exist('RandomForest',
                          models_to_load=['GasFacility', 'ElectricityFacility'],
                          downsample=DOWNSAMPLE_VALUE, root_path=metamodel_root_path):
    metamodel.load_models('RandomForest',
                          models_to_load=['GasFacility', 'ElectricityFacility'],
                          downsample=DOWNSAMPLE_VALUE, root_path=metamodel_root_path)
else:
    raise Exception('Metamodels do not exist')

# List of buildings to optimize
df = pd.read_csv('buildings_to_optimize.csv')
print(df.describe())


def run_sim(x, y, metamodel, output_dir, model_template, counter=[0], history=[]):
    counter[0] += 1

    print(x)
    sim_dir = os.path.join(output_dir, f'sim_{counter[0]}')
    if not os.path.exists(sim_dir):
        os.makedirs(sim_dir)

    # set the values in the template
    template_data = {
        "floor_area": row['REPORTEDBUILDINGGROSSFLOORAREA'],
        "lpd": x[0],
        "number_of_stories": x[1][0],
        "aspect_ratio": x[2],
        "hours_of_operation_start": x[3],
        "hours_of_operation_duration": x[4],
    }
    new_office_description = model_template.render(**template_data)
    input_file = os.path.join(sim_dir, 'medium_office.json')
    with open(os.path.join(sim_dir, 'medium_office.json'), 'w') as f:
        f.write(new_office_description)

    analysis = AnalysisDefinition(input_file)
    analysis.load_weather_file(
        '../bem/weather/USA_VA_Arlington/USA_VA_Arlington-Ronald.Reagan.Washington.Natl.AP.724050_TMY3.epw')

    # convert the analysis definition to a dataframe for use in the metamodel
    data = analysis.as_dataframe()
    data = metamodel.yhats(data, 'RF', ['ElectricityFacility', 'GasFacility'])
    data['RF_ElectricityFacility'] = data['RF_ElectricityFacility'] / (3600 * 1000)  # J to kWh
    data['RF_GasFacility'] = (data['RF_GasFacility'] * 3.412) / (3600 * 1000 * 100)  # J to kWh to kBtu to therms

    # calculate the modeled totals
    electricity_hat = sum(data['RF_ElectricityFacility'])  # kwh
    gas_hat = sum(data['RF_GasFacility'])  # therms
    eui_hat = (electricity_hat * 3.412 + gas_hat * 100) / y['REPORTEDBUILDINGGROSSFLOORAREA']

    electricity_actual = y['ELECTRICITYUSE_GRID_KWH']
    if math.isnan(y['NATURALGASUSE_THERMS']):
        gas_actual = 0
    else:
        gas_actual = y['NATURALGASUSE_THERMS']
    eui_actual = y['SITEEUI_KBTU_FT']

    electricity_error = math.sqrt((electricity_actual - electricity_hat) ** 2)
    gas_error = math.sqrt((gas_actual - gas_hat) ** 2)
    eui_error = math.sqrt((eui_actual - eui_hat) ** 2)

    # Create heat maps of the modeled data
    responses = [
        'RF_ElectricityFacility',
        'RF_GasFacility',
    ]
    for response in responses:
        heatdata = data[["DayOfYear", "Hour", response]].pivot("DayOfYear", "Hour", response)
        f, ax = plt.subplots(figsize=(5, 12))
        sns.heatmap(heatdata)
        filename = f"{sim_dir}/{response.replace(' ', '_')}.png"
        plt.savefig(filename)
        plt.close('all')

    history.append({
        "index": counter[0],
        "inputs": template_data,
        "outputs": {
            "electricity_hat": electricity_hat,
            "gas_hat": gas_hat,
            "eui_hat": eui_hat,
            "electricity_error": electricity_error,
            "gas_error": gas_error,
            "eui_error": eui_error,
        }
    })
    print(f"electricity_hat: {electricity_hat} | electricity_actual: {electricity_actual} | {electricity_error}")
    print(f"gas_hat: {gas_hat} | gas_actual: {gas_actual} | {gas_error}")
    print(f"eui_hat: {eui_hat} | eui_actual: {eui_actual} | {eui_error}")

    # minimize to 0
    return eui_error, electricity_error, gas_error


optimize_path = os.path.join(os.path.dirname(__file__), 'output', f'optimize_{OPTIMIZE_VERSION}')
for index, row in df.iterrows():
    history = []
    counter = [0]
    building_dir = os.path.join(optimize_path, f'building_{index}')

    # remove the previous results
    if os.path.exists(building_dir):
        shutil.rmtree(building_dir)

    print(row)

    # run the metamodel simulation
    f_partial = partial(
        run_sim, y=row, metamodel=metamodel, output_dir=building_dir, model_template=medium_office_template,
        counter=counter, history=history
    )
    problem = Problem(nvars=5, nobjs=3, function=f_partial)
    # problem.types[0] = Subset(['a', 'b'], 1)
    problem.types[0] = Real(1, 20)  # lpd
    problem.types[1] = Subset(range(1, 13), 1)  # number of stories
    problem.types[2] = Real(1, 5)  # aspect_ratio
    problem.types[3] = Real(6, 10)  # hours_of_operation_start
    problem.types[4] = Real(8, 16)  # hours_of_operation_duration

    # problem.types[1] = Integer(1, 13)
    algorithm = NSGAII(problem, population_size=15, variator=SSX())
    algorithm.run(30)

    for h in history:
        print(h)

    # save the history to the building_dir
    with open(os.path.join(building_dir, 'history.json'), 'w') as f:
        json.dump(history, f, indent=2)

# for s in algorithm.result:
#     print(f"{s.objectives[0]}")


# # plot the results using matplotlib
# import matplotlib.pyplot as plt
#
# plt.scatter([s.objectives[0] for s in algorithm.result],
#             [s.objectives[1] for s in algorithm.result])
# plt.xlim([0, 1.1])
# plt.ylim([0, 1.1])
# plt.xlabel("$f_1(x)$")
# plt.ylabel("$f_2(x)$")
# plt.show()
