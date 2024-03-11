import pyodbc
import os
import pymssql
import json
import re
import sys
import time

def pyodbc_test(server: str, port: str, database: str, username: str, password: str, encryption: str, trust_server_certificate: str, read_only: str, odbc_version: int) -> None:
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
            pass

    # Catch specific exceptions to provide more helpful error messages
    except pyodbc.OperationalError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] PYODBC operational error: server '{server}:{port}' is not reachable.")
        raise e
    except pyodbc.InterfaceError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] PYODBC interface error: Wrong credentials for server '{server}:{port}'.")
        raise e
    except pyodbc.DatabaseError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] PYODBC database error: Database '{database}' does not exist.")
        raise e
    except pyodbc.Error as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] PYODBC unrecognized error: {e}")
        raise e

def pymssql_test(server: str, port: str, database: str, username: str, password: str) -> None:
    try:
        # Conneccting to SQL Server using pymssql that does not support encryption, trust server certificate, and read only attributes
        with pymssql.connect(server, username, password, database, port) as conn:
            pass
        
    # Catch specific exceptions to provide more helpful error messages
    except pymssql.DatabaseError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] PYMSSQL database error: Wrong credentials for server '{server}:{port}' or database '{database}' does not exist.")
        raise e
    except pymssql.OperationalError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] PYMSSQL operational error: server '{server}:{port}' is not reachable.")
        raise e
    except pymssql.Error as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] PYMSSQL unrecognized error: {e}")
        raise e

if __name__ == '__main__':
    # Open config file
    config_file_path = os.environ.get('CONFIG_FILE_PATH')
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

        match = re.match(r'py_odbc_(.+)', driver)
        try:
            # Check which driver is being used
            if match:
                odbc_version = match.group(1)
                for encryption in use_encryption:
                    for trust in trust_server_certificate:
                        for read in read_only:
                            pyodbc_test(server, port, database, user, password, encryption, trust, read, odbc_version)
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] All tests passed for endpoint '{server}:{port}' with driver 'PyODBC {odbc_version}'")
            elif driver == 'py_mssql':
                pymssql_test(server, port, database, user, password)
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] All tests passed for endpoint '{server}:{port}' with driver 'PyMSSQL'")
        except Exception as e:
            continue
