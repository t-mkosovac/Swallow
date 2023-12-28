@echo off

REM Navigate to the directory where the C# program is located
cd /d "%~dp0..\..\python"

REM Run the C# program using dotnet
python sql-test.py %1 %2
