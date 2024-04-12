# pm4py-mdl
Multi-Dimensional Log Module for PM4Py

## Forked from [pm4py-mdl](https://github.com/Javert899/pm4py-mdl)

This repo is a fork of the original [pm4py-mdl](https://github.com/Javert899/pm4py-mdl) repository. Consider the original repository is last updated in 2021, and this fork is created to resolve the compatibility issues.

## Installation

> **Note:** The package `pm4pymdl` available on Pypi is not compatible with the new version of `pandas` and `pm4py`. Please follow the below steps to install the package.

### Step 1: Clone the repository

Open the terminal and run the following command to clone the repository.

```bash
git clone https://github.com/ZhipengHe/pm4py-mdl.git
```

### Step 2: Stetup the environment

Since some packages used in this repository are not updated, it is recommended to create a new environment using `conda`.

```bash
conda create -n pm4py-mdl
conda activate pm4py-mdl
conda install -c conda-forge python=3.10
```

After creating the environment, install the required packages using the following command.

```bash
cd pm4py-mdl # Move to the cloned repository
pip install -r requirements.txt
```

Then, all the required packages will be installed.

### Step 3: Run the web application

The web application is created with flask. To run the web application, use the following command.

```bash
python main.py
```

Then, the web application will be available at `http://127.0.0.1:5000/`.

### Step 4: Use the package

To understand how to use the package, please refer to folder `example_code`.

## License

This repository is licensed under the MIT License.


