import pyodbc
import os
import json
import re
import sys
import time

def pyodbc_test(server: str, port: str, database: str, username: str, password: str, encryption: str, trust_server_certificate: str, read_only: str, odbc_version: int, log_file_path: str) -> int:
    try:
        # Connection string for connecting to SQL Server using ODBC Driver
        conn_str = (
            f'DRIVER={{ODBC Driver {odbc_version} for SQL Server}};'
            f'SERVER={server};PORT={port};DATABASE={database};'
            f'UID={username};PWD={password};Encrypt={"yes" if encryption else "no"};'
            f'TrustServerCertificate={"yes" if trust_server_certificate else "no"};'
            f'ReadOnly={"yes" if read_only else "no"}'
        )

        with pyodbc.connect(conn_str) as conn:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Test passed for endpoint '{server}:{port}' with driver 'ODBC {odbc_version}' with options: encryption='{encryption}', trust_server_certificate='{trust_server_certificate}', read_only='{read_only}'.", file=open(log_file_path, 'a'))
            return 0

    # Catch specific exceptions to provide more helpful error messages
    except pyodbc.OperationalError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ODBC {odbc_version} server error: server '{server}:{port}' is not reachable with options: encryption='{encryption}', trust_server_certificate='{trust_server_certificate}', read_only='{read_only}'.", file=open(log_file_path, 'a'))
        return 1
    except pyodbc.InterfaceError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ODBC {odbc_version} login error: Wrong credentials for server '{server}:{port}' with options: encryption='{encryption}', trust_server_certificate='{trust_server_certificate}', read_only='{read_only}'.", file=open(log_file_path, 'a'))
        return 2
    except pyodbc.DatabaseError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ODBC {odbc_version} database error: Database '{database}' does not exist with options: encryption='{encryption}', trust_server_certificate='{trust_server_certificate}', read_only='{read_only}'.", file=open(log_file_path, 'a'))
        return 4
    except pyodbc.Error as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ODBC {odbc_version} unrecognized error: {e} with options: encryption='{encryption}', trust_server_certificate='{trust_server_certificate}', read_only='{read_only}'.", file=open(log_file_path, 'a'))
        return 8

def print_result(error_bits: int, odbc_version: str) -> None:
    if error_bits == 0:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] All tests passed for endpoint '{server}:{port}' with driver 'ODBC {odbc_version}'")
    elif error_bits == 1:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ODBC {odbc_version} server error: server '{server}:{port}' is not reachable.")
    elif error_bits == 2:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ODBC {odbc_version} login error: Wrong credentials for server '{server}:{port}'.")
    elif error_bits == 4:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ODBC {odbc_version} database error: Database '{database}' does not exist.")
    elif error_bits == 8:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ODBC {odbc_version} unrecognized error. Please check the log file for more details.")
    else:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ODBC {odbc_version} multiple errors. Please check the log file for more details.")

if __name__ == '__main__':
    # Open config file
    config_file_path = os.environ.get('CONFIG_FILE_PATH')
    log_file_path = os.environ.get('LOG_FILE_PATH')

    with open(config_file_path) as config_file:
        try:
            config = json.load(config_file)
        except json.JSONDecodeError as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error loading JSON config: {e}")
            sys.exit(1)

    driver = os.environ.get('DRIVER')

    # Iterate through endpoints in config file
    for endpoint in config.get('endpoints', []):
        server = endpoint.get('server')
        port = endpoint.get('port')
        database = endpoint.get('database')
        user = endpoint.get('username')
        password = endpoint.get('password')
        use_encryption = endpoint.get('options', {}).get('useEncryption', [False])
        trust_server_certificate = endpoint.get('options', {}).get('trustServerCertificate', [True])
        read_only = endpoint.get('options', {}).get('readOnly', [False])


        # Check which driver is being used
        match = re.search(r'ODBC (\d+)', driver)
        error_bits = 0
        odbc_version = match.group(1)
        for encryption in use_encryption:
            for trust in trust_server_certificate:
                for read in read_only:
                    error = pyodbc_test(server, port, database, user, password, encryption, trust, read, odbc_version, log_file_path)
                    error_bits |= error

        print_result(error_bits, odbc_version)
