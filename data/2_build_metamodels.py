# Note that the run_commands will be killed if this script is killed (as it should).

import os
import subprocess

METAMODEL_VERSION = 'v4'


def run_command(run_dir, command):
    print(f"Running in {run_dir}")
    print(f"Command in {command}")
    curdir = os.getcwd()
    try:
        os.chdir(run_dir)

        p = subprocess.Popen(command, stdout=subprocess.PIPE)
        for line in p.stdout:
            print(line.strip())
        p.wait()
        print(f"Returned from command with {p.returncode}")
        if p.returncode != 0:
            raise Exception("Command failed with nonzero exit code")
    finally:
        os.chdir(curdir)




# path to the metamodel folder
run_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metamodel'))

cmd = f"metamodel.py inspect -f definitions/mediumoffice_{METAMODEL_VERSION}.json -a mediumoffice_{METAMODEL_VERSION} -m RandomForest"
run_command(run_path, cmd.split(' '))

cmd = f"metamodel.py build -f definitions/mediumoffice_{METAMODEL_VERSION}.json -a mediumoffice_{METAMODEL_VERSION} -m RandomForest"
result = run_command(run_path, cmd.split(' '))

cmd = f"metamodel.py evaluate -f definitions/mediumoffice_{METAMODEL_VERSION}.json -a mediumoffice_{METAMODEL_VERSION} -m RandomForest"
run_command(run_path, cmd.split(' '))

cmd = f"metamodel.py validate -f definitions/mediumoffice_{METAMODEL_VERSION}.json -a mediumoffice_{METAMODEL_VERSION} -m RandomForest"
run_command(run_path, cmd.split(' '))
