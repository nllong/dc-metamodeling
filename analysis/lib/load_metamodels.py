from metamodeling.metamodels import Metamodels
from metamodeling.analysis_definition.analysis_definition import AnalysisDefinition
import os


def load_metamodels(metamodel_version, downsample_value):
    file_def = os.path.abspath(f'../metamodel/definitions/mediumoffice_{metamodel_version}.json')
    if not os.path.exists(file_def):
        raise Exception(f"Metamodel definition does not exist: {file_def}")

    root_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', '..', 'metamodel', 'output', f'mediumoffice_{metamodel_version}'
    ))

    metamodel = Metamodels(file_def)
    metamodel.set_analysis(f'mediumoffice_{metamodel_version}')
    # Load the existing models
    if metamodel.models_exist('RandomForest',
                              models_to_load=['GasFacility', 'ElectricityFacility'],
                              downsample=downsample_value, root_path=root_path):
        metamodel.load_models('RandomForest',
                              models_to_load=['GasFacility', 'ElectricityFacility'],
                              downsample=downsample_value, root_path=root_path)
    else:
        raise Exception(f'Metamodels do not exist: {file_def}')

    return metamodel

