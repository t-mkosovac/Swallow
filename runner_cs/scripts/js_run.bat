@echo off

REM Navigate to the directory where the C# program is located
cd /d "%~dp0..\..\js"

REM Run the C# program using dotnet
node --no-deprecation sql-test.js %1 %2

