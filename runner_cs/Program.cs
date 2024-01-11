using System;
using System.Diagnostics;
using System.IO;

class Program
{
    static string GetAbsolutePath(string relativePath)
    {
        string currentDir = Environment.CurrentDirectory;
        return Path.Combine(currentDir, relativePath);
    }

    static void RunScript(string scriptPath, params string[] args)
    {
        string batchScriptPath = GetAbsolutePath(scriptPath);

        ProcessStartInfo startInfo = new ProcessStartInfo
        {
            FileName = batchScriptPath,
            UseShellExecute = true,
            Arguments = string.Join(" ", args)
        };

        using (Process process = new Process { StartInfo = startInfo })
        {
            process.Start();
            process.WaitForExit();
        }
    }

    static void Main()
    {
        // Example usage:
        string scriptPath = "scripts\\cs_run.bat";
        string arg1 = "config\\sql_tests_config.json";
        arg1 = GetAbsolutePath(arg1);
        Console.WriteLine(arg1);
        string arg2 = "5.0.0";

        RunScript(scriptPath, arg1, arg2);
    }
}