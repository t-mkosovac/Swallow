const sql = require('mssql');
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

async function iterateConfigurations(options, endpoint) {
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

        try {
          await testMssqlConnection(connection_params);
        } catch (err) {
          return;
        }
      }
    }
  }
  console.log(`[${getFormattedDate()}] All tests passed for endpoint '${endpoint.server}:${endpoint.port}' with driver 'JSMSSQL'`);
}

async function runTests(config) {
  try {
    // Read the JSON file
    const data = await fs.promises.readFile(config, 'utf8');

    // Parse JSON data
    const json_data = JSON.parse(data);

    // Iterate over endpoints
    for (const endpoint of json_data.endpoints) {
      await iterateConfigurations(endpoint.options, endpoint);
    }
  } catch (err) {
    // Handle errors
    console.error('Error reading the file or running tests:', err);
  } finally {
    // Close the SQL connection pool after all tests
    await sql.close();
  }
}

config_file_path = process.env.CONFIG_FILE_PATH;
runTests(config_file_path);

