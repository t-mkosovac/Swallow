@echo off

REM Navigate to the directory where the C# program is located
cd /d "%~dp0..\..\c#"

REM Run the C# program using dotnet
dotnet run %1 %2

