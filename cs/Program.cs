using Microsoft.Data.SqlClient;
using System.Text;
using Newtonsoft.Json.Linq;


#nullable disable
class Program
{
    static void Main(string[] args)
    {
        //make a dummy file
        runTests();
    }

    static void runTests()
    {
        // Path to the JSON config file
        string jsonConfigPath = Environment.GetEnvironmentVariable("CONFIG_FILE_PATH");
        JObject jsonConfig = JObject.Parse(File.ReadAllText(jsonConfigPath));

        // Update the .csproj file with the driver version
        string driverVersion = Environment.GetEnvironmentVariable("DRIVER");
        string logFilePath = Environment.GetEnvironmentVariable("LOG_FILE_PATH");

        // Iterate over endpoints
        JArray endpoints = (JArray)jsonConfig["endpoints"];
        foreach (JObject endpoint in endpoints)
        {
            string server = endpoint["server"].ToString();
            int port = (int)endpoint["port"];
            string databaseName = endpoint["database"].ToString();
            string user = endpoint["username"].ToString();
            string password = endpoint["password"].ToString();


            // Build the connection string that is used to connect to the SQL Server instance
            StringBuilder connectionStringBuilder = new StringBuilder();
            connectionStringBuilder.Append($"Server={server},{port};User Id={user};Password={password};Database={databaseName};");

            JObject config = (JObject)endpoint["options"];
            JArray useEncryption = (JArray)config["useEncryption"];
            JArray readOnly = (JArray)config["readOnly"];
            JArray trustServerCertificate = (JArray)config["trustServerCertificate"];

            if (useEncryption == null) useEncryption = new JArray(false);
            if (readOnly == null) readOnly = new JArray(false);
            if (trustServerCertificate == null) trustServerCertificate = new JArray(true);

            int errorBits = 0;

            foreach (JValue encryption in useEncryption.Values())
            {
                foreach (JValue trust in trustServerCertificate.Values())
                {
                    foreach (JValue read in readOnly.Values())
                    {

                        StringBuilder connectionStringBuilderCopy = new StringBuilder(connectionStringBuilder.ToString());
                        string applicationIntent = (bool)read.Value ? "ReadOnly" : "ReadWrite";
                        connectionStringBuilderCopy.Append($"ApplicationIntent={applicationIntent};");
                        connectionStringBuilderCopy.Append($"Encrypt={encryption.Value};");
                        connectionStringBuilderCopy.Append($"TrustServerCertificate={trust.Value};");

                        // Test the connection with the connection string
                        int error = TestConnection(connectionStringBuilderCopy, driverVersion, server, port.ToString(), databaseName, read.Value.ToString(), encryption.Value.ToString(), trust.Value.ToString(), logFilePath);
                        errorBits |= error;
                    }
                }
            }

            printResult(errorBits, driverVersion, server, port);
        }
    }

    static int TestConnection(StringBuilder connectionStringBuilder, String driverVersion, String server, String port, String database, String applicationIntent, String encryption, String trustServerCertificate, String logFilePath)
    {
        using (SqlConnection connection = new SqlConnection(connectionStringBuilder.ToString()))
        {
            try
            {
                connection.Open();

                DateTime currentTime = DateTime.Now;
                string formattedDateTime = currentTime.ToString("[yyyy-MM-dd HH:mm:ss]");

                File.AppendAllText(logFilePath, $"{formattedDateTime} Test passed for endpoint '{server}:{port}' with driver 'C# SqlClient {driverVersion}' with options: encryption={encryption}, trust_server_certificate={trustServerCertificate}, read_only={applicationIntent}.\n");
                return 0;
            }
            catch (SqlException ex)
            {
                DateTime currentTime = DateTime.Now;
                string formattedDateTime = currentTime.ToString("[yyyy-MM-dd HH:mm:ss]");

                if (ex.Number == 0 && ex.ErrorCode == -2146232060)
                {
                    Console.WriteLine(logFilePath);
                    File.AppendAllText(logFilePath, $"{formattedDateTime} C# SqlClient {driverVersion} server error: server '{server}:{port}' is not reachable with options: encryption={encryption}, trust_server_certificate={trustServerCertificate}, read_only={applicationIntent}.\n");
                    return 1;

                }
                else if (ex.Number == 4060)
                {
                    File.AppendAllText(logFilePath, $"{formattedDateTime} C# SqlClient {driverVersion} database error: Database '{database}' does not exist on server '{server}:{port}' with options: encryption={encryption}, trust_server_certificate={trustServerCertificate}, read_only={applicationIntent}.\n");
                    return 2;
                }
                else if (ex.Number == 18456)
                {
                    File.AppendAllText(logFilePath, $"{formattedDateTime} C# SqlClient {driverVersion} login error: Wrong credentials for server '{server}:{port}' with options: encryption={encryption}, trust_server_certificate={trustServerCertificate}, read_only={applicationIntent}.\n");
                    return 4;
                }
                else
                {
                    File.AppendAllText(logFilePath, $"{formattedDateTime} C# SqlClient {driverVersion} unrecognized error: {ex.Message} for server '{server}:{port}' with options: encryption={encryption}, trust_server_certificate={trustServerCertificate}, read_only={applicationIntent}.\n");
                    return 8;
                }
            }
        }
    }

    static void printResult(int errorBits, string driverVersion, string server, int port)
    {
        DateTime currentTime = DateTime.Now;
        string formattedDateTime = currentTime.ToString("[yyyy-MM-dd HH:mm:ss]");

        if (errorBits == 0)
        {
            Console.WriteLine($"{formattedDateTime} All tests passed for endpoint '{server}:{port}' with driver 'C# SqlClient {driverVersion}'");
        }
        else if (errorBits == 1)
        {
            Console.WriteLine($"{formattedDateTime} C# SqlClient {driverVersion} server error: server '{server}:{port}' is not reachable.");

        }
        else if (errorBits == 2)
        {
            Console.WriteLine($"{formattedDateTime} C# SqlClient {driverVersion} database error: Database does not exist on server '{server}:{port}'.");
        }
        else if (errorBits == 4)
        {
            Console.WriteLine($"{formattedDateTime} C# SqlClient {driverVersion} login error: Wrong credentials for server '{server}:{port}'.");
        }
        else if (errorBits == 8)
        {
            Console.WriteLine($"{formattedDateTime} C# SqlClient {driverVersion} unrecognized error: Unrecognized error for server '{server}:{port}'. Please check the log file for more details.");
        }
        else
        {
            Console.WriteLine($"{formattedDateTime} C# SqlClient {driverVersion} multiple errors: Multiple errors for server '{server}:{port}'. Please check the log file for more details.");
        }
    }
}

