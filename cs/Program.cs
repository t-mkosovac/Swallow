using Microsoft.Data.SqlClient;
using System.Text;
using Newtonsoft.Json.Linq;


#nullable disable
class Program
{
    static void Main(string[] args)
    {
        runTests();
    }

    static void runTests()
    {
        // Path to the JSON config file
        string jsonConfigPath = Environment.GetEnvironmentVariable("CONFIG_FILE_PATH");
        JObject jsonConfig = JObject.Parse(File.ReadAllText(jsonConfigPath));

        // Update the .csproj file with the driver version
        string driverVersion = Environment.GetEnvironmentVariable("DRIVER");

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
            if (trustServerCertificate == null) trustServerCertificate = new JArray(false);

            try
            {
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
                            TestConnection(connectionStringBuilderCopy, driverVersion, server, port.ToString(), databaseName);
                        }
                    }
                }

                DateTime currentTime = DateTime.Now;
                string formattedDateTime = currentTime.ToString("[yyyy-MM-dd HH:mm:ss]");

                Console.WriteLine($"{formattedDateTime} All tests passed for endpoint '{server}:{port}' with driver 'C# SqlClient {driverVersion}'");
            }
            catch (SqlException)
            {
                break;
            }
        }
    }

    static void TestConnection(StringBuilder connectionStringBuilder, String driverVersion, String server, String port, String database)
    {
        using (SqlConnection connection = new SqlConnection(connectionStringBuilder.ToString()))
        {
            try
            {
                connection.Open();
            }
            catch (SqlException ex)
            {
                DateTime currentTime = DateTime.Now;
                string formattedDateTime = currentTime.ToString("[yyyy-MM-dd HH:mm:ss]");

                if (ex.Number == 0 && ex.ErrorCode == -2146232060)
                    Console.WriteLine($"{formattedDateTime} C# SqlClient {driverVersion} server error: server '{server}:{port}' is not reachable.");
                else if (ex.Number == 4060)
                {
                    Console.WriteLine($"{formattedDateTime} C# SqlClient {driverVersion} database error: Database '{database}' does not exist on server '{server}:{port}'.");
                }
                else if (ex.Number == 18456)
                {
                    Console.WriteLine($"{formattedDateTime} C# SqlClient {driverVersion} login error: Wrong credentials for server '{server}:{port}'.");
                }
                else
                {
                    Console.WriteLine($"{formattedDateTime} C# SqlClient {driverVersion} unrecognized error: {ex.Message} for server '{server}:{port}' ex.Number: {ex.Number} ex.ErrorCode: {ex.ErrorCode} ex.State: {ex.State} ex.LineNumber: {ex.LineNumber} ex.Procedure: {ex.Procedure} ex.Server: {ex.Server} ex.Source: {ex.Source} ex.TargetSite: {ex.TargetSite} ex.InnerException: {ex.InnerException} ex.StackTrace: {ex.StackTrace} ex.HelpLink: {ex.HelpLink} ex.Data: {ex.Data} ex.HResult: {ex.HResult} ex.GetType: {ex.GetType()} ex.GetType().Name: {ex.GetType().Name} ex.GetType().FullName: {ex.GetType().FullName} ex.GetType().AssemblyQualifiedName: {ex.GetType().AssemblyQualifiedName} ex.GetType().BaseType: {ex.GetType().BaseType} ex.GetType().GUID: {ex.GetType().GUID} ex.GetType().IsCOMObject: {ex.GetType().IsCOMObject} ex.GetType().IsInterface: {ex.GetType().IsInterface} ex.GetType().IsArray: {ex.GetType().IsArray} ex.GetType().IsByRef: {ex.GetType().IsByRef} ex.GetType().IsPointer: {ex.GetType().IsPointer} ex.GetType().IsPrimitive: {ex.GetType().IsPrimitive} ex.GetType().IsValueType: {ex.GetType().IsValueType} ex.GetType().IsEnum: {ex.GetType().IsEnum} ex.GetType().IsGenericType: {ex.GetType().IsGenericType} ex.GetType().IsGenericTypeDefinition: {ex.GetType().IsGenericTypeDefinition} ex.GetType().IsConstructedGenericType: {ex.GetType().IsConstructedGenericType} ex.GetType().IsGenericParameter: {ex.GetType().IsGenericParameter} ex.GetType().IsSecurityCritical: {ex.GetType().IsSecurityCritical} ex.GetType().IsSecuritySafeCritical: {ex.GetType().IsSecuritySafeCritical} ex.GetType().IsSecurityTransparent: {ex.GetType().IsSecurityTransparent} ex.GetType().IsVisible: {ex.GetType().IsVisible} ex.GetType().IsNotPublic: {ex.GetType().IsNotPublic} ex.GetType().IsPublic: {ex.GetType().IsPublic} ex.GetType().IsNestedPublic: {ex.GetType().IsNestedPublic} ex.GetType().IsNestedPrivate: {ex.GetType().IsNestedPrivate} ex.GetType().IsNestedFamily: {ex.GetType().IsNestedFamily} ex.GetType().IsNestedAssembly: {ex.GetType().IsNestedAssembly} ex.GetType().IsNestedFamANDAssem: {ex.GetType().IsNestedFamANDAssem} ex.GetType().Is");
                }
                throw;
            }
        }
    }
}

