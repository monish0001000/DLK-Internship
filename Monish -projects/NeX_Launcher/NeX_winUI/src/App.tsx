import React, { useState, useEffect } from 'react';
import {
  Globe,
  FileText,
  Table,
  BookOpen,
  Edit,
  Calculator as CalcIcon,
  Palette,
  FolderOpen,
  Camera as CameraIcon,
  Sliders,
  Settings as SettingsIcon,
  HelpCircle,
  Activity,
  ShieldAlert,
  Search,
  Power,
  Volume2,
  VolumeX,
  Wifi,
  WifiOff,
  Maximize2,
  Minimize2,
  X,
  Terminal as TermIcon,
  FileSpreadsheet,
  Grid,
  CheckCircle,
  Flame,
  User,
  ExternalLink,
  Smartphone,
  ShieldAlert as AlertIcon,
  RefreshCw,
  Compass,
  FileEdit,
  Table2,
  BookOpenCheck,
  StickyNote,
  Paintbrush,
  FolderHeart,
  ScanFace,
  SlidersHorizontal,
  Sun,
  Moon,
  FileCode,
  Sparkles
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

// Types
import { AppID, AppDefinition, VirtualFile, SystemState } from './types';

// App Components
import Calculator from './components/Calculator';
import PaintApp from './components/PaintApp';
import CameraApp from './components/CameraApp';
import EdgeBrowser from './components/EdgeBrowser';
import WordEditor from './components/WordEditor';
import ExcelSpreadsheet from './components/ExcelSpreadsheet';
import PdfViewer from './components/PdfViewer';
import Notepad from './components/Notepad';
import FileExplorer from './components/FileExplorer';
import SettingsApp from './components/SettingsApp';
import WindowsCodeViewer from './components/WindowsCodeViewer';

export default function App() {
  // 1. Storage files state
  const [files, setFiles] = useState<VirtualFile[]>([
    {
      name: 'Lumina_Systems_Specs.doc',
      type: 'doc',
      content: `==================================================
LUMINA SYSTEMS HARDWARE SPECIFICATIONS
==================================================
MODEL: LUM-NEX-01
BUILD REGISTRATION: 2026-07-08T02:27:00
HOST INGRESS GATEWAY: PORT 3000

CPU: Intel Xeon Scalable Core @ 3.4GHz
RAM: 16 GB DDR5 Dedicated
STORAGE: 256 GB Encrypted Kiosk Volume (C:)

SECURE NODE CONFIGURATION: MODE 1 (RESTRICTED)`,
      size: '2.4 KB',
      updatedAt: '07/08/2026',
    },
    {
      name: 'Core_Kiosk_Telemetry.sheet',
      type: 'sheet',
      content: JSON.stringify({
        A1: 'METRIC', B1: 'VALUE', C1: 'THRESHOLD', D1: 'STATUS',
        A2: 'Core Temp', B2: '42', C2: '75', D2: 'STABLE',
        A3: 'Memory Heap', B3: '4.1', C3: '12.0', D3: 'OPTIMAL',
        A4: 'Packet loss', B4: '0.00', C4: '0.05', D4: 'SECURE',
      }),
      size: '1.2 KB',
      updatedAt: '07/08/2026',
    },
    {
      name: 'Lumina_Kiosk_Operator_Manual.pdf',
      type: 'pdf',
      content: 'manual',
      size: '4.8 MB',
      updatedAt: '10/24/2023',
    },
  ]);

  // 2. Telemetry transaction log history
  const [logs, setLogs] = useState<string[]>([
    'Kiosk boot parameters initialized.',
    'Secure proxy server mapped to host PORT 3000.',
    'DNS Filter Shield loaded. Mode 1 restrictions activated.',
    'Device hostname mapped to NEX-WIN-001.',
    'Biometric camera diagnostic... PASS.',
  ]);

  // Adding logs helpers
  const addLog = (msg: string) => {
    const timestamp = new Date().toLocaleTimeString([], { hour12: false });
    setLogs((prev) => [`[${timestamp}] ${msg}`, ...prev].slice(0, 100));
  };

  const clearLogs = () => {
    setLogs([]);
    addLog('System log buffer flushed.');
  };

  // 3. System States
  const [systemState, setSystemState] = useState<SystemState>({
    mode: 'Mode 1',
    isOnline: true,
    isMuted: false,
    volume: 80,
    wifiConnected: true,
    integritySecure: true,
    logs: [],
    theme: 'dark',
  });

  // Bind systemState logs to our active audit array
  useEffect(() => {
    setSystemState((prev) => ({ ...prev, logs }));
  }, [logs]);

  // Synchronize document theme
  useEffect(() => {
    if (systemState.theme === 'light') {
      document.documentElement.classList.add('light');
      document.documentElement.setAttribute('data-theme', 'light');
    } else {
      document.documentElement.classList.remove('light');
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  }, [systemState.theme]);

  // Live network utilization simulation values (pulse slightly)
  const [netBars, setNetBars] = useState<number[]>([60, 80, 40, 90, 70, 20]);
  useEffect(() => {
    const interval = setInterval(() => {
      setNetBars((prev) =>
        prev.map((val) => {
          const delta = Math.floor(Math.random() * 21) - 10; // -10 to +10
          return Math.max(10, Math.min(100, val + delta));
        })
      );
    }, 1200);
    return () => clearInterval(interval);
  }, []);

  // 4. GUI Navigation
  const [activeApp, setActiveApp] = useState<AppID | null>(null);
  const [windowViewMode, setWindowViewMode] = useState<'app' | 'code'>('app');
  const [isStartMenuOpen, setIsStartMenuOpen] = useState(false);
  const [deviceName, setDeviceName] = useState('NEX-WIN-001');
  const [searchTerm, setSearchTerm] = useState('');
  const [isShutdownModalOpen, setIsShutdownModalOpen] = useState(false);
  const [isPowerOffEffect, setIsPowerOffEffect] = useState(false);

  // Auto-reset view mode to 'app' when changing activeApp
  useEffect(() => {
    setWindowViewMode('app');
  }, [activeApp]);

  // Time / Clock state
  const [timeStr, setTimeStr] = useState('14:30');
  const [dateStr, setDateStr] = useState('10/24/2023');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(
        now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })
      );
      setDateStr(
        now.toLocaleDateString([], { month: '2-digit', day: '2-digit', year: 'numeric' })
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Application directory mapping
  const appDefinitions: AppDefinition[] = [
    {
      id: 'edge',
      name: 'Microsoft Edge',
      iconName: 'Compass',
      bgClass: 'bg-indigo-500/10 border border-indigo-500/20',
      iconColorClass: 'text-indigo-600 dark:text-indigo-400',
      description: 'Secure Sandbox Web Browser.',
    },
    {
      id: 'word',
      name: 'Word Processor',
      iconName: 'FileEdit',
      bgClass: 'bg-blue-500/10 border border-blue-500/20',
      iconColorClass: 'text-blue-600 dark:text-blue-400',
      description: 'Simulated Word Processor.',
    },
    {
      id: 'excel',
      name: 'Excel Sheet',
      iconName: 'Table2',
      bgClass: 'bg-emerald-500/10 border border-emerald-500/20',
      iconColorClass: 'text-emerald-600 dark:text-emerald-400',
      description: 'Simulated Spreadsheet Workspace.',
    },
    {
      id: 'pdf',
      name: 'PDF Reader',
      iconName: 'BookOpenCheck',
      bgClass: 'bg-rose-500/10 border border-rose-500/20',
      iconColorClass: 'text-rose-600 dark:text-rose-400',
      description: 'Read Manuals and system policies.',
    },
    {
      id: 'notepad',
      name: 'Notepad',
      iconName: 'StickyNote',
      bgClass: 'bg-amber-500/10 border border-amber-500/20',
      iconColorClass: 'text-amber-600 dark:text-amber-400',
      description: 'Plaintext logs scratchpad.',
    },
    {
      id: 'calculator',
      name: 'Calculator',
      iconName: 'CalcIcon',
      bgClass: 'bg-orange-500/10 border border-orange-500/20',
      iconColorClass: 'text-orange-600 dark:text-orange-400',
      description: 'Standard diagnostic calculator.',
    },
    {
      id: 'paint',
      name: 'Paint Canvas',
      iconName: 'Paintbrush',
      bgClass: 'bg-fuchsia-500/10 border border-fuchsia-500/20',
      iconColorClass: 'text-fuchsia-600 dark:text-fuchsia-400',
      description: 'Sketch and map board simulator.',
    },
    {
      id: 'files',
      name: 'File Explorer',
      iconName: 'FolderHeart',
      bgClass: 'bg-yellow-500/10 border border-yellow-500/20',
      iconColorClass: 'text-yellow-600 dark:text-yellow-400',
      description: 'Access secure file nodes.',
    },
    {
      id: 'camera',
      name: 'Camera',
      iconName: 'CameraIcon',
      bgClass: 'bg-cyan-500/10 border border-cyan-500/20',
      iconColorClass: 'text-cyan-600 dark:text-cyan-400',
      description: 'Capture snapshots and control camera video feeds.',
    },
    {
      id: 'settings',
      name: 'Settings',
      iconName: 'SlidersHorizontal',
      bgClass: 'bg-slate-500/10 border border-slate-500/20',
      iconColorClass: 'text-slate-600 dark:text-slate-400',
      description: 'Workstation configs and logs.',
    },
  ];

  // Helper mapping icon key to Lucide Component
  const renderAppIcon = (iconName: string, size = 32, className = '') => {
    switch (iconName) {
      case 'Compass': return <Compass size={size} className={className} />;
      case 'FileEdit': return <FileEdit size={size} className={className} />;
      case 'Table2': return <Table2 size={size} className={className} />;
      case 'BookOpenCheck': return <BookOpenCheck size={size} className={className} />;
      case 'StickyNote': return <StickyNote size={size} className={className} />;
      case 'CalcIcon': return <CalcIcon size={size} className={className} />;
      case 'Paintbrush': return <Paintbrush size={size} className={className} />;
      case 'FolderHeart': return <FolderHeart size={size} className={className} />;
      case 'ScanFace': return <ScanFace size={size} className={className} />;
      case 'CameraIcon': return <CameraIcon size={size} className={className} />;
      case 'SlidersHorizontal': return <SlidersHorizontal size={size} className={className} />;
      default: return <Grid size={size} className={className} />;
    }
  };

  // 5. File Explorer Operations
  const handleSaveFile = (name: string, type: 'doc' | 'sheet' | 'pdf' | 'text' | 'image', content: string) => {
    const existingIndex = files.findIndex((f) => f.name.toLowerCase() === name.toLowerCase());

    const formattedSize =
      content.length > 1024
        ? `${(content.length / 1024).toFixed(1)} KB`
        : `${content.length} B`;

    const newFile: VirtualFile = {
      name,
      type,
      content,
      size: formattedSize,
      updatedAt: new Date().toLocaleDateString(),
    };

    if (existingIndex > -1) {
      const updated = [...files];
      updated[existingIndex] = newFile;
      setFiles(updated);
    } else {
      setFiles((prev) => [...prev, newFile]);
    }
  };

  const handleDeleteFile = (name: string) => {
    setFiles((prev) => prev.filter((f) => f.name !== name));
    addLog(`Deleted file: ${name}`);
  };

  const handleOpenFile = (file: VirtualFile) => {
    addLog(`Launching file node: ${file.name}`);
    if (file.type === 'doc') {
      setActiveApp('word');
    } else if (file.type === 'sheet') {
      setActiveApp('excel');
    } else if (file.type === 'pdf') {
      setActiveApp('pdf');
    } else if (file.type === 'text') {
      setActiveApp('notepad');
    } else if (file.type === 'image') {
      // Images can be previewed directly or open paint
      setActiveApp('paint');
    }
    setIsStartMenuOpen(false);
  };

  // Toggle States
  const toggleMute = () => {
    setSystemState((prev) => {
      const nextMute = !prev.isMuted;
      addLog(nextMute ? 'System audio muted.' : 'System audio restored.');
      return { ...prev, isMuted: nextMute };
    });
  };

  const toggleWifi = () => {
    setSystemState((prev) => {
      const nextWifi = !prev.wifiConnected;
      addLog(nextWifi ? 'Wireless link established.' : 'Wireless link terminated.');
      return { ...prev, wifiConnected: nextWifi, isOnline: nextWifi };
    });
  };

  // Power controls
  const handlePowerAction = (action: 'restart' | 'shutdown' | 'lock') => {
    setIsShutdownModalOpen(false);
    setIsStartMenuOpen(false);
    
    if (action === 'shutdown') {
      addLog('Initiating secure system container teardown...');
      setIsPowerOffEffect(true);
    } else if (action === 'restart') {
      addLog('Rebooting secure system sandbox hypervisor...');
      setIsPowerOffEffect(true);
      setTimeout(() => {
        setIsPowerOffEffect(false);
        setActiveApp(null);
        setLogs([
          'Kiosk boot parameters re-initialized.',
          'Secure proxy server recovered standard PORT 3000.',
          'DNS Filter Shield reloaded. Mode 1 restrictions activated.',
          `Device hostname recovered: ${deviceName}.`,
          'Self-recovering memory heap is flushed and clean.',
        ]);
      }, 3000);
    } else {
      addLog('Kiosk screen locked.');
      alert('Kiosk is locked. Under sandboxed mode, click OK to resume operation instantly.');
    }
  };

  return (
    <div className="bg-surface-dim text-on-surface h-screen flex flex-col relative select-none font-sans overflow-hidden bg-[radial-gradient(circle_at_top_right,rgba(59,130,246,0.06),transparent_50%),radial-gradient(circle_at_bottom_left,rgba(168,85,247,0.04),transparent_50%)]">
      {/* Power Off/Terminal Sweep Screen Overlay */}
      <AnimatePresence>
        {isPowerOffEffect && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="absolute inset-0 bg-[#000000] z-[9999] flex flex-col items-center justify-center font-mono text-xs text-primary p-6"
          >
            <div className="w-full max-w-md space-y-2 text-left">
              <p className="text-secondary font-bold">LUMINA HARDENED SYSTEM OS v4.2 [TEARDOWN]</p>
              <div className="h-[1px] bg-white/20 my-2"></div>
              <p className="animate-pulse">FLUSHING EPHEMERAL INGRESS MEMORY...</p>
              <p>✔ Flushed RAM partition (C:)</p>
              <p>✔ Discharged video biometric modules</p>
              <p>✔ Dissolved DNS Secure proxy channels</p>
              <p>✔ Terminated container daemon</p>
              <p className="text-tertiary mt-4">✔ REBOOT SECURE CORE READY // WAITING FOR INITIALIZATION...</p>
              <div className="flex items-center gap-2 mt-4 text-on-surface-variant">
                <RefreshCw size={14} className="animate-spin text-primary" />
                <span>Restoring pristine sandboxed states in 3 seconds...</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Shutdown Modal Confirmation */}
      <AnimatePresence>
        {isShutdownModalOpen && (
          <div className="absolute inset-0 bg-black/65 backdrop-blur-sm z-[999] flex items-center justify-center">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="glass-panel p-6 rounded-2xl w-full max-w-sm text-center space-y-4 shadow-2xl relative border border-white/10"
            >
              <div className="w-12 h-12 rounded-full bg-error-container/10 border border-error-container/20 text-error flex items-center justify-center mx-auto mb-2">
                <Power size={24} />
              </div>
              <h3 className="text-sm font-semibold text-white">Power Workstation Options</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Choose a power option to control the secure Lumina Kiosk terminal environment.
              </p>

              <div className="grid grid-cols-3 gap-2 pt-2">
                <button
                  onClick={() => handlePowerAction('restart')}
                  className="p-2.5 bg-white/5 hover:bg-white/10 border border-white/10 hover:text-white rounded-lg text-xs transition-all cursor-pointer font-semibold"
                  id="power-restart"
                >
                  Restart
                </button>
                <button
                  onClick={() => handlePowerAction('lock')}
                  className="p-2.5 bg-white/5 hover:bg-white/10 border border-white/10 hover:text-white rounded-lg text-xs transition-all cursor-pointer font-semibold"
                  id="power-lock"
                >
                  Lock
                </button>
                <button
                  onClick={() => handlePowerAction('shutdown')}
                  className="p-2.5 bg-error-container/20 hover:bg-error-container/30 border border-error/20 text-error hover:text-white rounded-lg text-xs transition-all cursor-pointer font-bold"
                  id="power-shutdown"
                >
                  Shutdown
                </button>
              </div>

              <button
                onClick={() => setIsShutdownModalOpen(false)}
                className="w-full py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs font-semibold text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer border border-white/5 mt-2"
                id="power-cancel"
              >
                Cancel
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Dynamic Ambient Background Shader Effect */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(180,228,255,0.025)_0%,transparent_50%)] pointer-events-none" />

      {/* TopAppBar */}
      <header
        className="flex justify-between items-center w-full px-10 h-16 backdrop-blur-[40px] border-b border-black/10 dark:border-white/10 z-20 shrink-0"
        style={{ background: 'var(--header-bg)' }}
      >
        <div className="flex flex-col text-left select-none cursor-pointer" onClick={() => { setActiveApp(null); setIsStartMenuOpen(false); }}>
          <h1 className="text-sm font-semibold tracking-wide text-on-surface">System Terminal</h1>
          <p className="text-[10px] font-mono text-on-surface-variant opacity-70 mt-0.5 uppercase tracking-wider">
            Lumina Dashboard v4.2
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              setActiveApp('settings');
              setIsStartMenuOpen(false);
            }}
            className={`p-2 rounded-full hover:bg-white/5 transition-colors text-on-surface-variant ${
              activeApp === 'settings' ? 'text-primary bg-primary/10' : ''
            }`}
            title="System Settings"
            id="topbar-settings"
          >
            <SettingsIcon size={18} />
          </button>
          <button
            onClick={() => {
              setActiveApp('pdf');
              setIsStartMenuOpen(false);
            }}
            className={`p-2 rounded-full hover:bg-white/5 transition-colors text-on-surface-variant ${
              activeApp === 'pdf' ? 'text-primary bg-primary/10' : ''
            }`}
            title="Operator Help Guide"
            id="topbar-help"
          >
            <HelpCircle size={18} />
          </button>
        </div>
      </header>

      {/* Main Area */}
      <main className="flex-1 flex overflow-hidden relative">
        {/* Content Canvas */}
        <section className="flex-1 p-10 overflow-y-auto custom-scrollbar relative flex flex-col min-w-0">
          <AnimatePresence mode="wait">
            {activeApp === null ? (
              /* Desktop Grid Mode */
              <motion.div
                key="desktop"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="flex-1 flex flex-col justify-center max-w-6xl mx-auto w-full py-8 px-4"
              >
                {/* Header Section */}
                <div className="mb-8 text-left">
                  <h2 className="text-3xl font-semibold text-primary tracking-tight mb-2 font-sans select-none">
                    Welcome
                  </h2>
                  <div className="flex items-center gap-2 px-3 py-1 bg-primary/10 border border-primary/20 rounded-full w-fit">
                    <CheckCircle className="text-primary" size={13} />
                    <p className="text-[11px] font-semibold text-primary">
                      You are in Mode 1. Only allowed applications are available.
                    </p>
                  </div>
                </div>

                {/* Application Bento Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-6">
                  {appDefinitions.map((app) => (
                    <button
                      key={app.id}
                      onClick={() => {
                        setActiveApp(app.id);
                        addLog(`Laid shell focus onto module: ${app.name}`);
                      }}
                      className="acrylic-card p-6 rounded-2xl flex flex-col items-center justify-center gap-4 group cursor-pointer"
                      id={`app-launcher-${app.id}`}
                    >
                      <div
                        className={`w-16 h-16 rounded-2xl ${app.bgClass} flex items-center justify-center border border-black/5 dark:border-white/5 group-hover:scale-110 transition-transform duration-300 shadow-lg`}
                      >
                        {renderAppIcon(app.iconName, 28, app.iconColorClass)}
                      </div>
                      <span className="text-xs font-semibold text-on-surface group-hover:text-primary transition-colors">
                        {app.name}
                      </span>
                    </button>
                  ))}
                </div>
              </motion.div>
            ) : (
              /* Active App Sandbox Frame */
              <motion.div
                key="app-frame"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.2, ease: 'easeOut' }}
                className="flex-1 flex flex-col bg-surface-container/60 border border-black/10 dark:border-white/10 rounded-2xl overflow-hidden glass-panel shadow-2xl"
              >
                {/* Window Header Titlebar */}
                <div className="flex items-center justify-between px-4 h-12 bg-surface-container-highest/60 border-b border-black/5 dark:border-white/5 select-none shrink-0">
                  <div className="flex items-center gap-2.5">
                    <div className="p-1.5 rounded-lg bg-black/5 dark:bg-white/5">
                      {renderAppIcon(
                        appDefinitions.find((a) => a.id === activeApp)?.iconName || '',
                        14,
                        appDefinitions.find((a) => a.id === activeApp)?.iconColorClass
                      )}
                    </div>
                    <span className="text-[11px] font-bold text-on-surface uppercase tracking-wider font-mono">
                      {appDefinitions.find((a) => a.id === activeApp)?.name}
                    </span>
                  </div>

                  {/* Mode Toggles: Live Application vs XAML + C# Code */}
                  <div className="flex items-center bg-black/10 dark:bg-black/30 p-0.5 rounded-lg border border-black/5 dark:border-white/5 mx-2">
                    <button
                      onClick={() => setWindowViewMode('app')}
                      className={`px-3 py-1 text-[11px] font-sans font-semibold rounded-md transition-all flex items-center gap-1.5 cursor-pointer ${
                        windowViewMode === 'app'
                          ? 'bg-primary/20 text-primary shadow-sm font-bold'
                          : 'text-on-surface-variant hover:text-on-surface'
                      }`}
                      id="view-mode-app"
                    >
                      <Sparkles size={11} className={windowViewMode === 'app' ? 'text-primary' : 'text-on-surface-variant'} />
                      <span>Live App</span>
                    </button>
                    <button
                      onClick={() => {
                        setWindowViewMode('code');
                        addLog(`Opened XAML + C# source workspace for: ${appDefinitions.find((a) => a.id === activeApp)?.name}`);
                      }}
                      className={`px-3 py-1 text-[11px] font-sans font-semibold rounded-md transition-all flex items-center gap-1.5 cursor-pointer ${
                        windowViewMode === 'code'
                          ? 'bg-primary/20 text-primary shadow-sm font-bold'
                          : 'text-on-surface-variant hover:text-on-surface'
                      }`}
                      id="view-mode-code"
                    >
                      <FileCode size={11} className={windowViewMode === 'code' ? 'text-primary' : 'text-on-surface-variant'} />
                      <span>XAML + C# Code</span>
                    </button>
                  </div>

                  {/* Window Actions */}
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => {
                        setActiveApp(null);
                        addLog('Minimized current window workspace.');
                      }}
                      className="p-1.5 hover:bg-white/5 text-on-surface-variant hover:text-white rounded"
                      title="Minimize Workspace"
                      id="app-frame-minimize"
                    >
                      <Minimize2 size={12} />
                    </button>
                    <button
                      className="p-1.5 hover:bg-white/5 text-on-surface-variant hover:text-white rounded opacity-40 cursor-not-allowed"
                      title="Toggle Maximize (Fixed Aspect)"
                      disabled
                    >
                      <Maximize2 size={12} />
                    </button>
                    <div className="w-[1px] h-3 bg-white/10 mx-1"></div>
                    <button
                      onClick={() => {
                        setActiveApp(null);
                        addLog(`Closed active module: ${activeApp}`);
                      }}
                      className="p-1.5 hover:bg-error-container/30 text-on-surface-variant hover:text-error rounded transition-colors"
                      title="Term Session"
                      id="app-frame-close"
                    >
                      <X size={12} />
                    </button>
                  </div>
                </div>

                {/* Window Container Body (Render appropriate app component or IDE view) */}
                <div className="flex-1 p-5 min-h-0 bg-surface-dim/40 overflow-y-auto custom-scrollbar">
                  {windowViewMode === 'code' ? (
                    <WindowsCodeViewer activeApp={activeApp || ''} addLog={addLog} />
                  ) : (
                    <>
                      {activeApp === 'calculator' && <Calculator />}
                      {activeApp === 'paint' && <PaintApp onSaveFile={handleSaveFile} />}
                      {activeApp === 'camera' && <CameraApp onSaveFile={handleSaveFile} addLog={addLog} />}
                      {activeApp === 'edge' && <EdgeBrowser addLog={addLog} />}
                      {activeApp === 'word' && <WordEditor onSaveFile={handleSaveFile} addLog={addLog} />}
                      {activeApp === 'excel' && <ExcelSpreadsheet onSaveFile={handleSaveFile} addLog={addLog} />}
                      {activeApp === 'pdf' && <PdfViewer addLog={addLog} />}
                      {activeApp === 'notepad' && <Notepad onSaveFile={handleSaveFile} addLog={addLog} />}
                      {activeApp === 'files' && (
                        <FileExplorer files={files} onOpenFile={handleOpenFile} onDeleteFile={handleDeleteFile} />
                      )}
                      {activeApp === 'settings' && (
                        <SettingsApp
                          systemState={systemState}
                          onUpdateState={(updates) => setSystemState((prev) => ({ ...prev, ...updates }))}
                          deviceName={deviceName}
                          onChangeDeviceName={setDeviceName}
                          addLog={addLog}
                          clearLogs={clearLogs}
                          netBars={netBars}
                        />
                      )}
                    </>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </section>
      </main>

      {/* Start Menu Popup */}
      <AnimatePresence>
        {isStartMenuOpen && (
          <div className="absolute inset-x-0 bottom-16 top-0 z-[100]" onClick={() => setIsStartMenuOpen(false)}>
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 15 }}
              transition={{ duration: 0.15 }}
              onClick={(e) => e.stopPropagation()} // Prevent click away from closing immediately
              className="absolute bottom-2 left-6 glass-panel p-5 rounded-2xl w-80 shadow-2xl flex flex-col gap-4 border border-black/10 dark:border-white/10 overflow-hidden text-left"
            >
              {/* Profile Block */}
              <div className="flex items-center gap-3 border-b border-black/5 dark:border-white/5 pb-3">
                <div className="w-9 h-9 rounded-full bg-primary text-on-primary flex items-center justify-center">
                  <User size={16} />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-on-surface">OPERATOR</h4>
                  <p className="text-[9px] font-mono text-on-surface-variant opacity-60">Status: Secure Session</p>
                </div>
              </div>

              {/* Start search bar */}
              <div className="flex items-center bg-black/5 dark:bg-black/20 rounded-lg border border-black/10 dark:border-white/5 px-2.5 py-1.5 gap-2">
                <Search size={12} className="text-on-surface-variant opacity-60" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Type to filter apps..."
                  className="bg-transparent border-0 outline-none text-xs text-on-surface w-full p-0 font-mono"
                  id="start-menu-search"
                />
              </div>

              {/* Search filtered apps */}
              <div className="space-y-1 max-h-48 overflow-y-auto custom-scrollbar">
                {appDefinitions
                  .filter((a) => a.name.toLowerCase().includes(searchTerm.toLowerCase()))
                  .map((app) => (
                    <button
                      key={app.id}
                      onClick={() => {
                        setActiveApp(app.id);
                        setIsStartMenuOpen(false);
                        addLog(`Start Menu executed application: ${app.name}`);
                      }}
                      className="w-full text-left p-2 hover:bg-black/5 dark:hover:bg-white/5 hover:text-on-surface rounded-lg text-xs flex items-center gap-2.5 transition-colors cursor-pointer"
                      id={`start-app-${app.id}`}
                    >
                      <div className="p-1.5 rounded bg-black/5 dark:bg-white/5">
                        {renderAppIcon(app.iconName, 12, app.iconColorClass)}
                      </div>
                      <div className="truncate text-on-surface">
                        <p className="font-semibold leading-none">{app.name}</p>
                        <span className="text-[9px] text-on-surface-variant opacity-50 mt-0.5 block truncate">
                          {app.description}
                        </span>
                      </div>
                    </button>
                  ))}
              </div>

              {/* Shutdown Tray */}
              <div className="flex justify-between items-center border-t border-black/10 dark:border-white/5 pt-3 mt-1 shrink-0">
                <div className="flex items-center gap-1.5 text-[9px] font-mono text-on-surface-variant opacity-50">
                  <Flame size={10} className="text-primary" />
                  <span>Kiosk Host v4.2</span>
                </div>

                <button
                  onClick={() => setIsShutdownModalOpen(true)}
                  className="flex items-center justify-center w-8 h-8 rounded-lg hover:bg-error-container/20 hover:text-error text-on-surface-variant transition-all cursor-pointer"
                  title="Shut Down options"
                  id="start-power-btn"
                >
                  <Power size={14} />
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* BottomNavBar (Taskbar) */}
      <footer
        className="w-full h-16 backdrop-blur-[40px] border-t border-black/10 dark:border-white/10 z-50 flex items-center justify-between px-10 shrink-0"
        style={{ background: 'var(--taskbar-bg)' }}
      >
        {/* Start Button Section */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => setIsStartMenuOpen(!isStartMenuOpen)}
            className={`relative flex items-center justify-center w-11 h-11 rounded-xl transition-all duration-300 cursor-pointer overflow-hidden group border border-black/10 dark:border-white/10 ${
              isStartMenuOpen
                ? 'bg-primary/20 border-primary/40 shadow-[0_0_15px_rgba(96,205,255,0.4)] scale-95'
                : 'bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 hover:border-black/20 dark:hover:border-white/20 hover:scale-105 active:scale-95'
            }`}
            title="Start Menu"
            id="taskbar-start-btn"
          >
            {/* Glossy glass sheen */}
            <div className="absolute inset-0 bg-gradient-to-b from-white/15 to-transparent pointer-events-none" />

            {/* Modern multi-colored gradient Infinity loop with hover-rotate, scale, and glowing effects */}
            <svg
              viewBox="0 0 24 24"
              fill="none"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="w-[22px] h-[22px] relative z-10 transition-all duration-500 group-hover:rotate-[360deg] group-hover:scale-110"
              id="start-button-infinity-svg"
            >
              <defs>
                <linearGradient id="infinity-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#00adef" />
                  <stop offset="35%" stopColor="#7fba00" />
                  <stop offset="70%" stopColor="#ffb900" />
                  <stop offset="100%" stopColor="#f25022" />
                </linearGradient>
              </defs>
              <path
                d="M12 12c-2-2.67-4-4-6-4a4 4 0 1 0 0 8c2 0 4-1.33 6-4Zm0 0c2 2.67 4 4 6 4a4 4 0 1 0 0-8c-2 0-4 1.33-6 4Z"
                stroke="url(#infinity-gradient)"
                className="drop-shadow-[0_0_4px_rgba(0,173,239,0.4)]"
              />
            </svg>

            {/* Radiant ambient background focus ring */}
            <div className={`absolute inset-0 transition-opacity duration-300 ${
              isStartMenuOpen ? 'bg-primary/10 opacity-100' : 'bg-primary/5 opacity-0 group-hover:opacity-100'
            }`} />
          </button>

          <div className="h-6 w-[1px] bg-black/10 dark:bg-white/10" />

          {/* Persistent Workspace Indicators */}
          <nav className="flex gap-6">
            <div
              onClick={() => {
                setActiveApp(null);
                setIsStartMenuOpen(false);
              }}
              className="flex items-center justify-center relative group cursor-pointer"
              title="Show Desktop Grid"
              id="taskbar-nav-desktop"
            >
              <Smartphone
                size={18}
                className={`transition-colors group-hover:scale-110 duration-200 ${
                  activeApp === null ? 'text-primary' : 'text-on-surface-variant hover:text-on-surface'
                }`}
              />
              {activeApp === null && (
                <div className="absolute -bottom-4 w-6 h-1 bg-primary rounded-full" />
              )}
            </div>

            <div
              onClick={() => {
                setActiveApp('settings');
                setIsStartMenuOpen(false);
              }}
              className="flex items-center justify-center relative group cursor-pointer"
              title="Telemetry Terminal Console"
              id="taskbar-nav-terminal"
            >
              <TermIcon
                size={18}
                className={`transition-colors group-hover:scale-110 duration-200 ${
                  activeApp === 'settings' ? 'text-primary' : 'text-on-surface-variant hover:text-on-surface'
                }`}
              />
              {activeApp === 'settings' && (
                <div className="absolute -bottom-4 w-6 h-1 bg-primary rounded-full" />
              )}
            </div>

            <div
              onClick={() => {
                setActiveApp('files');
                setIsStartMenuOpen(false);
              }}
              className="flex items-center justify-center relative group cursor-pointer"
              title="Secure Storage Logs"
              id="taskbar-nav-files"
            >
              <FolderOpen
                size={18}
                className={`transition-colors group-hover:scale-110 duration-200 ${
                  activeApp === 'files' ? 'text-primary' : 'text-on-surface-variant hover:text-on-surface'
                }`}
              />
              {activeApp === 'files' && (
                <div className="absolute -bottom-4 w-6 h-1 bg-primary rounded-full" />
              )}
            </div>
          </nav>
        </div>

        {/* System Tray */}
        <div className="flex items-center gap-4 text-on-surface">
          <div className="flex items-center gap-4 bg-black/5 dark:bg-white/5 px-4 py-1.5 rounded-full border border-black/5 dark:border-white/5 text-[10px] select-none font-mono">
            {/* Keyboard layout */}
            <span className="text-on-surface-variant font-bold tracking-wide">ENG</span>

            {/* Mute toggle button */}
            <button
              onClick={toggleMute}
              className="text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer"
              title="Toggle Audio Mute"
              id="taskbar-sound-btn"
            >
              {systemState.isMuted ? (
                <VolumeX size={15} className="text-error" />
              ) : (
                <Volume2 size={15} />
              )}
            </button>

            {/* Wireless signal link toggle */}
            <button
              onClick={toggleWifi}
              className="transition-colors cursor-pointer text-on-surface-variant"
              title="Toggle Wireless Network Link"
              id="taskbar-wifi-btn"
            >
              {systemState.wifiConnected ? (
                <Wifi size={15} className="text-tertiary animate-pulse" />
              ) : (
                <WifiOff size={15} className="text-error" />
              )}
            </button>

            {/* Live Clock Tray */}
            <div className="flex flex-col items-end select-text">
              <span className="font-bold text-on-surface leading-none tracking-wide text-xs">
                {timeStr}
              </span>
              <span className="text-[9px] text-on-surface-variant leading-none mt-0.5 select-all">
                {dateStr}
              </span>
            </div>
          </div>

          {/* Quick Power Modal trigger */}
          <button
            onClick={() => setIsShutdownModalOpen(true)}
            className="flex items-center justify-center w-10 h-10 rounded-lg hover:bg-error-container/20 text-error transition-all group cursor-pointer"
            title="Kiosk Power Options"
            id="taskbar-power-btn"
          >
            <Power className="group-hover:rotate-12 transition-transform" size={18} />
          </button>
        </div>
      </footer>
    </div>
  );
}
