import subprocess
import os
import sys
import json
import re
import schedule
import time
from sql_drivers import cs_drivers, py_drivers, js_drivers, java_drivers

scripts = {
    'cs': 'scripts\\cs_run.bat',
    'py': 'scripts\\py_run.bat',
    'js': 'scripts\\js_run.bat',
    'java': 'scripts\\java_run.bat'
}

def get_absolute_path(relative_path: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(current_dir, relative_path)

def run_script(script_path: str, *args) -> None:
    batch_script_path = get_absolute_path(script_path)

    subprocess.run([batch_script_path] + list(args), shell=True)

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

def run_tests(config_file: str) -> None:
    with open(config_file) as f:
        data = json.load(f)

    # Iterate through list of drivers in config file
    for driver in data['drivers']:
        if driver in cs_drivers:
            run_script(scripts['cs'], config_file, re.sub(r'cs_', '', driver))
        elif driver in py_drivers:
            run_script(scripts['py'], config_file, driver)
        elif driver in js_drivers:
            run_script(scripts['js'], config_file, driver)
        elif driver in java_drivers:
            run_script(scripts['java'], config_file, re.sub(r'jdbc_', '', driver))
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Driver '{driver}' is not supported. Please check sql_drivers.py for a list of supported drivers.")
    print('-------------------------------------------------------------------------------------------')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Please provide a config file as an argument")
        exit(1)

    # Get absolute path to config file
    config_file = get_absolute_path('config\\' + sys.argv[1])

    # Check if config file exists
    if not os.path.exists(config_file):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Config file does not exist")
        exit(1)

    # check if config file is in correct format
    validate_json(config_file)

    # Read retry period from config file (if exists)
    retry_period = read_retry_period(config_file)

    if retry_period > 0:
        # Setup schedule to run tests every retry_period minutes
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running tests with retry period of " + str(retry_period) + " minute" + ("s" if retry_period > 1 else "") + "")
        print('-------------------------------------------------------------------------------------------')
        schedule.every(retry_period).minutes.do(run_tests, config_file)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        # If retry period is does not exist, run tests once
        print('-------------------------------------------------------------------------------------------')
        run_tests(config_file)
