using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Reflection;

namespace NeX_Launcher.Deployment
{
    public static class FileLogger
    {
        private const string LogPath = @"C:\NeX_Storage\System\Crash_Log.txt";

        public static void Log(string message)
        {
            try
            {
                string directory = Path.GetDirectoryName(LogPath);
                if (!Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                string logEntry = $"[{DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC] {message}\n";
                File.AppendAllText(LogPath, logEntry);
            }
            catch
            {
                // Last resort fallback
                Debug.WriteLine($"[Logger Error] Failed to write to log.");
            }
        }

        public static void LogError(Exception ex, string context = "")
        {
            try
            {
                string directory = Path.GetDirectoryName(LogPath);
                if (!Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                string contextStr = string.IsNullOrEmpty(context) ? "" : $"[{context}] ";
                string logEntry = $"[{DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC] ERROR: {contextStr}{ex.Message}\nStackTrace:\n{ex.StackTrace}\n";
                if (ex.InnerException != null)
                {
                    logEntry += $"Inner Exception: {ex.InnerException.Message}\n";
                }
                File.AppendAllText(LogPath, logEntry);
            }
            catch
            {
                Debug.WriteLine($"[Logger Error] Failed to write exception to log.");
            }
        }
    }

    public class KioskDeployer
    {
        public async Task<(string Output, string Error)> EnableCustomShellAsync(string scriptPath)
        {
            if (string.IsNullOrWhiteSpace(scriptPath))
                throw new ArgumentException("Script path cannot be null or empty.", nameof(scriptPath));

            FileLogger.Log($"Executing script to Enable Custom Shell/Clear AppLocker: {scriptPath}");
            string arguments = $"-ExecutionPolicy Bypass -NoProfile -NonInteractive -File \"{scriptPath}\"";
            return await ExecuteProcessAsync("powershell.exe", arguments);
        }

        public async Task<(string Output, string Error)> ApplyLGPORestrictionsAsync(string lgpoExePath, string appLockerXmlPath)
        {
            if (string.IsNullOrWhiteSpace(lgpoExePath))
                throw new ArgumentException("LGPO executable path cannot be null or empty.", nameof(lgpoExePath));
            if (string.IsNullOrWhiteSpace(appLockerXmlPath))
                throw new ArgumentException("Policy file path cannot be null or empty.", nameof(appLockerXmlPath));

            FileLogger.Log($"Initiating AppLocker Policy Application using {appLockerXmlPath}");

            // 1. DYNAMIC XML PATCHING (Self-Whitelisting)
            try
            {
                if (File.Exists(appLockerXmlPath))
                {
                    // We must use Process.GetCurrentProcess().MainModule.FileName for single-file executables
                    // because Assembly.GetExecutingAssembly().Location returns an empty string.
                    string currentExePath = Process.GetCurrentProcess().MainModule?.FileName;

                    if (!string.IsNullOrEmpty(currentExePath))
                    {
                        FileLogger.Log($"Dynamic Assembly Path Detected: {currentExePath}");
                        
                        string xmlContent = File.ReadAllText(appLockerXmlPath);
                        string placeholderPath = @"C:\NeX_Launcher\NeX_Launcher.exe"; // The hardcoded path in your template
                        
                        if (xmlContent.Contains(placeholderPath, StringComparison.OrdinalIgnoreCase))
                        {
                            xmlContent = xmlContent.Replace(placeholderPath, currentExePath, StringComparison.OrdinalIgnoreCase);
                            File.WriteAllText(appLockerXmlPath, xmlContent);
                            FileLogger.Log($"CRITICAL: Self-Whitelisting successful! Patched AppLocker XML to allow {currentExePath}");
                        }
                        else
                        {
                            FileLogger.Log("Notice: Hardcoded placeholder path not found in XML. Dynamic patching skipped. Ensure the XML contains the placeholder path if self-whitelisting is required.");
                        }
                    }
                }
                else
                {
                    FileLogger.Log($"Warning: AppLocker XML not found at {appLockerXmlPath}. Cannot perform dynamic patching.");
                }
            }
            catch (Exception ex)
            {
                FileLogger.LogError(ex, "Dynamic AppLocker XML Patching");
            }

            // 2. APPLY THE POLICIES
            string arguments = $"/g \"{appLockerXmlPath}\""; 
            return await ExecuteProcessAsync(lgpoExePath, arguments);
        }

        private async Task<(string Output, string Error)> ExecuteProcessAsync(string fileName, string arguments)
        {
            var outputBuilder = new StringBuilder();
            var errorBuilder = new StringBuilder();

            using var process = new Process();
            
            process.StartInfo = new ProcessStartInfo
            {
                FileName = fileName,
                Arguments = arguments,
                CreateNoWindow = true,         
                UseShellExecute = false,       
                RedirectStandardOutput = true, 
                RedirectStandardError = true   
            };

            process.OutputDataReceived += (sender, e) =>
            {
                if (e.Data != null) outputBuilder.AppendLine(e.Data);
            };

            process.ErrorDataReceived += (sender, e) =>
            {
                if (e.Data != null) errorBuilder.AppendLine(e.Data);
            };

            try
            {
                FileLogger.Log($"System Execution: {fileName} {arguments}");
                process.Start();
                process.BeginOutputReadLine();
                process.BeginErrorReadLine();
                await process.WaitForExitAsync();
                
                string error = errorBuilder.ToString();
                if (!string.IsNullOrWhiteSpace(error))
                {
                    FileLogger.Log($"[Execution Error] {fileName}: {error}");
                }
                else
                {
                    FileLogger.Log($"Execution of {fileName} completed successfully.");
                }
                
                return (outputBuilder.ToString(), errorBuilder.ToString());
            }
            catch (Exception ex)
            {
                string msg = $"Process execution encountered an exception: {ex.Message}";
                errorBuilder.AppendLine(msg);
                FileLogger.LogError(ex, "Fatal Execution Error");
                return (outputBuilder.ToString(), errorBuilder.ToString());
            }
        }
    }
}
