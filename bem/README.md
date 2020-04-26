# DC Metamodeling - BEM

This repository contains the BEM files needed for generating the metamodels for Washington DC.

# Instructions

* Clone this repository

    * Note that the measures in this repository are copies from various locations. Contact @nllong with specifics 
    if needed.  
    * If updating measures, then launch PAT and go to Window -> Set MyMeasure directory 
    and set the directory to the checked out measures.*
    
* If running simulations, then following instructions below on "Running Simulations" before launching PAT. If PAT is launched first, then PAT will use it's own version of OpenStudio Server which doesn't support running the algorithms needed for these projects. 

* Launch PAT (= Version 2.9.1)


## Running Simulations

In order to run the simulations locally, you will need to run a docker-based version of OpenStudio Server. Note that you must run the commands below before launching PAT, otherwise, PAT will launch it's own version of OpenStudio Server (in local mode) on the same port as the dockerized OpenStudio Server.

* Install [Docker CE](https://docs.docker.com/install/)
* Clone [OpenStudio Server](https://github.com/nrel/openstudio-server). Use the 2.9.1-LTS branch. 

```bash
git clone https://github.com/nrel/OpenStudio-server.git

# use the 2.9.1 long term support branch of the server
git checkout 2.9.X-LTS
```

* Build and launch the containers (include number of workers if planning on scaling)

```bash
cd <root-of-openstudio-server-checkout>
docker-compose up --build
```

```bash
OS_SERVER_NUMBER_OF_WORKERS=n docker-compose up
```

* Scale the number of workers (from n above, if desired)

```bash
docker-compose scale worker=n
```

* It is helpful to remove PAT's running instance of PAT to save resources. To stop PAT from spinning up resources make sure to run the following command line a few seconds after launching and loading your PAT project.

```bash
for KILLPID in `ps ax | grep -e 'ParametricAnalysisTool.app.Contents.Resources.ruby.bin.ruby' -e 'mongod.*--logpath' -e 'delayed_job' -e 'rails' | grep -v grep | awk '{print $1;}'`; do 
	echo "Killing process $KILLPID"
	kill -9 $KILLPID;
done
```

## Downloading Simulations

The downloading of the results are in the `download_data.py` file in the root directory of bem. Simply edit this 
file with the updated analysis ID from OpenStudio Server and the name of the models that are being downloads. The name
is a custom name that can be used to identify the simulations.

Run the file by calling:

```bash
python download_data.py
```

The results will download in the base directory defined in the file. Note that if the directory of the datapoint 
already exists (even if there aren't simulations results in the datapoint directory), then the data will 
not be downloaded; however downloading will still try to download other datapoints.

