# Swallow - SQL Connectivity Testing App

## Overview
Swallow is an internship project for testing connectivity to a SQL server using various drivers. It includes a runner that runs connectivity tests based on a configuration JSON file. The project supports multiple drivers, including ODBC, JDBC, MSSQL and SQLClient (you can see available_drivers.py for a list of all available driver versions).

## Installation
Before installing this project, make sure you have Docker and Python installed on your system. Once you have these prerequisites installed, you can install the project's dependencies by running the following command:

```
pip install schedule python-dotenv
docker-compose build
```

## Usage
To use this project, first modify the sql_tests_config.json file. You can specify multiple drivers and endpoints in this file. Once you have configured the project, you can run it by executing the following command:

```
python runner.py
```


