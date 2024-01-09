package jdbc_11_2_3;

import java.io.FileReader;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Map;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class JDBC_11_2_3 {

    public static void main(String[] args) {
        JSONParser parser = new JSONParser();

        try {
            JSONObject config = (JSONObject) parser.parse(new FileReader(args[0])); // path to the config file

            JSONArray endpoints = (JSONArray) config.get("endpoints");

            // Iterate through each endpoint
            for (Object endpointObj : endpoints) {
                JSONObject endpoint = (JSONObject) endpointObj;
                String server = (String) endpoint.get("server");
                int port = ((Long) endpoint.get("port")).intValue();
                String databaseName = (String) endpoint.get("database");
                String user = (String) endpoint.get("username");
                String password = (String) endpoint.get("password");

                JSONObject endpointOptions = (JSONObject) endpoint.get("options");

                itterateAttributes(server, port, databaseName, user, password, endpointOptions, args[1]);

            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void itterateAttributes(String server, int port, String database, String user, String password,
            JSONObject endpointOptions, String driverVersion) {
        List<Boolean> useEncryption = new ArrayList<Boolean>() {
            {
                add(false);
            }
        };
        List<Boolean> trustServerCertificate = new ArrayList<Boolean>() {
            {
                add(false);
            }
        };
        List<Boolean> readOnly = new ArrayList<Boolean>() {
            {
                add(false);
            }
        };
        for (Object entrySet : endpointOptions.entrySet()) {
            Map.Entry<String, Object> entry = (Map.Entry<String, Object>) entrySet;
            String attributeName = entry.getKey();
            Object attributeValue = entry.getValue();

            if (attributeName.equals("useEncryption")) {
                useEncryption = (List<Boolean>) attributeValue;
            } else if (attributeName.equals("trustServerCertificate")) {
                trustServerCertificate = (List<Boolean>) attributeValue;
            } else if (attributeName.equals("readOnly")) {
                readOnly = (List<Boolean>) attributeValue;
            }
        }

        for (Boolean useEncryptionValue : useEncryption) {
            for (Boolean trustServerCertificateValue : trustServerCertificate) {
                for (Boolean readOnlyValue : readOnly) {
                    Map<String, Object> values = new HashMap<String, Object>();
                    values.put("useEncryption", useEncryptionValue.toString());
                    values.put("trustServerCertificate", trustServerCertificateValue.toString());
                    values.put("readOnly", readOnlyValue.toString());
                    String url = buildConnectionString(server, port, database, user, password, values);
                    try {
                        performDatabaseTest(url, driverVersion, server, Integer.toString(port), database);
                    } catch (SQLException e) {
                        if (e.getErrorCode() == 18456 && e.getSQLState().equals("S0001")) {
                            System.out.println("[" + printCurrentTime()
                                    + "] JDBC " + driverVersion + " login error: Wrong credentials for server: '"
                                    + server + ":" + port
                                    + "'.");
                        } else if (e.getErrorCode() == 0 && e.getSQLState().equals("08S01")) {
                            System.out.println("[" + printCurrentTime() + "] JDBC " + driverVersion
                                    + " server error: Server '" + server
                                    + ":" + port + "' is not reachable.");
                        } else if (e.getErrorCode() == 4060 && e.getSQLState().equals("S0001")) {
                            System.out.println(
                                    "[" + printCurrentTime() + "] JDBC " + driverVersion + " login error: Database '"
                                            + database + "' does not exist on server " + server + ":" + port + ".");
                        } else {
                            System.out.println(
                                    "[" + printCurrentTime() + "] JDBC " + driverVersion + " unrecognized error: "
                                            + e.getMessage());
                        }

                        return;
                    }
                }
            }
        }

        System.out.println("[" + printCurrentTime() + "] All tests passed for endpoint '" + server + ":" + port
                + "' with driver 'JDBC " + driverVersion + "'");
    }

    // Build the connection string with the current configuration
    private static String buildConnectionString(String server, int port, String databaseName, String user,
            String password, Map<String, Object> values) {
        StringBuilder urlBuilder = new StringBuilder(
                String.format("jdbc:sqlserver://%s:%d;databaseName=%s;", server, port, databaseName));

        for (Map.Entry<String, Object> entry : values.entrySet()) {
            String attributeName = entry.getKey();
            Object attributeValue = entry.getValue();
            urlBuilder.append(attributeName).append("=").append(attributeValue).append(";");
        }

        return urlBuilder.append("user=").append(user).append(";password=").append(password).toString();
    }

    private static void performDatabaseTest(String url, String driverVersion, String server, String port,
            String database) throws SQLException {
        String sqlQuery = "SELECT * FROM employees";

        try {
            // Load the JDBC driver
            Class.forName("com.microsoft.sqlserver.jdbc.SQLServerDriver");
            // Establish the connection
            try (Connection connection = DriverManager.getConnection(url)) {
                // Create a PreparedStatement for the SQL query
                try (PreparedStatement preparedStatement = connection.prepareStatement(sqlQuery)) {
                    // Execute the query and retrieve the result set
                    try (ResultSet resultSet = preparedStatement.executeQuery()) {
                        // Iterate through the result set and print the values
                    }
                }
            }
        } catch (SQLException se) {
            throw se;
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static String printCurrentTime() {
        LocalDateTime now = LocalDateTime.now();

        String pattern = "yyyy-MM-dd HH:mm:ss";

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern(pattern);

        String formattedDateTime = now.format(formatter);

        return formattedDateTime;
    }
}
