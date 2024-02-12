const sql = require('mssql');
const odbc = require('odbc');
const fs = require('fs');

function getFormattedDate() {
  const currentDate = new Date();
  const year = currentDate.getFullYear();
  const month = String(currentDate.getMonth() + 1).padStart(2, '0');
  const day = String(currentDate.getDate()).padStart(2, '0');
  const hours = String(currentDate.getHours()).padStart(2, '0');
  const minutes = String(currentDate.getMinutes()).padStart(2, '0');
  const seconds = String(currentDate.getSeconds()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

async function testMssqlConnection(config) {
  try {
    await sql.connect(config);
  } catch (err) {
    // Handle errors
    if (err.code === 'ETIMEOUT') {
      console.error(`[${getFormattedDate()}] JSMSSQL timeout error: Server ${config.server}:${config.port} is not reachable`);
    } else if (err.code === 'ELOGIN') {
      console.error(`[${getFormattedDate()}] JSMSSQL login error: Wrong credentials for server ${config.server}:${config.port} or database ${config.database} does not exist`);
    } else {
      console.error(`[${getFormattedDate()}] JSMSSQL unrecognized error: ${err.message}`);
    }
    throw err;
  } finally {
    // Close the SQL connection
    await sql.close();
  }
}

async function testOdbcConnection(config, driver) {
  let connection;
  try {
    const config_string = `DRIVER={ODBC Driver ${driver} for SQL Server};SERVER=${config.server};DATABASE=${config.database};UID=${config.user};PWD=${config.password};PORT=${config.port};Encrypt=${config.encrypt ? 'Yes' : 'No'};TrustServerCertificate=${config.trustServerCertificate ? 'Yes' : 'No'};ReadOnly=${config.readOnlyIntent ? 'Yes' : 'No'}`;
  // Now use the config_string in your connection logic...
    const connect = {
      connectionString: config_string,
    }
    await odbc.connect(connect);
  } catch (err) {
    // Handle errors
    if (err.odbcErrors.some(item => item.state == 'HYT00')) {
      console.error(`[${getFormattedDate()}] JSODBC timeout error: Server '${config.server}:${config.port}' is not reachable`);
    } else if (err.odbcErrors.some(item => item.state == '42000')) {
      console.error(`[${getFormattedDate()}] JSODBC database error: Database '${config.database}' does not exist`);
    } else if (err.odbcErrors.some(item => item.state == '28000') && err.odbcErrors.some(item => item.state == '01S00')) {
      console.error(`[${getFormattedDate()}] JSODBC login error: Wrong credentials for server '${config.server}:${config.port}'`);
    } else {
      console.error(`[${getFormattedDate()}] JSODBC unrecognized error: ${err.odbcErrors}`);
    }
    throw err;
  } finally {
    // Close the ODBC connection
    if (connection)
      await connection.close();
  }
}

async function iterateConfigurations(options, endpoint, driver) {
  // Option fields are optional, so we need to check if they exist
  let { useEncryption, trustServerCertificate, readOnly } = options;
  if (!useEncryption) {
    useEncryption = [false];
  }
  if (!trustServerCertificate) {
    trustServerCertificate = [false];
  }
  if (!readOnly) {
    readOnly = [false];
  }

  // Iterate over all possible combinations of options
  for (const encryption of useEncryption) {
    for (const trust of trustServerCertificate) {
      for (const read of readOnly) {

        const connection_params = {
          user: endpoint.username,
          password: endpoint.password,
          server: endpoint.server,
          database: endpoint.database,
          port: endpoint.port,
          encrypt: encryption,
          trustServerCertificate: trust,
          readOnlyIntent: read,
        };

        // Check if the driver is ODBC or MSSQL
        const driverPattern = /^js_odbc_(.+)$/;
        const match = driver.match(driverPattern);

        try {
          if (match) {
            const odbcVersion = match[1];
            await testOdbcConnection(connection_params, odbcVersion);
          } else if (driver === 'js_mssql') {
            await testMssqlConnection(connection_params);
          }
        } catch (err) {
          return;
        }
      }
    }
  }
  console.log(`[${getFormattedDate()}] All tests passed for endpoint '${endpoint.server}:${endpoint.port}' with driver '${driver}'`);
}

async function runTests(config, driver) {
  try {
    // Read the JSON file
    const data = await fs.promises.readFile(config, 'utf8');

    // Parse JSON data
    const json_data = JSON.parse(data);

    // Iterate over endpoints
    for (const endpoint of json_data.endpoints) {
      await iterateConfigurations(endpoint.options, endpoint, driver);
    }
  } catch (err) {
    // Handle errors
    console.error('Error reading the file or running tests:', err);
  } finally {
    // Close the SQL connection pool after all tests
    await sql.close();
  }
}

runTests("../config.json", "js_mssql");

