import subprocess
import os
import json
import re
import schedule
import time
import xml.etree.ElementTree as ET
from dotenv import dotenv_values
from available_drivers import cs_drivers, py_drivers, js_drivers, java_drivers

def get_absolute_path(relative_path: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(current_dir, relative_path)

def validate_json(config_file: str) -> None:
    with open(config_file) as f:
        data = json.load(f)

    if 'drivers' not in data:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file is not in correct format, 'drivers' key is missing.")
        exit(1)
    if not isinstance(data['drivers'], list):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file is not in correct format, 'drivers' key is not a list.")
        exit(1)
    if len(data['drivers']) == 0:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file is not in correct format, 'drivers' list is empty.")
        exit(1)
    if 'endpoints' not in data:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file is not in correct format, 'endpoints' key is missing.")
        exit(1)
    if not isinstance(data['endpoints'], list):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file is not in correct format, 'endpoints' key is not a list.")
        exit(1)
    if len(data['endpoints']) == 0:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file is not in correct format, 'endpoints' list is empty.")
        exit(1)

    for endpoint in data['endpoints']:
        if 'server' not in endpoint:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file is not in correct format, 'server' key is missing in endpoint.")
            exit(1)
        if 'port' not in endpoint:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file is not in correct format, 'port' key is missing in endpoint.")
            exit(1)
        if 'database' not in endpoint:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file is not in correct format, 'database' key is missing in endpoint.")
            exit(1)
        if 'username' not in endpoint:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file is not in correct format, 'username' key is missing in endpoint.")
            exit(1)
        if 'password' not in endpoint:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file is not in correct format, 'password' key is missing in endpoint.")
            exit(1)
        if 'options' not in endpoint:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file is not in correct format, 'options' key is missing in endpoint.")
            exit(1)
        if not isinstance(endpoint['options'], dict):
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file is not in correct format, 'options' key is not a dictionary.")
            exit(1)

def read_retry_period(config_file: str) -> int:
    with open(config_file) as f:
        data = json.load(f)

    return data.get('retryPeriod', 0)

def update_cs_driver_version(xml_path: str, new_version: str) -> None:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    package_ref = root.find("./ItemGroup/PackageReference[@Include='Microsoft.Data.SqlClient']")

    if package_ref is not None:
        package_ref.set('Version', new_version)
        tree.write(xml_path)

def run_tests(config_file: str) -> None:
    with open(config_file) as f:
        data = json.load(f)

    docker_config_file_path = dotenv_values('.env').get('DOCKER_CONFIG_FILE_PATH')

    # Iterate through list of drivers in config file
    for driver in data['drivers']:
        if driver in cs_drivers:
            cs_driver = re.sub(r'cs_', '', driver)
            update_cs_driver_version(get_absolute_path('cs/cs.csproj'), cs_driver)
            subprocess.run(['docker-compose', 'build', 'cs'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['docker-compose', 'run', '-e', 'DRIVER=' + cs_driver, '-e', 'CONFIG_FILE_PATH=' + docker_config_file_path, 'cs'])
        elif driver in py_drivers:
            subprocess.run(['docker-compose', 'run', '-e', 'DRIVER=' + driver, '-e', 'CONFIG_FILE_PATH=' + docker_config_file_path, 'py'])
        elif driver in js_drivers:
            subprocess.run(['docker-compose', 'run', '-e', 'DRIVER=' + driver, '-e','CONFIG_FILE_PATH=' + docker_config_file_path, 'js'])
        elif driver in java_drivers:
            subprocess.run(['docker-compose', 'run', '-e', 'CONFIG_FILE_PATH=' + docker_config_file_path, 'java' + int(re.search(r'\d+', driver).group()).__str__()])
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Driver '{driver}' is not supported. Please check available_drivers.py for a list of supported drivers.")
    print('-------------------------------------------------------------------------------------------')

if __name__ == "__main__":

    # Get absolute path to config file
    config_file = dotenv_values('.env').get('CONFIG_FILE_PATH')
    config_file_path = get_absolute_path(config_file)

    # Check if config file exists
    if not os.path.exists(config_file_path):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file does not exist")
        exit(1)

    # check if config file is in correct format
    validate_json(config_file_path)

    # Read retry period from config file (if exists)
    retry_period = read_retry_period(config_file_path)

    if retry_period > 0:
        # Setup schedule to run tests every retry_period minutes
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running tests with retry period of " + str(retry_period) + " minute" + ("s" if retry_period > 1 else "") + "")
        print('-------------------------------------------------------------------------------------------')
        run_tests(config_file_path)
        schedule.every(retry_period).minutes.do(run_tests, config_file_path)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        # If retry period is does not exist, run tests once
        print('-------------------------------------------------------------------------------------------')
        run_tests(config_file_path)
