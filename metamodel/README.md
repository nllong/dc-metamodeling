# Building Metamodels

* Make sure to install the Metamodeling Framework, look in the requirements.txt as example for installing with git.

* Run the following command to inspect the results file (using RandomForest is not required)

```bash
cd metamodel
metamodel.py inspect -f definitions/mediumoffice_v1.json -a mediumoffice_v1 -m RandomForest
metamodel.py inspect -f definitions/mediumoffice_v2.json -a mediumoffice_v2 -m RandomForest
```

* Build the RandomForest model

```bash
metamodel.py build -f definitions/mediumoffice_v1.json -a mediumoffice_v1 -m RandomForest

metamodel.py build -f definitions/mediumoffice_v2.json -a mediumoffice_v2 -m RandomForest
```

* Evaluate and Validate model

```bash
metamodel.py evaluate -f definitions/mediumoffice_v1.json -a mediumoffice_v1 -m RandomForest
metamodel.py validate -f definitions/mediumoffice_v1.json -a mediumoffice_v1 -m RandomForest

metamodel.py evaluate -f definitions/mediumoffice_v2.json -a mediumoffice_v2 -m RandomForest
metamodel.py validate -f definitions/mediumoffice_v2.json -a mediumoffice_v2 -m RandomForest

```


# Analysis the Data

You need to install orca, psutil, and requests in order to generate the images

```bash
npm install -g electron@1.8.4 orca
pip install psutil requests
```