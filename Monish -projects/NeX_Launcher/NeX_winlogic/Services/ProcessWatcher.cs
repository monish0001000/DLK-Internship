using System;
using System.Diagnostics;
using System.Threading;
using System.Collections.Generic;

namespace NexLauncher.Services
{
    public class ProcessWatcher
    {
        private readonly string[] _blacklist = {
            // "taskmgr", "cmd", "powershell", "regedit", "powershell_ise"
        };

        private readonly Dictionary<string, List<string>> _whitelists = new()
        {
            ["mode1"] = new List<string> {
                "msedge", "chrome", "win32calc", "calculator",
                "windowscamera", "systemsettings", "applicationframehost"
            }
        };

        private string _currentMode = "mode1";
        private Thread? _thread;
        private bool _running = false;

        public void SetMode(string mode)
        {
            _currentMode = mode.ToLower().Trim();
            Console.WriteLine($"[*] ProcessWatcher mode: {_currentMode}");
        }

        public void Start()
        {
            _running = true;
            _thread = new Thread(WatchLoop) { IsBackground = true };
            _thread.Start();
            Console.WriteLine("[+] Process Watcher Active");
        }

        public void Stop() => _running = false;

        private void WatchLoop()
        {
            while (_running)
            {
                foreach (var name in _blacklist)
                    foreach (var p in Process.GetProcessesByName(name))
                        try { p.Kill(); Console.WriteLine($"[-] KILLED: {name}"); } catch { }

                // Whitelist enforcement — enable after Monish integration approval
                /*
                if (_whitelists.TryGetValue(_currentMode, out var allowed))
                {
                    foreach (var proc in Process.GetProcesses())
                    {
                        try
                        {
                            if (proc.Id <= 4) continue;
                            string pname = proc.ProcessName.ToLower();
                            if (IsSystemProcess(pname)) continue;
                            if (pname == "nexlauncher") continue;
                            if (!allowed.Contains(pname)) proc.Kill();
                        }
                        catch { }
                    }
                }
                */

                Thread.Sleep(200);
            }
        }

        private bool IsSystemProcess(string name)
        {
            string[] safe = {
                "explorer", "svchost", "winlogon", "csrss", "lsass", "services",
                "system", "dwm", "wininit", "smss", "taskhostw", "sihost",
                "runtimebroker", "searchhost", "shellexperiencehost",
                "startmenuexperiencehost", "fontdrvhost", "spoolsv", "audiodg",
                "conhost", "dllhost", "ctfmon", "msmpeng", "securityhealthservice",
                "devenv", "msbuild", "dotnet"
            };
            foreach (var s in safe)
                if (name.Contains(s)) return true;
            return false;
        }
    }
}