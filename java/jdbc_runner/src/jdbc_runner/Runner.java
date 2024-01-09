package jdbc_runner;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;

public class Runner {
	public static void main(String[] args) {
		try {
			// Depending on the driver version, set the workspace, driver folder and
			// classpath
			String version = args[1]; // driver version
			String workspace = "", driverFolder = "", classpath = "";
			switch ((String) version) {
				case "10.2.3":
					workspace += "jdbc_10_2_3";
					driverFolder += "sqljdbc_10.2.3.0_enu\\sqljdbc_10.2enu\\mssql-jdbc-10.2.3.jre8.jar";
					classpath += "jdbc_10_2_3.JDBC_10_2_3";
					break;

				case "11.2.3":
					workspace += "jdbc_11_2_3";
					driverFolder += "sqljdbc_11.2.3.0_enu\\sqljdbc_11.2enu\\mssql-jdbc-11.2.3.jre18.jar";
					classpath += "jdbc_11_2_3.JDBC_11_2_3";
					break;

				case "12.4.2":
					workspace += "jdbc_12_4_2";
					driverFolder += "sqljdbc_12.4.2.0_enu\\sqljdbc_12.4\\enu\\jars\\mssql-jdbc-12.4.2.jre11.jar";
					classpath += "jdbc_12_4_2.JDBC_12_4_2";
					break;

				default:
					throw new Exception("Driver version " + version + " not supported");
			}

			// Create the process builder
			ProcessBuilder processBuilder = new ProcessBuilder(
					"java",
					"-cp", "H:\\sql-driver-apps\\java\\" + workspace + "\\bin;"
							+ "C:\\Users\\t-mkosovac\\Downloads\\json-simple-1.1.jar;"
							+ "C:\\Users\\t-mkosovac\\Downloads\\" + driverFolder,
					classpath, args[0], version);

			processBuilder.redirectErrorStream(true);

			// Start the process
			Process process = processBuilder.start();

			// Read the output from the process
			InputStream inputStream = process.getInputStream();
			BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
			String line;
			while ((line = reader.readLine()) != null) {
				System.out.println(line);
			}

			// Wait for the process to finish
			int exitCode = process.waitFor();

		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
