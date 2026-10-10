# 🚀 NeX_Launcher - Hardened Enterprise Kiosk Platform

A high-security, custom Windows Kiosk Shell built with **C# and .NET 8.0 WPF**. Engineered to restrict unauthorized Windows system utilities, sandbox local execution, and synchronize endpoint policies with Firebase Realtime Database in real time.

---

## 📌 Architecture & Features

1. **Sandboxed Shell Replacement**:
   - Custom WPF desktop interface replacing standard unmanaged user environments.
   - Enforces execution boundaries within `C:\NeX_Storage` (`Downloads`, `System`, `Wallpapers`).
   - Prevents unauthorized access to native command shells (`cmd`, `powershell`, `regedit`).

2. **Dynamic Application Discovery**:
   - Monitors `C:\NeX_Storage\Downloads` for authorized executable payloads.
   - Automatically generates desktop shortcuts with state management (Active, Blocked, Disabled).

3. **Cloud-Managed MDM Policy Synchronization**:
   - Uses `FirebaseSyncManager` to listen for remote policy triggers.
   - **Default Mode**: Standard access to designated applications.
   - **Lockdown Mode**: High-priority blackout security overlay with administrative override authentication.
   - Remote app installation and remote revocation/kill commands.

4. **Integrated Defensive Tools**:
   - Built-in sandboxed apps: Edge Browser, Settings & Diagnostics, Secure Storage Sandbox, DataSheet, Document Editor, and Media Hub.
   - Comprehensive audit logging written to `C:\NeX_Storage\System\Crash_Log.txt`.

---

## 🛠️ Build & Run Instructions

### Prerequisites
- Windows 10/11 (x64)
- Microsoft .NET 8.0 SDK (`dotnet --version` $\ge$ 8.0)

### 1. Build the Project
```powershell
cd "D:\project\DLK\Monish -projects\NeX_Launcher"
dotnet build NeX_Launcher.csproj -c Debug
```

### 2. Run the Application
```powershell
Start-Process -FilePath "bin\Debug\net8.0-windows\NeX_Launcher_v1.exe"
```

---

## 📂 Project Directory Structure

```
NeX_Launcher/
├── App.xaml / App.xaml.cs            # WPF Application lifecycle & exception handlers
├── MainWindow.xaml / .xaml.cs        # Primary kiosk desktop UI & taskbar shell
├── NeX_Launcher.csproj               # .NET 8.0 Windows WPF project definition
├── app.manifest                      # Execution privileges & DPI awareness
├── Deployment/
│   ├── KioskDeployer.cs              # Script execution and AppLocker policy integration
│   └── SignatureValidator.cs         # X.509 code signing certificate verification
├── NeX_winlogic/
│   ├── Hooks/KeyboardHook.cs         # Win32 low-level keyboard filter
│   └── Services/
│       ├── FirebaseSyncManager.cs    # Realtime cloud policy listener & heartbeat
│       └── ProcessWatcher.cs         # Background process monitoring & enforcement
├── State/
│   └── FirebaseStateManager.cs       # Reactive Firebase client
├── wallpaper/                        # Cyberpunk desktop backgrounds
└── Test report monish/               # Diagnostic test reports
```

---

## 👤 Author
- **Monish** - Cybersecurity & Systems Engineering Intern, DLK Career Solutions.
