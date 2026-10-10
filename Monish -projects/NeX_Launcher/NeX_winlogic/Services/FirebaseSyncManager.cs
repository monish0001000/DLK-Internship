using System;
using System.Net.Http;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace NexLauncher.Services
{
    public class FirebaseSyncManager
    {
        private readonly string _databaseUrl;
        private readonly HttpClient _httpClient;
        private CancellationTokenSource? _cts;

        // Event — MainWindow subscribe பண்ணும்
        public event Action<string>? OnActiveModeChanged;
        public event Action<string>? OnRemoteInstallRequested;
        public event Action<string>? OnRemoteCommandReceived;
        public event Action<string>? OnInstalledAppsUpdated;

        public bool IsListenerActive { get; private set; }

        public FirebaseSyncManager(string databaseUrl)
        {
            _databaseUrl = databaseUrl.TrimEnd('/');
            _httpClient = new HttpClient();
        }

        public void StartActiveModeListener()
        {
            _cts = new CancellationTokenSource();
            IsListenerActive = true;
            Task.Run(() => PollFirebaseNodes(_cts.Token));
            Console.WriteLine("[+] Firebase Listeners started");
        }

        private async Task PollFirebaseNodes(CancellationToken token)
        {
            string? lastMode = null;
            string? lastUrl = null;
            string? lastApps = null;

            while (!token.IsCancellationRequested)
            {
                try
                {
                    // 1. Check Active Mode
                    var modeUrl = $"{_databaseUrl}/Kiosks/LAPTOP_01/active_mode.json";
                    var modeResponse = await _httpClient.GetStringAsync(modeUrl, token);
                    var mode = modeResponse.Trim('"');

                    if (mode != lastMode && mode != "null")
                    {
                        lastMode = mode;
                        Console.WriteLine($"[Firebase] Mode changed: {mode}");
                        OnActiveModeChanged?.Invoke(mode);
                    }

                    // 2. Check Remote Install URL
                    var installUrl = $"{_databaseUrl}/Kiosks/LAPTOP_01/Commands/DownloadUrl.json";
                    var installResponse = await _httpClient.GetStringAsync(installUrl, token);
                    var url = installResponse.Trim('"');

                    if (url != lastUrl && url != "null")
                    {
                        lastUrl = url;
                        Console.WriteLine($"[Firebase] Remote Install URL received: {url}");
                        OnRemoteInstallRequested?.Invoke(url);
                    }

                    // 3. Check Remote Commands
                    var cmdUrl = $"{_databaseUrl}/Kiosks/LAPTOP_01/Commands.json";
                    try 
                    {
                        var cmdResponse = await _httpClient.GetStringAsync(cmdUrl, token);
                        if (cmdResponse != "null" && !string.IsNullOrWhiteSpace(cmdResponse))
                        {
                            Console.WriteLine($"[Firebase] Command received: {cmdResponse}");
                            OnRemoteCommandReceived?.Invoke(cmdResponse);
                            
                            // Delete command to prevent replay loop
                            await _httpClient.DeleteAsync(cmdUrl, token);
                        }
                    }
                    catch (Exception) { /* Node might not exist, ignore */ }

                    // 4. Check InstalledApps for Disable/Block
                    var appsUrl = $"{_databaseUrl}/Kiosks/LAPTOP_01/InstalledApps.json";
                    try 
                    {
                        var appsResponse = await _httpClient.GetStringAsync(appsUrl, token);
                        if (appsResponse != "null" && appsResponse != lastApps)
                        {
                            lastApps = appsResponse;
                            OnInstalledAppsUpdated?.Invoke(appsResponse);
                        }
                    }
                    catch (Exception) { /* Node might not exist, ignore */ }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[Firebase] Poll error: {ex.Message}");
                    if (lastMode == null)
                    {
                        lastMode = "default";
                        OnActiveModeChanged?.Invoke(lastMode);
                    }
                }

                await Task.Delay(3000, token); // 3 seconds polling
            }
        }

        public void StartHeartbeat()
        {
            Task.Run(async () =>
            {
                while (true)
                {
                    try
                    {
                        if (System.Net.NetworkInformation.NetworkInterface.GetIsNetworkAvailable())
                        {
                            var url = $"{_databaseUrl}/Kiosks/LAPTOP_01/last_heartbeat.json";
                            var payload = $"\"{DateTime.UtcNow:o}\"";
                            var content = new StringContent(payload, System.Text.Encoding.UTF8, "application/json");
                            await _httpClient.PutAsync(url, content);
                            Console.WriteLine("[Firebase] Heartbeat sent");
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"[Firebase] Heartbeat error: {ex.Message}");
                    }
                    await Task.Delay(5000); // 5 seconds
                }
            });
        }

        public void Stop()
        {
            _cts?.Cancel();
            IsListenerActive = false;
            _httpClient.Dispose();
        }
    }
}