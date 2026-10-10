using System;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.ComponentModel;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
using System.Runtime.InteropServices;
using System.Management;

// Reference the custom WinLogic security service namespaces
using NexLauncher.Hooks;
using NexLauncher.Services;
using NeX_Launcher.Deployment;

namespace NeX_Launcher
{
    public class StartAppItem
    {
        public string Id { get; set; } = "";
        public string Name { get; set; } = "";
        public string IconCode { get; set; } = "";
        public System.Windows.Media.Brush IconColor { get; set; } = System.Windows.Media.Brushes.White;
        public string Description { get; set; } = "";
    }

    public partial class MainWindow : Window
    {
        #region Win32 API and COM Interfaces
        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        public const int SW_RESTORE = 9;

        // CoreAudio API COM interfaces for Master Volume
        [ComImport]
        [Guid("5CDF2C82-841E-4546-9722-0CF74078229A")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        public interface IAudioEndpointVolume
        {
            int RegisterControlChangeNotify(IntPtr pNotify);
            int UnregisterControlChangeNotify(IntPtr pNotify);
            int GetChannelCount(out int pnChannelCount);
            int SetMasterVolumeLevel(float fLevelDB, Guid pguidEventContext);
            int SetMasterVolumeLevelScalar(float fLevel, Guid pguidEventContext);
            int GetMasterVolumeLevel(out float pfLevelDB);
            int GetMasterVolumeLevelScalar(out float pfLevel);
        }

        [ComImport]
        [Guid("D666063F-1587-4E43-81F1-B948E807363F")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        internal interface IMMDevice
        {
            int Activate(ref Guid id, int clsCtx, IntPtr activationParams, out IAudioEndpointVolume aev);
        }

        [ComImport]
        [Guid("A95664D2-9614-4F35-A746-DE8DB63617E6")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        internal interface IMMDeviceEnumerator
        {
            int EnumAudioEndpoints(int dataFlow, int stateMask, out IntPtr devices);
            int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice ppEndpoint);
        }

        [ComImport]
        [Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
        internal class MMDeviceEnumerator { }
        #endregion
        // Core Security and Sync Services
        private KeyboardHook? _keyboardHook;
        private ProcessWatcher? _processWatcher;
        private FirebaseSyncManager? _firebaseSyncManager;

        // UI Binding Collections
        private readonly ObservableCollection<string> _logs = new();
        private DispatcherTimer? _clockTimer;
        private System.Windows.Threading.DispatcherTimer _telemetryTimer;
        
        // Explorer State
        private static readonly System.Net.Http.HttpClient _httpClient = new System.Net.Http.HttpClient();
        private readonly string _sandboxRoot = @"C:\NeX_Storage";
        private string _currentExplorerPath = @"C:\NeX_Storage";
        private const long MAX_QUOTA_BYTES = 1073741824; // 1GB
        private Random _random = new();
        private double[] _netBars = { 60, 80, 40, 90, 70, 20 };

        // Taskbar State
        private readonly System.Collections.Generic.Dictionary<int, System.Windows.Controls.Button> _activeNativeApps = new();
        private readonly System.Collections.Generic.Dictionary<string, string> _appStatusMap = new(StringComparer.OrdinalIgnoreCase);

        // System tray / widget state
        private bool _isMuted = false;
        private bool _wifiConnected = true;
        private string _deviceName = "NEX-WIN-001";

        public MainWindow()
        {
            // System.Windows.MessageBox.Show("BOOT TRACE 2: MainWindow Constructor reached.", "Tracer");
            try
            {
                InitializeComponent();
            }
            catch (Exception ex)
            {
                System.Windows.MessageBox.Show("XAML CRASH: " + ex.Message + "\n\nINNER EXCEPTION: " + ex.InnerException?.Message, "Tracer");
                Environment.Exit(1);
            }
            
            // Wire Loaded lifetime event (Closing is wired via XAML)
            this.SourceInitialized += (s, e) => FileLogger.Log($"[Window.SourceInitialized] HWND: {new System.Windows.Interop.WindowInteropHelper(this).Handle}");
            this.Loaded += MainWindow_Loaded;
            this.ContentRendered += (s, e) => FileLogger.Log("[Window.ContentRendered] MainWindow visual content rendered to screen.");
            this.Closed += (s, e) => FileLogger.Log($"[Window.Closed] MainWindow closed. Trace:\n{Environment.StackTrace}");
        }

        // =====================================================================
        // LIFECYCLE & INTEGRATION BRIDGE
        // =====================================================================
        private System.Windows.Media.Imaging.BitmapImage LoadImageSafely(string filePath)
        {
            var bitmap = new System.Windows.Media.Imaging.BitmapImage();
            using (var stream = new System.IO.FileStream(filePath, System.IO.FileMode.Open, System.IO.FileAccess.Read, System.IO.FileShare.Read))
            {
                bitmap.BeginInit();
                bitmap.CacheOption = System.Windows.Media.Imaging.BitmapCacheOption.OnLoad;
                bitmap.StreamSource = stream;
                bitmap.EndInit();
            }
            bitmap.Freeze(); // Ensures cross-thread safety and memory efficiency
            return bitmap;
        }

        private async void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            // System.Windows.MessageBox.Show("BOOT TRACE 4: MainWindow Loaded event fired.", "Tracer");
            try
            {
                FileLogger.Log("==================================================");
                FileLogger.Log("Enterprise Kiosk WPF Shell Launching.");
                SetupClockAndTelemetryTimers();

                AddLog("Initializing Enterprise Security Modules...");

                // Ensure Sandbox Directories
                System.IO.Directory.CreateDirectory(@"C:\NeX_Storage\Downloads");
                System.IO.Directory.CreateDirectory(@"C:\NeX_Storage\System");
                System.IO.Directory.CreateDirectory(@"C:\NeX_Storage\System\Wallpapers");

                // Copy built-in wallpapers
                try
                {
                    string sourceWallpapers = @"D:\project\DLK\Training\ReShell - Launcher -personal\NeX_Launcher\wallpaper";
                    if (System.IO.Directory.Exists(sourceWallpapers))
                    {
                        foreach (string file in System.IO.Directory.GetFiles(sourceWallpapers))
                        {
                            if (file.EndsWith(".jpg", StringComparison.OrdinalIgnoreCase) || file.EndsWith(".png", StringComparison.OrdinalIgnoreCase) || file.EndsWith(".jpeg", StringComparison.OrdinalIgnoreCase))
                            {
                                string destFile = System.IO.Path.Combine(@"C:\NeX_Storage\System\Wallpapers", System.IO.Path.GetFileName(file));
                                if (!System.IO.File.Exists(destFile))
                                {
                                    System.IO.File.Copy(file, destFile, true);
                                }
                            }
                        }
                    }
                    
                    var galleryItems = new System.Collections.ObjectModel.ObservableCollection<string>();
                    galleryItems.Clear();
                    foreach (string file in System.IO.Directory.GetFiles(@"C:\NeX_Storage\System\Wallpapers"))
                    {
                        if (!galleryItems.Contains(file)) galleryItems.Add(file);
                    }
                    if (WallpaperGalleryList != null)
                    {
                        WallpaperGalleryList.ItemsSource = galleryItems;
                    }
                }
                catch (Exception ex) { AddLog("Failed to initialize wallpaper gallery: " + ex.Message); }

                // Load Custom Wallpaper if exists
                if (System.IO.File.Exists(@"C:\NeX_Storage\System\active_wallpaper.jpg"))
                {
                    try
                    {
                        this.Background = new ImageBrush(LoadImageSafely(@"C:\NeX_Storage\System\active_wallpaper.jpg")) { Stretch = Stretch.UniformToFill };
                    }
                    catch (Exception ex) { AddLog("Failed to load wallpaper: " + ex.Message); }
                }

                // 0. Explorer Executioner
                AddLog("Connecting native Windows shell...");
                // foreach (var process in Process.GetProcessesByName("explorer"))
                // {
                //     try { process.Kill(); } catch { }
                // }

                // 1. Instantiate the native services
                _keyboardHook = new KeyboardHook();
                _processWatcher = new ProcessWatcher();
                _firebaseSyncManager = new FirebaseSyncManager("https://your-project-id.firebaseio.com/");

                // 2. Wire event subscription with thread-safe marshalling
                _firebaseSyncManager.OnActiveModeChanged += Firebase_OnActiveModeChanged;
                _firebaseSyncManager.OnRemoteInstallRequested += Firebase_OnRemoteInstallRequested;
                _firebaseSyncManager.OnRemoteCommandReceived += Firebase_OnRemoteCommandReceived;
                _firebaseSyncManager.OnInstalledAppsUpdated += Firebase_OnInstalledAppsUpdated;
                this.PreviewKeyDown += Window_PreviewKeyDown;

                // 3. Start services
                // AddLog("Engaging Keyboard Hook filter...");
                // _keyboardHook.Start();

                AddLog("Starting background Process Watcher daemon...");
                _processWatcher.Start();

                AddLog("Connecting Firebase Realtime state listeners...");
                _firebaseSyncManager.StartActiveModeListener();

                AddLog("Starting cloud watchdog heartbeat ping...");
                _firebaseSyncManager.StartHeartbeat();

                // Telemetry Fix
                _telemetryTimer?.Start();

                await LoadPersistentApplicationsAsync();

                AddLog("Secure environment established.");
            }
            catch (Exception ex)
            {
                AddLog($"Critical service startup failure: {ex.Message}");
                FileLogger.LogError(ex, "MainWindow_Loaded Integration");
            }
        }

        private void Window_Closing(object sender, CancelEventArgs e)
        {
            // Under kiosk mode, prevent Alt+F4 closures unless explicitly authorized
            FileLogger.Log("Lifetime Warning: Kiosk termination intercepted.");
            
            try
            {
                AddLog("Disengaging custom hooks and stopping watchers...");

                // Stop all services gracefully to prevent leaks, release keyboard filters, and close threads
                _keyboardHook?.Stop();
                _processWatcher?.Stop();
                _firebaseSyncManager?.Stop();

                FileLogger.Log("Services stopped successfully. Releasing shell.");
            }
            catch (Exception ex)
            {
                FileLogger.LogError(ex, "MainWindow_Closing Cleanup");
            }
        }

        private void Firebase_OnActiveModeChanged(string newMode)
        {
            // Thread-safe dispatch back to WPF UI Thread
            Dispatcher.Invoke(() =>
            {
                try
                {
                    AddLog($"Active policy change received from Firebase: {newMode.ToUpper()}");

                    // 1. Update UI Header Mode Label
                    // ModeText removed from UI

                    // 2. Set Active Mode on Native Process Watcher to update whitelist filter
                    _processWatcher?.SetMode(newMode);

                    // 3. Call UI lockdown configuration method
                    SetUIForMode(newMode);
                }
                catch (Exception ex)
                {
                    AddLog($"Error updating active mode policies: {ex.Message}");
                    FileLogger.LogError(ex, "Firebase_OnActiveModeChanged Handler");
                }
            });
        }

        private void SetUIForMode(string mode)
        {
            AddLog($"Updating local shell layout visual bounds for: {mode.ToUpper()}");
            
            if (mode.ToLower() == "lockdown")
            {
                // Visual indicators for secure lockdown mode
                AddLog("Lockdown visual mode active. Restricting external explorer overlays.");
                LockdownOverlay.Visibility = Visibility.Visible;
            }
            else
            {
                // Standard visual mode indicators
                AddLog("Standard visual mode active. Default access rules loaded.");
                LockdownOverlay.Visibility = Visibility.Collapsed;
            }
        }

        private void Firebase_OnRemoteInstallRequested(string url)
        {
            // Extract filename from URL or default to update.exe
            string fileName = "update.exe";
            try 
            {
                Uri uri = new Uri(url);
                fileName = System.IO.Path.GetFileName(uri.LocalPath);
                if (string.IsNullOrEmpty(fileName)) fileName = "update.exe";
            }
            catch { }
            
            System.Threading.Tasks.Task.Run(async () => await HandleRemoteDownloadAsync(url, fileName));
        }

        private void RemoteAppLauncher_Click(object sender, RoutedEventArgs e)
        {
            if (sender is System.Windows.Controls.Button btn && btn.Tag is string exePath)
            {
                try
                {
                    AddLog($"Launching remote application: {exePath}");
                    var startInfo = new ProcessStartInfo
                    {
                        FileName = exePath,
                        UseShellExecute = true
                    };
                    
                    this.Topmost = false; // Z-Order Fix: Drop WPF shell behind
                    Process p = Process.Start(startInfo);
                    if (p != null)
                    {
                        System.Threading.Tasks.Task.Run(async () =>
                        {
                            try
                            {
                                p.WaitForInputIdle(3000);
                                await System.Threading.Tasks.Task.Delay(500);
                                Dispatcher.Invoke(() =>
                                {
                                    IntPtr handle = p.MainWindowHandle;
                                    if (handle != IntPtr.Zero)
                                    {
                                        ShowWindow(handle, SW_RESTORE);
                                        SetForegroundWindow(handle);
                                    }
                                });
                            }
                            catch { }
                        });
                    }
                }
                catch (Exception ex)
                {
                    AddLog($"Launch error for {exePath}: {ex.Message}");
                }
            }
        }

        // =====================================================================
        // NATIVE WINDOWS SPONSORED APP LAUNCHER
        // =====================================================================
        private void AppLauncher_Click(object sender, RoutedEventArgs e)
        {
            if (sender is System.Windows.Controls.Button btn && btn.Tag is string appId)
            {
                LaunchNativeWindowsApplication(appId);
            }
        }

        private void LaunchNativeWindowsApplication(string appId)
        {
            try
            {
                string? fileName = null;
                string? arguments = null;

                // Resolve click bindings directly to actual Windows executables
                switch (appId.ToLower())
                {
                    case "edge":
                        fileName = "msedge.exe";
                        arguments = "https://www.google.com";
                        break;
                    case "word":
                        fileName = "write.exe"; // Wordpad (preinstalled Windows binary)
                        break;
                    case "excel":
                        fileName = "notepad.exe"; // Fallback to notepad for diagnostic sheets
                        break;
                    case "pdf":
                        fileName = "msedge.exe"; // Fallback to edge for native PDF rendering
                        arguments = "https://www.adobe.com";
                        break;
                    case "notepad":
                        fileName = "notepad.exe";
                        break;
                    case "calculator":
                        fileName = "calc.exe";
                        break;
                    case "paint":
                        fileName = "mspaint.exe";
                        break;
                    case "files":
                    case "storage":
                        // Handled internally now
                        break;
                    case "browser":
                    case "webframe":
                        fileName = "msedge.exe";
                        arguments = "https://www.google.com";
                        break;
                    case "camera":
                        fileName = "microsoft.windows.camera:"; // Windows Camera App Protocol
                        break;
                }

                if (appId.ToLower() == "settings")
                {
                    DesktopGrid.Visibility = Visibility.Collapsed;
                    AppSandboxFrame.Visibility = Visibility.Visible;
                    LiveAppViewport.Visibility = Visibility.Visible;
                    SettingsSandbox.Visibility = Visibility.Visible;
                    System.Windows.Controls.Panel.SetZIndex(SettingsSandbox, 999);
                    SandboxedExplorerPane.Visibility = Visibility.Collapsed;
                    AppFrameTitle.Text = "SYSTEM SETTINGS & DIAGNOSTICS";
                    CreateInternalTaskbarIcon("settings", -1, "\uE713");
                    return;
                }

                if (appId.ToLower() == "files" || appId.ToLower() == "storage")
                {
                    DesktopGrid.Visibility = Visibility.Collapsed;
                    AppSandboxFrame.Visibility = Visibility.Visible;
                    LiveAppViewport.Visibility = Visibility.Visible;
                    SettingsSandbox.Visibility = Visibility.Collapsed;
                    SandboxedExplorerPane.Visibility = Visibility.Visible;
                    System.Windows.Controls.Panel.SetZIndex(SandboxedExplorerPane, 999);
                    AppFrameTitle.Text = "SECURE STORAGE SANDBOX";
                    CreateInternalTaskbarIcon("files", -2, "\uE8D5");
                    InitializeExplorer();
                    return;
                }

                if (!string.IsNullOrEmpty(fileName))
                {
                    AddLog($"Launching native process: {fileName}");
                    
                    // BROWSER REGISTRY HIJACK
                    if (appId.ToLower() == "edge" || appId.ToLower() == "chrome")
                    {
                        try
                        {
                            using (var key = Microsoft.Win32.Registry.CurrentUser.CreateSubKey(@"Software\Policies\Microsoft\Edge"))
                            {
                                key?.SetValue("DownloadDirectory", @"C:\NeX_Storage\Downloads", Microsoft.Win32.RegistryValueKind.String);
                            }
                            using (var key = Microsoft.Win32.Registry.CurrentUser.CreateSubKey(@"Software\Policies\Google\Chrome"))
                            {
                                key?.SetValue("DownloadDirectory", @"C:\NeX_Storage\Downloads", Microsoft.Win32.RegistryValueKind.String);
                            }
                            AddLog("Browser download directories hijacked to sandbox.");
                        }
                        catch (Exception ex) { AddLog("Failed to hijack browser registry: " + ex.Message); }
                    }
                    
                    var startInfo = new ProcessStartInfo
                    {
                        FileName = fileName,
                        Arguments = arguments ?? string.Empty,
                        UseShellExecute = true, // Re-route through the Windows shell
                        WorkingDirectory = @"C:\"
                    };

                    this.Topmost = false; // Z-Order Fix: Allow native app to foreground
                    try
                    {
                        Process p = Process.Start(startInfo);
                        if (p != null)
                        {
                            CreateTaskbarIcon(p, appId);
                            
                            System.Threading.Tasks.Task.Run(async () =>
                            {
                                try
                                {
                                    p.WaitForInputIdle(3000);
                                    await System.Threading.Tasks.Task.Delay(500);
                                    Dispatcher.Invoke(() =>
                                    {
                                        IntPtr handle = p.MainWindowHandle;
                                        if (handle != IntPtr.Zero)
                                        {
                                            ShowWindow(handle, SW_RESTORE);
                                            SetForegroundWindow(handle);
                                        }
                                    });
                                }
                                catch { }
                            });
                        }
                    }
                    catch (Exception ex)
                    {
                        AddLog($"Process.Start failed for {fileName}: {ex.Message}");
                    }
                }
                else
                {
                    AddLog($"Launch error: Unsupported app tag '{appId}'");
                }
            }
            catch (Exception ex)
            {
                AddLog($"Launch native app failed: {ex.Message}");
                FileLogger.LogError(ex, $"LaunchNativeWindowsApplication - {appId}");
            }
        }

        public async System.Threading.Tasks.Task HandleRemoteDownloadAsync(string downloadUrl, string fileName)
        {
            try
            {
                AddLog($"Starting download for {fileName}...");
                var response = await _httpClient.GetAsync(downloadUrl);
                response.EnsureSuccessStatusCode();

                string savePath = System.IO.Path.Combine(@"C:\NeX_Storage\Downloads", fileName);
                using (var fs = new System.IO.FileStream(savePath, System.IO.FileMode.Create, System.IO.FileAccess.Write, System.IO.FileShare.None))
                {
                    await response.Content.CopyToAsync(fs);
                }

                AddLog($"Download complete: {fileName}");

                CreateOrUpdateDesktopShortcut(savePath, fileName);
            }
            catch (Exception ex)
            {
                AddLog($"Download failed: {ex.Message}");
            }
        }

        private async System.Threading.Tasks.Task LoadPersistentApplicationsAsync()
        {
            try
            {
                string path = @"C:\NeX_Storage\Downloads\";
                if (!System.IO.Directory.Exists(path)) return;

                // Offload IO bound folder scanning (ONLY .exe files)
                string[] files = await System.Threading.Tasks.Task.Run(() => System.IO.Directory.GetFiles(path, "*.exe"));
                
                foreach (var file in files)
                {
                    string fileName = System.IO.Path.GetFileName(file);
                    CreateOrUpdateDesktopShortcut(file, fileName);
                }
            }
            catch (Exception ex)
            {
                AddLog($"Failed to load persistent applications: {ex.Message}");
            }
        }

        private void CreateOrUpdateDesktopShortcut(string savePath, string fileName)
        {
            Dispatcher.Invoke(() =>
            {
                foreach (var child in AppLauncherPanel.Children)
                {
                    if (child is System.Windows.Controls.Button existingBtn && existingBtn.Tag is string tagPath && tagPath.Equals(savePath, StringComparison.OrdinalIgnoreCase))
                    {
                        return;
                    }
                }

                var btn = new System.Windows.Controls.Button
                {
                    Style = (Style)FindResource("DesktopShortcutStyle"),
                    Margin = new Thickness(0, 0, 0, 8),
                    HorizontalAlignment = System.Windows.HorizontalAlignment.Left,
                    Tag = savePath
                };

                var sp = new System.Windows.Controls.StackPanel { HorizontalAlignment = System.Windows.HorizontalAlignment.Center };
                
                var iconBorder = new System.Windows.Controls.Border
                {
                    Width = 48,
                    Height = 48,
                    CornerRadius = new CornerRadius(8),
                    Background = new System.Windows.Media.SolidColorBrush((System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#33FFFFFF")),
                    Margin = new Thickness(0,0,0,4)
                };

                var icon = new System.Windows.Controls.TextBlock
                {
                    Text = "EXE",
                    FontFamily = new System.Windows.Media.FontFamily("Segoe UI"),
                    FontWeight = FontWeights.Bold,
                    FontSize = 16,
                    Foreground = System.Windows.Media.Brushes.White,
                    HorizontalAlignment = System.Windows.HorizontalAlignment.Center,
                    VerticalAlignment = VerticalAlignment.Center
                };
                iconBorder.Child = icon;

                var txt = new System.Windows.Controls.TextBlock
                {
                    Text = fileName,
                    Foreground = System.Windows.Media.Brushes.White,
                    FontSize = 13,
                    HorizontalAlignment = System.Windows.HorizontalAlignment.Center,
                    TextAlignment = TextAlignment.Center,
                    TextWrapping = TextWrapping.Wrap,
                    Width = 80
                };

                sp.Children.Add(iconBorder);
                sp.Children.Add(txt);
                btn.Content = sp;

                btn.Click += (s, e) =>
                {
                    try
                    {
                        if (_appStatusMap.TryGetValue(fileName, out string status) && status.Equals("blocked", StringComparison.OrdinalIgnoreCase))
                        {
                            System.Windows.MessageBox.Show("This app is locked by the Administrator.", "Access Denied", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Warning);
                            return;
                        }

                        var psi = new ProcessStartInfo(savePath) { UseShellExecute = true };
                        Process.Start(psi);
                        AddLog($"Executed downloaded payload: {fileName}");
                    }
                    catch (Exception ex)
                    {
                        AddLog($"Failed to execute payload: {ex.Message}");
                    }
                };

                AppLauncherPanel.Children.Add(btn);
                
                // Immediately check visibility state
                if (_appStatusMap.TryGetValue(fileName, out string currentStatus) && currentStatus.Equals("disabled", StringComparison.OrdinalIgnoreCase))
                {
                    btn.Visibility = Visibility.Collapsed;
                }
            });
        }

        private void CreateInternalTaskbarIcon(string appId, int dummyId, string iconCode)
        {
            if (_activeNativeApps.ContainsKey(dummyId)) return; // Already exists

            System.Windows.Controls.Button btn = new System.Windows.Controls.Button
            {
                Style = (Style)FindResource("TaskbarButtonStyle"),
                Content = new TextBlock
                {
                    Text = iconCode,
                    Style = (Style)FindResource("FontIcon"),
                    FontSize = 18,
                    Foreground = new SolidColorBrush((System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#60CDFF"))
                }
            };

            btn.Click += (s, e) =>
            {
                try
                {
                    this.Topmost = true;
                    if (appId == "settings")
                    {
                        SettingsSandbox.Visibility = Visibility.Visible;
                        SandboxedExplorerPane.Visibility = Visibility.Collapsed;
                        AppFrameTitle.Text = "SYSTEM SETTINGS & DIAGNOSTICS";
                    }
                    else if (appId == "files")
                    {
                        SandboxedExplorerPane.Visibility = Visibility.Visible;
                        SettingsSandbox.Visibility = Visibility.Collapsed;
                        AppFrameTitle.Text = "SECURE STORAGE SANDBOX";
                    }
                    DesktopGrid.Visibility = Visibility.Collapsed;
                    AppSandboxFrame.Visibility = Visibility.Visible;
                }
                catch { }
            };

            ActiveAppsTaskbar.Children.Add(btn);
            _activeNativeApps[dummyId] = btn;
        }

        private void CreateTaskbarIcon(Process p, string appId)
        {
            string iconCode = "\uE774"; // default
            switch (appId.ToLower())
            {
                case "edge": iconCode = "\uE774"; break;
                case "word": iconCode = "\uE1C2"; break;
                case "excel": iconCode = "\uE80A"; break;
                case "pdf": iconCode = "\uE8A5"; break;
                case "notepad": iconCode = "\uE70F"; break;
                case "calculator": iconCode = "\uE1D0"; break;
                case "paint": iconCode = "\uE2B1"; break;
                case "camera": iconCode = "\uE114"; break;
            }

            int pid = -1;
            try { pid = p.Id; } catch { return; } // Safely grab ID or abort if already exited

            System.Windows.Controls.Button btn = new System.Windows.Controls.Button
            {
                Style = (Style)FindResource("TaskbarButtonStyle"),
                Content = new TextBlock
                {
                    Text = iconCode,
                    Style = (Style)FindResource("FontIcon"),
                    FontSize = 18,
                    Foreground = new SolidColorBrush((System.Windows.Media.Color)System.Windows.Media.ColorConverter.ConvertFromString("#60CDFF"))
                }
            };

            btn.Click += (s, e) =>
            {
                try
                {
                    if (!p.HasExited)
                    {
                        IntPtr handle = p.MainWindowHandle;
                        if (handle != IntPtr.Zero)
                        {
                            ShowWindow(handle, SW_RESTORE);
                            SetForegroundWindow(handle);
                            this.Topmost = false;
                        }
                    }
                    else
                    {
                        ActiveAppsTaskbar.Children.Remove(btn);
                        _activeNativeApps.Remove(pid);
                    }
                }
                catch { }
            };

            p.EnableRaisingEvents = true;
            p.Exited += (s, e) =>
            {
                Dispatcher.Invoke(() =>
                {
                    ActiveAppsTaskbar.Children.Remove(btn);
                    _activeNativeApps.Remove(pid);
                });
            };

            ActiveAppsTaskbar.Children.Add(btn);
            _activeNativeApps[pid] = btn;
        }

        private void HomeButton_Click(object sender, RoutedEventArgs e)
        {
            if (StartMenuOverlay.Visibility == Visibility.Visible)
            {
                StartMenuOverlay.Visibility = Visibility.Collapsed;
                StartMenuDismissShield.Visibility = Visibility.Collapsed;
            }
            else
            {
                StartMenuOverlay.Visibility = Visibility.Visible;
                StartMenuDismissShield.Visibility = Visibility.Visible;
                
                // Restore Z-Order, show desktop
                this.Topmost = true;
                DesktopGrid.Visibility = Visibility.Visible;
                AppSandboxFrame.Visibility = Visibility.Collapsed;
                SettingsSandbox.Visibility = Visibility.Collapsed;
                SandboxedExplorerPane.Visibility = Visibility.Collapsed;
            }
        }

        private void StartMenuDismiss_Click(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            StartMenuOverlay.Visibility = Visibility.Collapsed;
            StartMenuDismissShield.Visibility = Visibility.Collapsed;
        }

        // =====================================================================
        // SIMULATED SYSTEM CLOCK & WIDGET TELEMETRY
        // =====================================================================
        private void SetupClockAndTelemetryTimers()
        {
            _clockTimer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(1) };
            _clockTimer.Tick += (s, e) =>
            {
                if (TaskbarClockText != null)
                {
                    TaskbarClockText.Text = DateTime.Now.ToString("HH:mm");
                }
                if (TaskbarDateText != null)
                {
                    TaskbarDateText.Text = DateTime.Now.ToString("dd-MM-yyyy");
                }
            };
            _clockTimer.Start();

            _telemetryTimer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(15) };
            _telemetryTimer.Tick += async (s, e) =>
            {
                await PushTelemetryAsync("ONLINE");
                await SyncInstalledAppsToFirebaseAsync();
            };
            _telemetryTimer.Start();

            AddLog("Kiosk shell clock/telemetry watchdogs initialized.");
        }

        private object GetSystemTelemetry(string status)
        {
            string mac = "UNKNOWN";
            try
            {
                var nic = System.Linq.Enumerable.FirstOrDefault(System.Net.NetworkInformation.NetworkInterface.GetAllNetworkInterfaces(), n => n.OperationalStatus == System.Net.NetworkInformation.OperationalStatus.Up && n.NetworkInterfaceType != System.Net.NetworkInformation.NetworkInterfaceType.Loopback);
                if (nic != null) mac = nic.GetPhysicalAddress().ToString();
            } catch {}

            return new
            {
                mac_adapter = mac,
                last_heartbeat_timestamp = DateTime.UtcNow.ToString("O"),
                kiosk_status = status,
                active_mode = "DEFAULT NODE"
            };
        }

        private async System.Threading.Tasks.Task PushTelemetryAsync(string status = "ONLINE")
        {
            try
            {
                var payload = GetSystemTelemetry(status);
                string json = System.Text.Json.JsonSerializer.Serialize(payload);
                var content = new System.Net.Http.StringContent(json, System.Text.Encoding.UTF8, "application/json");
                await _httpClient.PutAsync("https://your-project-id.firebaseio.com/Kiosks/LAPTOP_01/Telemetry.json", content);
            }
            catch { }
        }

        private async System.Threading.Tasks.Task SyncInstalledAppsToFirebaseAsync()
        {
            try
            {
                string path = @"C:\NeX_Storage\Downloads\";
                if (!System.IO.Directory.Exists(path)) return;

                var apps = new System.Collections.Generic.List<object>();
                foreach (var file in System.IO.Directory.GetFiles(path))
                {
                    string fileName = System.IO.Path.GetFileName(file);
                    string nameNoExt = System.IO.Path.GetFileNameWithoutExtension(file);
                    bool isRunning = false;
                    try
                    {
                        var procs = Process.GetProcessesByName(nameNoExt);
                        isRunning = procs.Length > 0;
                    }
                    catch { }

                    apps.Add(new
                    {
                        fileName = fileName,
                        creationDate = System.IO.File.GetCreationTimeUtc(file).ToString("O"),
                        isRunning = isRunning,
                        status = _appStatusMap.TryGetValue(fileName, out string s) ? s : "active"
                    });
                }

                string json = System.Text.Json.JsonSerializer.Serialize(apps);
                var content = new System.Net.Http.StringContent(json, System.Text.Encoding.UTF8, "application/json");
                await _httpClient.PutAsync("https://your-project-id.firebaseio.com/Kiosks/LAPTOP_01/InstalledApps.json", content);
            }
            catch (Exception ex)
            {
                AddLog($"SyncInstalledApps error: {ex.Message}");
            }
        }

        private void Firebase_OnInstalledAppsUpdated(string appsJson)
        {
            Dispatcher.Invoke(() =>
            {
                try
                {
                    using var doc = System.Text.Json.JsonDocument.Parse(appsJson);
                    if (doc.RootElement.ValueKind == System.Text.Json.JsonValueKind.Array)
                    {
                        foreach (var app in doc.RootElement.EnumerateArray())
                        {
                            if (app.TryGetProperty("fileName", out var nameProp))
                            {
                                string fileName = nameProp.GetString() ?? "";
                                string status = "active";
                                if (app.TryGetProperty("status", out var statusProp))
                                {
                                    status = statusProp.GetString() ?? "active";
                                }

                                if (!string.IsNullOrEmpty(fileName))
                                {
                                    _appStatusMap[fileName] = status;

                                    string savePath = System.IO.Path.Combine(@"C:\NeX_Storage\Downloads", fileName);
                                    foreach (var child in AppLauncherPanel.Children)
                                    {
                                        if (child is System.Windows.Controls.Button btn && btn.Tag is string tagPath && tagPath.Equals(savePath, StringComparison.OrdinalIgnoreCase))
                                        {
                                            btn.Visibility = status.Equals("disabled", StringComparison.OrdinalIgnoreCase) ? Visibility.Collapsed : Visibility.Visible;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                catch (Exception ex)
                {
                    AddLog($"Error processing installed apps update: {ex.Message}");
                }
            });
        }

        private void Firebase_OnRemoteCommandReceived(string commandJson)
        {
            Dispatcher.Invoke(() =>
            {
                try
                {
                    using var doc = System.Text.Json.JsonDocument.Parse(commandJson);
                    if (doc.RootElement.TryGetProperty("action", out var actionElement) &&
                        doc.RootElement.TryGetProperty("target", out var targetElement))
                    {
                        string action = actionElement.GetString() ?? "";
                        string target = targetElement.GetString() ?? "";

                        if (action == "delete_app" && !string.IsNullOrEmpty(target))
                        {
                            string targetPath = System.IO.Path.Combine(@"C:\NeX_Storage\Downloads\", target);
                            AddLog($"Remote Delete Requested for: {target}");
                            
                            // 1. Kill Process safely
                            string nameNoExt = System.IO.Path.GetFileNameWithoutExtension(target);
                            try
                            {
                                foreach (var p in Process.GetProcessesByName(nameNoExt))
                                {
                                    try { if (!p.HasExited) p.Kill(); } catch { }
                                }
                            }
                            catch (Exception ex) { AddLog($"Kill error: {ex.Message}"); }

                            // 2. Delete File
                            try
                            {
                                if (System.IO.File.Exists(targetPath))
                                {
                                    System.IO.File.Delete(targetPath);
                                    AddLog($"Deleted file: {targetPath}");
                                }
                            }
                            catch (Exception ex) { AddLog($"Delete error: {ex.Message}"); }

                            // 3. Remove Desktop Shortcut
                            System.Windows.Controls.Button? toRemove = null;
                            foreach (var child in DesktopGrid.Children)
                            {
                                if (child is System.Windows.Controls.Button btn && btn.Tag is string tagPath && tagPath.Equals(targetPath, StringComparison.OrdinalIgnoreCase))
                                {
                                    toRemove = btn;
                                    break;
                                }
                            }
                            if (toRemove != null)
                            {
                                DesktopGrid.Children.Remove(toRemove);
                                AddLog($"Removed Desktop shortcut for {target}");
                            }
                        }
                    }
                }
                catch (Exception ex)
                {
                    AddLog($"Error processing remote command: {ex.Message}");
                }
            });
        }

        private void Window_PreviewKeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            if (e.Key == System.Windows.Input.Key.D && (System.Windows.Input.Keyboard.Modifiers & (System.Windows.Input.ModifierKeys.Control | System.Windows.Input.ModifierKeys.Shift)) == (System.Windows.Input.ModifierKeys.Control | System.Windows.Input.ModifierKeys.Shift))
            {
                e.Handled = true;
                RunSystemDiagnostics();
            }
        }

        private void RunSystemDiagnostics()
        {
            try
            {
                AddLog("Running System Diagnostics...");
                var sb = new System.Text.StringBuilder();
                sb.AppendLine("=== NEX LAUNCHER DIAGNOSTICS ===");
                sb.AppendLine($"Timestamp: {DateTime.Now}");

                int expCount = Process.GetProcessesByName("explorer").Length;
                sb.AppendLine($"[FR-1] Explorer Process Count: {expCount} (Pass = {expCount == 0})");

                bool hooksActive = _keyboardHook != null && _keyboardHook.IsRunning;
                sb.AppendLine($"[FR-2/3] Keyboard Hooks Active: {hooksActive}");

                bool telemetryActive = _telemetryTimer != null && _telemetryTimer.IsEnabled;
                sb.AppendLine($"[FR-5] Telemetry Timer Active: {telemetryActive}");

                bool listenerActive = _firebaseSyncManager != null && _firebaseSyncManager.IsListenerActive;
                sb.AppendLine($"[FR-7] Remote Command Listener Active: {listenerActive}");

                sb.AppendLine("================================");

                string logPath = @"C:\NeX_Storage\System\Diagnostics.log";
                System.IO.File.AppendAllText(logPath, sb.ToString());
                AddLog($"Diagnostics written to {logPath}");
            }
            catch (Exception ex)
            {
                AddLog($"Diagnostics error: {ex.Message}");
            }
        }

        private void AddLog(string msg)
        {
            string time = DateTime.Now.ToString("HH:mm:ss");
            string entry = $"[{time}] {msg}";
            _logs.Insert(0, entry);
            
            // Limit UI list output to prevent bloat
            if (_logs.Count > 100) _logs.RemoveAt(100);

            // Print directly to text logger
            FileLogger.Log(msg);
        }

        // =====================================================================
        // TASKBAR ACTIONS & SYSTEM OVERLAYS
        // =====================================================================
        private void HeaderBranding_Click(object sender, MouseButtonEventArgs e)
        {
            AddLog("Navigated back to primary desktop shell view.");
        }



        private void QuickPower_Click(object sender, RoutedEventArgs e)
        {
            ShutdownModal.Visibility = Visibility.Visible;
        }

        private void TopbarSettings_Click(object sender, RoutedEventArgs e)
        {
            LaunchNativeWindowsApplication("settings");
        }

        private void TopbarHelp_Click(object sender, RoutedEventArgs e)
        {
            // Open user manual
            AddLog("Displaying systems user help index.");
        }

        private void PowerCancel_Click(object sender, RoutedEventArgs e)
        {
            ShutdownModal.Visibility = Visibility.Collapsed;
        }

        private void PowerLock_Click(object sender, RoutedEventArgs e)
        {
            ShutdownModal.Visibility = Visibility.Collapsed;
            AddLog("Workstation lock command sent.");
        }

        private async void PowerRestart_Click(object sender, RoutedEventArgs e)
        {
            ShutdownModal.Visibility = Visibility.Collapsed;
            DesktopGrid.Visibility = Visibility.Collapsed;
            PowerOffOverlay.Visibility = Visibility.Visible;

            PowerOffLogs.Text = "LUMINA KIOSK WORKSTATION [RESTARTING...]\n" +
                                "FLUSHING SERVICE LOOPS...\n" +
                                "✔ Unhooking low-level keyboard monitors\n" +
                                "✔ Terminating process watchdogs\n" +
                                "✔ Releasing Firebase listeners\n" +
                                "✔ REBOOT SYSTEM INITIALIZED\n";

            await System.Threading.Tasks.Task.Delay(2000);
            
            // Re-engage services (acting as simulated soft-reboot of client shell)
            PowerOffOverlay.Visibility = Visibility.Collapsed;
            DesktopGrid.Visibility = Visibility.Visible;
            AddLog("Kiosk shell soft-reboot cycle complete.");
        }

        private async void PowerShutdown_Click(object sender, RoutedEventArgs e)
        {
            ShutdownModal.Visibility = Visibility.Collapsed;
            DesktopGrid.Visibility = Visibility.Collapsed;
            PowerOffOverlay.Visibility = Visibility.Visible;

            PowerOffLogs.Text = "LUMINA KIOSK WORKSTATION [SHUTTING DOWN...]\n" +
                                "FLUSHING SERVICE LOOPS...\n" +
                                "✔ Unhooking low-level keyboard monitors\n" +
                                "✔ Terminating process watchdogs\n" +
                                "✔ Releasing Firebase listeners\n" +
                                "✔ KIOSK SHUTDOWN INSTRUCTIONS COMPLETED\n";

            await System.Threading.Tasks.Task.Delay(2000);
            await PushTelemetryAsync("OFFLINE");
            System.Windows.Application.Current.Shutdown();
        }

        // =====================================================================
        // BACKWARD COMPATIBILITY STUBS FOR UNUSED XAML COMPONENT EVENTS
        // =====================================================================
        private void FileFilter_Click(object sender, RoutedEventArgs e) { }
        private void FileSearch_TextChanged(object sender, TextChangedEventArgs e) { }
        private void FileListView_MouseDoubleClick(object sender, MouseButtonEventArgs e) { }
        private void CameraGridToggle_Click(object sender, RoutedEventArgs e) { }
        private void CameraMute_Click(object sender, RoutedEventArgs e) { }
        private void CameraShutter_Click(object sender, RoutedEventArgs e) { }
        private void SettingsPane_Checked(object sender, RoutedEventArgs e)
        {
            if (SettingsPersonalizationPane == null) return;
            
            SettingsPersonalizationPane.Visibility = Visibility.Collapsed;
            SettingsHardwarePane.Visibility = Visibility.Collapsed;
            SettingsOverridePane.Visibility = Visibility.Collapsed;

            if (SettingsPersonalizationRadio.IsChecked == true) SettingsPersonalizationPane.Visibility = Visibility.Visible;
            else if (SettingsHardwareRadio.IsChecked == true) SettingsHardwarePane.Visibility = Visibility.Visible;
            else if (SettingsOverrideRadio.IsChecked == true) SettingsOverridePane.Visibility = Visibility.Visible;
        }

        private void ExplorerDownloads_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                string path = @"C:\NeX_Storage\Downloads";
                if (!System.IO.Directory.Exists(path)) System.IO.Directory.CreateDirectory(path);
                LoadDirectory(path);
            }
            catch (Exception ex) { AddLog("Error navigating to downloads: " + ex.Message); }
        }

        private void WallpaperGalleryList_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            try
            {
                if (WallpaperGalleryList.SelectedItem is string selectedImagePath)
                {
                    WallpaperPreview.Source = LoadImageSafely(selectedImagePath);
                }
            }
            catch (Exception ex)
            {
                AddLog("Failed to preview wallpaper: " + ex.Message);
            }
        }

        private void SetBackground_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (WallpaperGalleryList.SelectedItem is string selectedImagePath)
                {
                    string targetPath = @"C:\NeX_Storage\System\active_wallpaper.jpg";
                    System.IO.File.Copy(selectedImagePath, targetPath, true);
                    
                    this.Background = new ImageBrush(LoadImageSafely(targetPath)) { Stretch = Stretch.UniformToFill };
                    
                    AddLog($"Custom wallpaper applied: {System.IO.Path.GetFileName(selectedImagePath)}");
                }
            }
            catch (Exception ex)
            {
                AddLog("Failed to update wallpaper: " + ex.Message);
            }
        }

        private async void RestoreSystem_Click(object sender, RoutedEventArgs e)
        {
            if (OverrideUsername.Text == "MONISH" && OverridePassword.Password == "2005")
            {
                OverrideErrorText.Visibility = Visibility.Collapsed;
                AddLog("CRITICAL: Admin Override triggered by MONISH.");
                
                try
                {
                    // Step A: Registry Revert
                    using (Microsoft.Win32.RegistryKey key = Microsoft.Win32.Registry.CurrentUser.OpenSubKey(@"Software\Microsoft\Windows NT\CurrentVersion\Winlogon", true))
                    {
                        if (key != null)
                        {
                            key.SetValue("Shell", "explorer.exe");
                        }
                    }

                    // Step B: Graceful Teardown
                    _keyboardHook?.Stop();
                    _processWatcher?.Stop();
                    _firebaseSyncManager?.Stop();
                    
                    // Step C: Logging is already done via AddLog which calls FileLogger
                    
                    // Step D: Resurrection
                    Process.Start("explorer.exe");
                    
                    // Step E: Exit
                    await PushTelemetryAsync("OFFLINE");
                    System.Windows.Application.Current.Shutdown();
                }
                catch (Exception ex)
                {
                    AddLog($"Override execution failed: {ex.Message}");
                }
            }
            else
            {
                OverrideErrorText.Visibility = Visibility.Visible;
                AddLog("Failed Administrator Override attempt.");
            }
        }
        private void SettingsDeviceName_Changed(object sender, TextChangedEventArgs e) { }
        private void SettingsClearLogs_Click(object sender, RoutedEventArgs e) { }
        private void SolutionExplorerList_SelectionChanged(object sender, SelectionChangedEventArgs e) { }
        private void CopySourceCode_Click(object sender, RoutedEventArgs e) { }
        private void FileLaunch_Click(object sender, RoutedEventArgs e) { }
        private void FileDelete_Click(object sender, RoutedEventArgs e) { }
        private void ExcelCalculate_Click(object sender, RoutedEventArgs e) { }
        private void WordBold_Click(object sender, RoutedEventArgs e) { }
        private void WordItalic_Click(object sender, RoutedEventArgs e) { }
        private void WordUnderline_Click(object sender, RoutedEventArgs e) { }
        private void WordSave_Click(object sender, RoutedEventArgs e) { }
        private void BrowserGo_Click(object sender, RoutedEventArgs e) { }
        private void BrowserUrl_KeyDown(object sender, System.Windows.Input.KeyEventArgs e) { }
        private void BrowserBack_Click(object sender, RoutedEventArgs e) { }
        private void BrowserForward_Click(object sender, RoutedEventArgs e) { }
        private void BrowserRefresh_Click(object sender, RoutedEventArgs e) { }
        private void MyWebBrowser_Navigating(object sender, System.Windows.Navigation.NavigatingCancelEventArgs e) { }
        private void MyWebBrowser_LoadCompleted(object sender, System.Windows.Navigation.NavigationEventArgs e) { }
        private void PdfPrev_Click(object sender, RoutedEventArgs e) { }
        private void PdfNext_Click(object sender, RoutedEventArgs e) { }
        private void ViewMode_Changed(object sender, RoutedEventArgs e) { }
        private void AppFrameMinimize_Click(object sender, RoutedEventArgs e) { }
        private void AppFrameClose_Click(object sender, RoutedEventArgs e) 
        { 
            SettingsSandbox.Visibility = Visibility.Collapsed;
            SandboxedExplorerPane.Visibility = Visibility.Collapsed;
            AppSandboxFrame.Visibility = Visibility.Collapsed;
            DesktopGrid.Visibility = Visibility.Visible;

            if (_activeNativeApps.TryGetValue(-1, out var settingsBtn))
            {
                ActiveAppsTaskbar.Children.Remove(settingsBtn);
                _activeNativeApps.Remove(-1);
            }
            if (_activeNativeApps.TryGetValue(-2, out var filesBtn))
            {
                ActiveAppsTaskbar.Children.Remove(filesBtn);
                _activeNativeApps.Remove(-2);
            }
        }

        // =====================================================================
        // HARDWARE CONTROLS (WMI & COM COREAUDIO)
        // =====================================================================
        private void BrightnessSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            try
            {
                byte brightness = (byte)e.NewValue;
                using (var mclass = new ManagementClass("WmiMonitorBrightnessMethods"))
                {
                    mclass.Scope = new ManagementScope(@"\\.\root\wmi");
                    using (var instances = mclass.GetInstances())
                    {
                        foreach (ManagementObject instance in instances)
                        {
                            instance.InvokeMethod("WmiSetBrightness", new object[] { 1, brightness });
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                AddLog($"Brightness control failed: {ex.Message}");
            }
        }

        private IAudioEndpointVolume? _masterVolumeControl = null;
        
        private void VolumeSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            try
            {
                if (_masterVolumeControl == null)
                {
                    Type enumeratorType = Type.GetTypeFromCLSID(new Guid("BCDE0395-E52F-467C-8E3D-C4579291692E"));
                    if (enumeratorType != null)
                    {
                        IMMDeviceEnumerator enumerator = (IMMDeviceEnumerator)Activator.CreateInstance(enumeratorType);
                        enumerator.GetDefaultAudioEndpoint(0, 1, out IMMDevice device);
                        Guid iid = typeof(IAudioEndpointVolume).GUID;
                        device.Activate(ref iid, 23, IntPtr.Zero, out _masterVolumeControl);
                    }
                }
                
                if (_masterVolumeControl != null)
                {
                    float scalarVolume = (float)(e.NewValue / 100.0);
                    _masterVolumeControl.SetMasterVolumeLevelScalar(scalarVolume, Guid.Empty);
                }
            }
            catch (Exception ex)
            {
                AddLog($"Volume control failed: {ex.Message}");
            }
        }
        private void CalcCE_Click(object sender, RoutedEventArgs e) { }
        private void CalcC_Click(object sender, RoutedEventArgs e) { }
        private void CalcDel_Click(object sender, RoutedEventArgs e) { }
        private void CalcNum_Click(object sender, RoutedEventArgs e) { }
        private void CalcOp_Click(object sender, RoutedEventArgs e) { }
        private void CalcNeg_Click(object sender, RoutedEventArgs e) { }
        private void CalcDot_Click(object sender, RoutedEventArgs e) { }
        private void CalcEqual_Click(object sender, RoutedEventArgs e) { }
        private void CalcClearHistory_Click(object sender, RoutedEventArgs e) { }
        private void CalcHistoryList_SelectionChanged(object sender, SelectionChangedEventArgs e) { }
        private void PaintMode_Checked(object sender, RoutedEventArgs e) { }
        private void PaintClear_Click(object sender, RoutedEventArgs e) { }
        private void PaintExport_Click(object sender, RoutedEventArgs e) { }
        private void NotepadNew_Click(object sender, RoutedEventArgs e) { }
        private void NotepadSave_Click(object sender, RoutedEventArgs e) { }
        
        // =====================================================================
        // SANDBOXED FILE EXPLORER LOGIC
        // =====================================================================
        private void InitializeExplorer()
        {
            try
            {
                if (!System.IO.Directory.Exists(_sandboxRoot))
                {
                    System.IO.Directory.CreateDirectory(_sandboxRoot);
                    AddLog($"Created sandbox root: {_sandboxRoot}");
                }
                
                _currentExplorerPath = _sandboxRoot;
                LoadDirectory(_currentExplorerPath);
            }
            catch (Exception ex)
            {
                AddLog($"Explorer Init Error: {ex.Message}");
                System.Windows.MessageBox.Show($"Failed to initialize sandbox storage: {ex.Message}", "Security Error", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Error);
            }
        }

        private void LoadDirectory(string targetPath)
        {
            try
            {
                // CHROOT JAIL VALIDATION
                string fullTarget = System.IO.Path.GetFullPath(targetPath);
                if (!fullTarget.StartsWith(_sandboxRoot, StringComparison.OrdinalIgnoreCase))
                {
                    AddLog($"Blocked path traversal attempt to: {fullTarget}");
                    System.Windows.MessageBox.Show("ACCESS DENIED. Path is outside of allowed sandbox.", "NeX Security Policy", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Warning);
                    return;
                }

                _currentExplorerPath = fullTarget;
                ExplorerPathText.Text = _currentExplorerPath;
                
                var items = new System.Collections.ObjectModel.ObservableCollection<FileItem>();
                
                // Add directories
                foreach (string dir in System.IO.Directory.GetDirectories(_currentExplorerPath))
                {
                    var info = new System.IO.DirectoryInfo(dir);
                    items.Add(new FileItem
                    {
                        Name = info.Name,
                        Path = info.FullName,
                        IsDirectory = true,
                        IconCode = "\uE8D5", // Folder icon
                        IconColor = "#FCD34D", // Folder yellow
                        SizeStr = "",
                        Details = info.LastWriteTime.ToString("yyyy-MM-dd HH:mm")
                    });
                }

                // Add files
                foreach (string file in System.IO.Directory.GetFiles(_currentExplorerPath))
                {
                    var info = new System.IO.FileInfo(file);
                    string ext = info.Extension.ToLower();
                    
                    // Simple icon mapping
                    string icon = "\uE7C3"; // Default file
                    string color = "#9CA3AF";
                    if (ext == ".txt" || ext == ".log") { icon = "\uE8C9"; color = "#60CDFF"; } // Text
                    else if (ext == ".jpg" || ext == ".png" || ext == ".jpeg") { icon = "\uEB9F"; color = "#34D399"; } // Image
                    else if (ext == ".pdf") { icon = "\uEA90"; color = "#F87171"; } // PDF
                    else if (ext == ".exe" || ext == ".bat" || ext == ".cmd" || ext == ".ps1" || ext == ".vbs" || ext == ".msi") { icon = "\uE943"; color = "#F87171"; } // Executable/Script
                    
                    items.Add(new FileItem
                    {
                        Name = info.Name,
                        Path = info.FullName,
                        IsDirectory = false,
                        IconCode = icon,
                        IconColor = color,
                        SizeStr = FormatBytes(info.Length),
                        Details = info.LastWriteTime.ToString("yyyy-MM-dd HH:mm")
                    });
                }

                ExplorerListView.ItemsSource = items;
                UpdateQuota();
            }
            catch (Exception ex)
            {
                AddLog($"Failed to load directory {_currentExplorerPath}: {ex.Message}");
            }
        }

        private string FormatBytes(long bytes)
        {
            if (bytes >= 1073741824) return (bytes / 1073741824.0).ToString("0.##") + " GB";
            if (bytes >= 1048576) return (bytes / 1048576.0).ToString("0.##") + " MB";
            if (bytes >= 1024) return (bytes / 1024.0).ToString("0.##") + " KB";
            return bytes.ToString() + " Bytes";
        }

        private long GetDirectorySize(string folderPath)
        {
            try
            {
                System.IO.DirectoryInfo di = new System.IO.DirectoryInfo(folderPath);
                long size = 0;
                foreach (System.IO.FileInfo fi in di.GetFiles("*.*", System.IO.SearchOption.AllDirectories))
                {
                    size += fi.Length;
                }
                return size;
            }
            catch
            {
                return 0; // Fallback if access denied on deep folders
            }
        }

        private void UpdateQuota()
        {
            long currentSize = GetDirectorySize(_sandboxRoot);
            double currentMb = currentSize / 1048576.0;
            double maxMb = MAX_QUOTA_BYTES / 1048576.0;
            
            ExplorerQuotaText.Text = $"Storage: {currentMb:0.##} MB / {maxMb:0} MB";
            ExplorerQuotaBar.Value = currentSize;
            
            if (currentSize > MAX_QUOTA_BYTES * 0.9)
            {
                ExplorerQuotaBar.Foreground = System.Windows.Media.Brushes.Red;
            }
            else
            {
                ExplorerQuotaBar.Foreground = (System.Windows.Media.Brush)FindResource("AccentColorBrush");
            }
        }

        private void ExplorerBackButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.Equals(_currentExplorerPath.TrimEnd('\\'), _sandboxRoot.TrimEnd('\\'), StringComparison.OrdinalIgnoreCase))
            {
                AddLog("Cannot navigate above sandbox root.");
                return;
            }

            string parent = System.IO.Directory.GetParent(_currentExplorerPath)?.FullName ?? _sandboxRoot;
            LoadDirectory(parent);
        }

        private void ExplorerListView_MouseDoubleClick(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            if (ExplorerListView.SelectedItem is FileItem item)
            {
                if (item.IsDirectory)
                {
                    LoadDirectory(item.Path);
                }
                else
                {
                    // Execution blocking
                    string ext = System.IO.Path.GetExtension(item.Path).ToLower();
                    string[] blockedExts = { ".exe", ".bat", ".cmd", ".ps1", ".vbs", ".msi" };
                    if (System.Linq.Enumerable.Contains(blockedExts, ext))
                    {
                        System.Windows.MessageBox.Show("Execution Blocked by NeX Security Policy.", "Security Block", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Error);
                        AddLog($"Blocked attempt to execute forbidden script/binary: {item.Name}");
                        return;
                    }
                    
                    try
                    {
                        System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo(item.Path) { UseShellExecute = true });
                        AddLog($"Securely launched file via shell: {item.Name}");
                    }
                    catch (Exception ex)
                    {
                        AddLog($"Failed to open file {item.Name}: {ex.Message}");
                    }
                }
            }
        }

        private void ExplorerPaste_Click(object sender, RoutedEventArgs e)
        {
            if (System.Windows.Clipboard.ContainsFileDropList())
            {
                var files = System.Windows.Clipboard.GetFileDropList();
                long currentSize = GetDirectorySize(_sandboxRoot);

                foreach (string file in files)
                {
                    if (System.IO.File.Exists(file))
                    {
                        long fileSize = new System.IO.FileInfo(file).Length;
                        if (currentSize + fileSize > MAX_QUOTA_BYTES)
                        {
                            System.Windows.MessageBox.Show("Cannot paste file. The 1GB storage quota would be exceeded.", "Quota Exceeded", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Error);
                            return;
                        }

                        string dest = System.IO.Path.Combine(_currentExplorerPath, System.IO.Path.GetFileName(file));
                        try
                        {
                            System.IO.File.Copy(file, dest, overwrite: true);
                            currentSize += fileSize;
                        }
                        catch (Exception ex)
                        {
                            AddLog($"Paste failed: {ex.Message}");
                        }
                    }
                }
                LoadDirectory(_currentExplorerPath); // Refresh
            }
        }

        private void ExplorerDelete_Click(object sender, RoutedEventArgs e)
        {
            if (ExplorerListView.SelectedItem is FileItem item)
            {
                try
                {
                    if (item.IsDirectory)
                        System.IO.Directory.Delete(item.Path, true);
                    else
                        System.IO.File.Delete(item.Path);
                        
                    LoadDirectory(_currentExplorerPath); // Refresh
                    AddLog($"Deleted item: {item.Name}");
                }
                catch (Exception ex)
                {
                    System.Windows.MessageBox.Show($"Delete failed: {ex.Message}", "Error", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Error);
                }
            }
        }

        // =====================================================================
        // NEW SANDBOXED EXPLORER FEATURES
        // =====================================================================
        private void ExplorerHomeButton_Click(object sender, RoutedEventArgs e)
        {
            LoadDirectory(_sandboxRoot);
        }

        private void ExplorerNewFolder_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                string newFolderPath = System.IO.Path.Combine(_currentExplorerPath, "New Folder");
                int count = 1;
                while (System.IO.Directory.Exists(newFolderPath))
                {
                    newFolderPath = System.IO.Path.Combine(_currentExplorerPath, $"New Folder ({count})");
                    count++;
                }
                System.IO.Directory.CreateDirectory(newFolderPath);
                LoadDirectory(_currentExplorerPath);
                AddLog($"Created folder: {newFolderPath}");
            }
            catch (Exception ex)
            {
                System.Windows.MessageBox.Show($"Failed to create folder: {ex.Message}", "Error", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Error);
            }
        }

        private FileItem? _itemToRename = null;
        private void ExplorerSetBackground_Click(object sender, RoutedEventArgs e)
        {
            if (ExplorerListView.SelectedItem is FileItem item)
            {
                string ext = System.IO.Path.GetExtension(item.Path).ToLower();
                if (ext == ".jpg" || ext == ".jpeg" || ext == ".png")
                {
                    try
                    {
                        string destPath = @"C:\NeX_Storage\System\active_wallpaper.jpg";
                        if (!System.IO.Directory.Exists(@"C:\NeX_Storage\System"))
                        {
                            System.IO.Directory.CreateDirectory(@"C:\NeX_Storage\System");
                        }
                        System.IO.File.Copy(item.Path, destPath, true);
                        this.Background = new System.Windows.Media.ImageBrush(LoadImageSafely(destPath)) { Stretch = System.Windows.Media.Stretch.UniformToFill };
                        AddLog("Wallpaper updated from Explorer.");
                    }
                    catch (Exception ex)
                    {
                        System.Windows.MessageBox.Show($"Failed to set wallpaper: {ex.Message}", "Error", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Error);
                    }
                }
                else
                {
                    System.Windows.MessageBox.Show("Selected file is not a supported image format.", "Invalid Format", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Warning);
                }
            }
        }

        private void ExplorerRename_Click(object sender, RoutedEventArgs e)
        {
            if (ExplorerListView.SelectedItem is FileItem item)
            {
                _itemToRename = item;
                RenameTextBox.Text = item.Name;
                RenameDialogContainer.Visibility = Visibility.Visible;
                RenameTextBox.Focus();
                RenameTextBox.SelectAll();
            }
        }

        private void RenameCancel_Click(object sender, RoutedEventArgs e)
        {
            RenameDialogContainer.Visibility = Visibility.Collapsed;
            _itemToRename = null;
        }

        private void RenameConfirm_Click(object sender, RoutedEventArgs e)
        {
            if (_itemToRename != null)
            {
                string newName = RenameTextBox.Text.Trim();
                if (!string.IsNullOrEmpty(newName))
                {
                    try
                    {
                        string oldPath = _itemToRename.Path;
                        string parent = System.IO.Path.GetDirectoryName(oldPath) ?? _currentExplorerPath;
                        string newPath = System.IO.Path.Combine(parent, newName);

                        if (_itemToRename.IsDirectory)
                            System.IO.Directory.Move(oldPath, newPath);
                        else
                            System.IO.File.Move(oldPath, newPath);

                        AddLog($"Renamed '{_itemToRename.Name}' to '{newName}'");
                        LoadDirectory(_currentExplorerPath);
                    }
                    catch (Exception ex)
                    {
                        System.Windows.MessageBox.Show($"Rename failed: {ex.Message}", "Error", System.Windows.MessageBoxButton.OK, System.Windows.MessageBoxImage.Error);
                    }
                }
                RenameDialogContainer.Visibility = Visibility.Collapsed;
                _itemToRename = null;
            }
        }

        private bool _isLargeIconView = false;
        private void ExplorerViewMode_Click(object sender, RoutedEventArgs e)
        {
            _isLargeIconView = !_isLargeIconView;
            if (_isLargeIconView)
            {
                FrameworkElementFactory factory = new FrameworkElementFactory(typeof(WrapPanel));
                factory.SetValue(WrapPanel.ItemWidthProperty, 100.0);
                factory.SetValue(WrapPanel.ItemHeightProperty, 100.0);
                ItemsPanelTemplate template = new ItemsPanelTemplate { VisualTree = factory };
                ExplorerListView.ItemsPanel = template;
                
                string xaml = @"<DataTemplate xmlns=""http://schemas.microsoft.com/winfx/2006/xaml/presentation"">
                                    <StackPanel Margin=""8"" Width=""84"" Height=""84"" Background=""Transparent"">
                                        <TextBlock Text=""{Binding IconCode}"" FontFamily=""Segoe Fluent Icons"" FontSize=""40"" Foreground=""{Binding IconColor}"" HorizontalAlignment=""Center"" Margin=""0,0,0,8""/>
                                        <TextBlock Text=""{Binding Name}"" FontSize=""12"" Foreground=""White"" TextAlignment=""Center"" TextWrapping=""Wrap"" MaxHeight=""34"" TextTrimming=""CharacterEllipsis""/>
                                    </StackPanel>
                                </DataTemplate>";
                ExplorerListView.ItemTemplate = (DataTemplate)System.Windows.Markup.XamlReader.Parse(xaml);
            }
            else
            {
                FrameworkElementFactory factory = new FrameworkElementFactory(typeof(VirtualizingStackPanel));
                ItemsPanelTemplate template = new ItemsPanelTemplate { VisualTree = factory };
                ExplorerListView.ItemsPanel = template;

                string xaml = @"<DataTemplate xmlns=""http://schemas.microsoft.com/winfx/2006/xaml/presentation"">
                                    <Border Background=""Transparent"" CornerRadius=""6"" Padding=""8,4"" Margin=""0,2"">
                                        <Grid>
                                            <Grid.ColumnDefinitions>
                                                <ColumnDefinition Width=""40""/>
                                                <ColumnDefinition Width=""*""/>
                                                <ColumnDefinition Width=""100""/>
                                            </Grid.ColumnDefinitions>
                                            <TextBlock Grid.Column=""0"" Text=""{Binding IconCode}"" FontFamily=""Segoe Fluent Icons"" FontSize=""20"" Foreground=""{Binding IconColor}"" VerticalAlignment=""Center"" HorizontalAlignment=""Center""/>
                                            <StackPanel Grid.Column=""1"" VerticalAlignment=""Center"" Margin=""12,0,0,0"">
                                                <TextBlock Text=""{Binding Name}"" FontSize=""13"" Foreground=""#F3F4F6"" FontWeight=""SemiBold""/>
                                                <TextBlock Text=""{Binding Details}"" FontSize=""11"" Foreground=""#9CA3AF"" FontFamily=""Consolas"" Margin=""0,2,0,0""/>
                                            </StackPanel>
                                            <TextBlock Grid.Column=""2"" Text=""{Binding SizeStr}"" FontSize=""11"" Foreground=""#9CA3AF"" FontFamily=""Consolas"" VerticalAlignment=""Center"" HorizontalAlignment=""Right""/>
                                        </Grid>
                                    </Border>
                                </DataTemplate>";
                ExplorerListView.ItemTemplate = (DataTemplate)System.Windows.Markup.XamlReader.Parse(xaml);
            }
        }
    }

    public class FileItem
    {
        public string Name { get; set; } = string.Empty;
        public string Path { get; set; } = string.Empty;
        public bool IsDirectory { get; set; }
        public string IconCode { get; set; } = string.Empty;
        public string IconColor { get; set; } = string.Empty;
        public string SizeStr { get; set; } = string.Empty;
        public string Details { get; set; } = string.Empty;
    }
}
