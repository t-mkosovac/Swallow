@echo off

REM Navigate to the directory where the C# program is located
cd /d "%~dp0..\..\java\jdbc_runner\src\jdbc_runner"

REM Run the C# program using dotnet
javac -cp "C:\Users\t-mkosovac\Downloads\json-simple-1.1.jar" Runner.java
java -cp "H:\sql-driver-apps\java\jdbc_runner\bin;C:\Users\t-mkosovac\Downloads\json-simple-1.1.jar" jdbc_runner.Runner %1 %2

