import React, { useState, useEffect } from 'react';
import {
  Sliders,
  ShieldCheck,
  Play,
  Terminal,
  Trash2,
  FileOutput,
  Check,
  Cpu,
  RefreshCw,
  Sun,
  Moon,
  ShieldAlert,
  Activity,
  Wifi,
  HardDrive
} from 'lucide-react';
import { SystemState } from '../types';

interface SettingsAppProps {
  systemState: SystemState;
  onUpdateState: (updates: Partial<SystemState>) => void;
  deviceName: string;
  onChangeDeviceName: (name: string) => void;
  addLog: (msg: string) => void;
  clearLogs: () => void;
  netBars: number[];
}

export default function SettingsApp({
  systemState,
  onUpdateState,
  deviceName,
  onChangeDeviceName,
  addLog,
  clearLogs,
  netBars,
}: SettingsAppProps) {
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanStatus, setScanStatus] = useState<'idle' | 'scanning' | 'passed'>('idle');
  const [activeTab, setActiveTab] = useState<'kiosk' | 'telemetry' | 'logs' | 'about'>('kiosk');
  const [exportSuccess, setExportSuccess] = useState(false);

  // Handle simulated integrity scan
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isScanning) {
      timer = setInterval(() => {
        setScanProgress((prev) => {
          if (prev >= 100) {
            clearInterval(timer);
            setIsScanning(false);
            setScanStatus('passed');
            addLog('Manual System Integrity Scan completed: SECURE');
            onUpdateState({ integritySecure: true });
            return 100;
          }
          return prev + 5;
        });
      }, 100);
    }
    return () => clearInterval(timer);
  }, [isScanning]);

  const handleStartScan = () => {
    setScanProgress(0);
    setIsScanning(true);
    setScanStatus('scanning');
    addLog('Manual System Integrity Scan initiated...');
  };

  const handleModeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const nextMode = e.target.value as 'Mode 1' | 'Mode 2' | 'Admin Mode';
    onUpdateState({ mode: nextMode });
    addLog(`Kiosk authorization state shifted to: ${nextMode}`);
  };

  const handleExportLogs = () => {
    setExportSuccess(true);
    addLog('System transaction audits exported successfully.');
    setTimeout(() => setExportSuccess(false), 2000);
  };

  const toggleTheme = () => {
    const nextTheme = systemState.theme === 'light' ? 'dark' : 'light';
    onUpdateState({ theme: nextTheme });
    addLog(`System workspace theme shifted to: ${nextTheme.toUpperCase()}`);
  };

  return (
    <div className="flex flex-col md:flex-row h-full gap-4 text-on-surface">
      {/* Sub tabs & Theme Toggle */}
      <div className="w-full md:w-56 p-4 bg-surface-container/40 rounded-xl border border-black/10 dark:border-white/5 flex flex-col gap-1.5 justify-between">
        <div className="space-y-1.5">
          <h3 className="text-xs font-semibold opacity-70 uppercase tracking-wider mb-2">Settings Category</h3>
          
          <button
            onClick={() => setActiveTab('kiosk')}
            className={`w-full text-left p-2.5 rounded-lg text-xs flex items-center gap-2.5 transition-all cursor-pointer ${
              activeTab === 'kiosk'
                ? 'bg-primary/10 text-primary border border-primary/20 font-semibold'
                : 'bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 text-on-surface-variant hover:bg-black/10 dark:hover:bg-white/10'
            }`}
            id="settings-tab-kiosk"
          >
            <Sliders size={14} />
            <span>Kiosk Dashboard</span>
          </button>

          <button
            onClick={() => setActiveTab('telemetry')}
            className={`w-full text-left p-2.5 rounded-lg text-xs flex items-center gap-2.5 transition-all cursor-pointer ${
              activeTab === 'telemetry'
                ? 'bg-primary/10 text-primary border border-primary/20 font-semibold'
                : 'bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 text-on-surface-variant hover:bg-black/10 dark:hover:bg-white/10'
            }`}
            id="settings-tab-telemetry"
          >
            <Activity size={14} />
            <span>System Telemetry</span>
          </button>

          <button
            onClick={() => setActiveTab('logs')}
            className={`w-full text-left p-2.5 rounded-lg text-xs flex items-center gap-2.5 transition-all cursor-pointer ${
              activeTab === 'logs'
                ? 'bg-primary/10 text-primary border border-primary/20 font-semibold'
                : 'bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 text-on-surface-variant hover:bg-black/10 dark:hover:bg-white/10'
            }`}
            id="settings-tab-logs"
          >
            <Terminal size={14} />
            <span>Audit Logs</span>
          </button>

          <button
            onClick={() => setActiveTab('about')}
            className={`w-full text-left p-2.5 rounded-lg text-xs flex items-center gap-2.5 transition-all cursor-pointer ${
              activeTab === 'about'
                ? 'bg-primary/10 text-primary border border-primary/20 font-semibold'
                : 'bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 text-on-surface-variant hover:bg-black/10 dark:hover:bg-white/10'
            }`}
            id="settings-tab-about"
          >
            <Cpu size={14} />
            <span>Workstation Spec</span>
          </button>
        </div>

        {/* Dynamic Theme Control Block */}
        <div className="pt-3 border-t border-black/10 dark:border-white/5 mt-4">
          <p className="text-[10px] font-mono text-on-surface-variant opacity-60 uppercase tracking-widest mb-2 text-center">
            Theme Sandbox
          </p>
          <button
            onClick={toggleTheme}
            className="w-full p-2.5 bg-primary/10 hover:bg-primary/15 border border-primary/20 rounded-xl flex items-center justify-between text-xs transition-all cursor-pointer group"
            id="theme-toggle-sidebar"
          >
            <div className="flex items-center gap-2">
              {systemState.theme === 'light' ? (
                <Sun size={14} className="text-amber-500 animate-spin-slow" />
              ) : (
                <Moon size={14} className="text-primary animate-pulse" />
              )}
              <span className="font-semibold text-primary capitalize">{systemState.theme} Mode</span>
            </div>
            <div className="w-8 h-4 bg-black/15 dark:bg-black/30 rounded-full p-0.5 flex items-center transition-all">
              <div
                className={`w-3 h-3 bg-primary rounded-full shadow-md transform transition-all duration-300 ${
                  systemState.theme === 'light' ? 'translate-x-4 bg-amber-500' : 'translate-x-0'
                }`}
              />
            </div>
          </button>
        </div>
      </div>

      {/* Main Settings Display */}
      <div className="flex-1 bg-surface-container-low/60 rounded-xl border border-black/10 dark:border-white/5 p-5 flex flex-col gap-4 overflow-hidden text-left text-xs">
        {activeTab === 'kiosk' && (
          <div className="space-y-4 overflow-y-auto custom-scrollbar flex-1 pr-1">
            <h2 className="text-sm font-semibold text-on-surface border-b border-black/10 dark:border-white/5 pb-2 mb-3">Workstation Configuration</h2>

            {/* Profile */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-[10px] font-mono text-on-surface-variant opacity-70 uppercase tracking-wider block">
                  Device Hostname
                </label>
                <input
                  type="text"
                  value={deviceName}
                  onChange={(e) => onChangeDeviceName(e.target.value.replace(/[^a-zA-Z0-9_-]/g, ''))}
                  placeholder="NEX-WIN-001"
                  className="w-full text-xs bg-black/5 dark:bg-black/30 border border-black/10 dark:border-white/10 focus:border-primary/50 rounded-lg p-2.5 text-on-surface font-mono outline-none"
                  id="settings-device-input"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-mono text-on-surface-variant opacity-70 uppercase tracking-wider block">
                  Workstation Authorization
                </label>
                <select
                  value={systemState.mode}
                  onChange={handleModeChange}
                  className="w-full text-xs bg-black/5 dark:bg-black/30 border border-black/10 dark:border-white/10 focus:border-primary/50 rounded-lg p-2.5 text-on-surface outline-none font-semibold cursor-pointer"
                  id="settings-mode-selector"
                >
                  <option value="Mode 1">Mode 1 (Standard Kiosk)</option>
                  <option value="Mode 2">Mode 2 (Expanded Kiosk)</option>
                  <option value="Admin Mode">Admin Mode (Unrestricted Root)</option>
                </select>
              </div>
            </div>

            {/* Integrity Scan block */}
            <div className="p-4 bg-black/5 dark:bg-white/5 rounded-xl border border-black/10 dark:border-white/5 space-y-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <h3 className="font-semibold text-on-surface">System Integrity Shield</h3>
                  <p className="text-[11px] text-on-surface-variant opacity-60">
                    Verify that sandboxes, camera permissions, and firewalls comply with security metrics.
                  </p>
                </div>
                <button
                  onClick={handleStartScan}
                  disabled={isScanning}
                  className="p-2 bg-primary text-on-primary hover:bg-primary-container disabled:opacity-50 font-semibold rounded-lg flex items-center justify-center gap-1.5 font-sans transition-colors cursor-pointer shrink-0"
                  id="settings-scan-btn"
                >
                  {isScanning ? <RefreshCw size={12} className="animate-spin" /> : <Play size={12} />}
                  <span>{isScanning ? 'Verifying...' : 'Audit System'}</span>
                </button>
              </div>

              {/* Progress bar */}
              {isScanning && (
                <div className="space-y-1.5">
                  <div className="flex justify-between font-mono text-[9px] opacity-60">
                    <span>SCANNING PORTS AND CONTAINER DEFAULTS...</span>
                    <span>{scanProgress}%</span>
                  </div>
                  <div className="w-full bg-black/10 dark:bg-white/10 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-primary h-full transition-all duration-100" style={{ width: `${scanProgress}%` }}></div>
                  </div>
                </div>
              )}

              {scanStatus === 'passed' && (
                <div className="p-3 bg-tertiary-container/10 border border-tertiary-container/30 text-tertiary rounded-lg flex items-center gap-2">
                  <ShieldCheck size={16} className="animate-bounce shrink-0" />
                  <div>
                    <p className="font-bold">ALL SECURITY INTEGRITY METRICS PASSED // COMPLIANT</p>
                    <p className="text-[10px] opacity-80 font-mono mt-0.5">Biometric, Network Sandbox, and FS storage parameters are 100% SECURE.</p>
                  </div>
                </div>
              )}
            </div>

            {/* Quick settings switches */}
            <div className="p-4 bg-black/5 dark:bg-white/5 rounded-xl border border-black/10 dark:border-white/5">
              <h3 className="font-semibold text-on-surface mb-3">System Features</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
                <div className="flex items-center justify-between p-2.5 bg-black/5 dark:bg-black/15 rounded">
                  <span className="text-on-surface-variant">DNS Proxy Sandbox</span>
                  <span className="text-tertiary font-bold">✔ ACTIVE</span>
                </div>
                <div className="flex items-center justify-between p-2.5 bg-black/5 dark:bg-black/15 rounded">
                  <span className="text-on-surface-variant">HMR File Watching</span>
                  <span className="text-error font-bold">✖ DISABLED</span>
                </div>
                <div className="flex items-center justify-between p-2.5 bg-black/5 dark:bg-black/15 rounded">
                  <span className="text-on-surface-variant">Session Transcripts</span>
                  <span className="text-tertiary font-bold">✔ AUDITED</span>
                </div>
                <div className="flex items-center justify-between p-2.5 bg-black/5 dark:bg-black/15 rounded">
                  <span className="text-on-surface-variant">Host IP Ingress</span>
                  <span className="text-primary font-bold">PORT 3000</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Real-time System Telemetry Tab */}
        {activeTab === 'telemetry' && (
          <div className="space-y-4 overflow-y-auto custom-scrollbar flex-1 pr-1">
            <div className="border-b border-black/10 dark:border-white/5 pb-2 mb-3">
              <h2 className="text-sm font-semibold text-on-surface">System Telemetry Audit</h2>
              <p className="text-[10px] text-on-surface-variant opacity-60 font-mono">Real-time hardware pipeline & sandbox environment tracking</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {/* Telemetry Card 1 */}
              <div className="p-4 bg-black/5 dark:bg-white/5 rounded-xl border border-black/10 dark:border-white/5 space-y-1.5 flex flex-col justify-between">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-on-surface-variant opacity-60 uppercase tracking-wider">Device Status</span>
                  <div className="flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${systemState.isOnline ? 'bg-tertiary status-glow' : 'bg-on-surface-variant'}`} />
                    <span className={`text-[10px] font-mono uppercase font-bold ${systemState.isOnline ? 'text-tertiary' : 'text-on-surface-variant'}`}>
                      {systemState.isOnline ? 'ONLINE' : 'OFFLINE'}
                    </span>
                  </div>
                </div>
                <div className="pt-2">
                  <p className="text-[9px] text-on-surface-variant opacity-50 uppercase font-mono">HOSTNAME</p>
                  <p className="text-sm font-bold text-primary font-mono">{deviceName}</p>
                </div>
              </div>

              {/* Telemetry Card 2 */}
              <div className="p-4 bg-black/5 dark:bg-white/5 rounded-xl border border-black/10 dark:border-white/5 space-y-1.5 flex flex-col justify-between">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-on-surface-variant opacity-60 uppercase tracking-wider">Security State</span>
                  <ShieldAlert size={14} className="text-secondary" />
                </div>
                <div className="pt-2">
                  <p className="text-[9px] text-on-surface-variant opacity-50 uppercase font-mono">AUTHORIZATION</p>
                  <p className="text-sm font-bold text-secondary font-mono">{systemState.mode}</p>
                </div>
              </div>

              {/* Telemetry Card 3 */}
              <div className="p-4 bg-black/5 dark:bg-white/5 rounded-xl border border-black/10 dark:border-white/5 space-y-1.5 flex flex-col justify-between">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-on-surface-variant opacity-60 uppercase tracking-wider">Container Integrity</span>
                  <ShieldCheck size={14} className="text-tertiary" />
                </div>
                <div className="pt-2">
                  <p className="text-[9px] text-on-surface-variant opacity-50 uppercase font-mono">SANDBOX</p>
                  <p className="text-sm font-bold text-tertiary font-mono">SECURE / ENCLOSED</p>
                </div>
              </div>
            </div>

            {/* Network Utilization */}
            <div className="p-4 bg-black/5 dark:bg-white/5 rounded-xl border border-black/10 dark:border-white/5 space-y-3">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-semibold text-on-surface">Network Bandwidth Ingress</h3>
                  <p className="text-[10px] text-on-surface-variant opacity-60">Real-time port 3000 stream data packets</p>
                </div>
                <span className="font-mono text-[10px] text-primary bg-primary/10 px-2 py-0.5 rounded-full border border-primary/20">
                  Ingress Capable
                </span>
              </div>
              
              <div className="flex items-end gap-1.5 h-16 pt-2 bg-black/5 dark:bg-black/15 px-4 rounded-lg border border-black/10 dark:border-white/5">
                {netBars && netBars.length > 0 ? (
                  netBars.map((val, idx) => (
                    <div
                      key={idx}
                      style={{ height: `${val}%` }}
                      className="flex-1 bg-primary/30 hover:bg-primary rounded-sm transition-all duration-300 ease-in-out cursor-help"
                      title={`Bandwidth Pipeline ${idx + 1}: ${val}%`}
                    />
                  ))
                ) : (
                  <div className="text-on-surface-variant opacity-40 text-center w-full pb-4 font-mono">Telemetry link offline.</div>
                )}
              </div>
              <p className="text-[9px] font-mono text-on-surface-variant opacity-50 text-right">Updated 1200ms dynamically // Sandbox Tunnel Ingress</p>
            </div>

            {/* Detailed System Diagnostics Log summary */}
            <div className="p-4 bg-black/5 dark:bg-white/5 rounded-xl border border-black/10 dark:border-white/5 space-y-2.5">
              <h3 className="font-semibold text-on-surface">Security Sandboxing Verification</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] font-mono">
                <div className="flex items-center gap-2 p-2 bg-black/10 dark:bg-black/20 rounded">
                  <Wifi size={12} className="text-tertiary" />
                  <span className="text-on-surface-variant">Proxy Port Binding: <strong className="text-on-surface">PORT 3000 (PASSED)</strong></span>
                </div>
                <div className="flex items-center gap-2 p-2 bg-black/10 dark:bg-black/20 rounded">
                  <HardDrive size={12} className="text-tertiary" />
                  <span className="text-on-surface-variant">Biometric Camera Driver: <strong className="text-on-surface">LOADED (SECURE)</strong></span>
                </div>
                <div className="flex items-center gap-2 p-2 bg-black/10 dark:bg-black/20 rounded">
                  <Cpu size={12} className="text-tertiary" />
                  <span className="text-on-surface-variant">Thread Affinity Cap: <strong className="text-on-surface">4 Cores (BOUND)</strong></span>
                </div>
                <div className="flex items-center gap-2 p-2 bg-black/10 dark:bg-black/20 rounded">
                  <ShieldAlert size={12} className="text-tertiary" />
                  <span className="text-on-surface-variant">Firewall Isolation: <strong className="text-on-surface">ACTIVE (ISOLATED)</strong></span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="flex-1 flex flex-col justify-between overflow-hidden">
            <div className="flex items-center justify-between border-b border-black/10 dark:border-white/5 pb-2 mb-3">
              <div>
                <h2 className="text-sm font-semibold text-on-surface">Diagnostic Audit Logs</h2>
                <p className="text-[10px] text-on-surface-variant opacity-60 font-mono">Dynamic shell session transcript audits</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={clearLogs}
                  className="p-1.5 bg-black/5 dark:bg-white/5 hover:bg-error-container/20 hover:text-error text-on-surface-variant border border-black/10 dark:border-white/5 rounded flex items-center justify-center cursor-pointer"
                  title="Clear Log History"
                  id="settings-clear-logs"
                >
                  <Trash2 size={12} />
                </button>
                <button
                  onClick={handleExportLogs}
                  className={`p-1.5 border rounded flex items-center justify-center gap-1 cursor-pointer font-sans font-semibold text-[11px] ${
                    exportSuccess ? 'bg-tertiary text-on-tertiary border-tertiary' : 'bg-primary text-on-primary border-primary hover:bg-primary-container'
                  }`}
                  id="settings-export-logs"
                >
                  {exportSuccess ? <Check size={12} /> : <FileOutput size={12} />}
                  <span>{exportSuccess ? 'Exported!' : 'Export Logs'}</span>
                </button>
              </div>
            </div>

            {/* Dynamic log terminal */}
            <div className="flex-1 bg-black/5 dark:bg-black/50 border border-black/10 dark:border-white/5 p-3 rounded-lg font-mono text-[11px] text-on-surface-variant overflow-y-auto custom-scrollbar space-y-1.5 select-text">
              {systemState.logs.length === 0 ? (
                <p className="text-on-surface-variant opacity-40 italic">Terminal transaction logs empty.</p>
              ) : (
                systemState.logs.map((log, index) => (
                  <p key={index} className="leading-relaxed">
                    <span className="text-primary font-semibold">[AUDIT_LOG]</span> {log}
                  </p>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'about' && (
          <div className="space-y-4 overflow-y-auto custom-scrollbar flex-1 pr-1">
            <h2 className="text-sm font-semibold text-on-surface border-b border-black/10 dark:border-white/5 pb-2 mb-3">Workstation Specification</h2>
            <div className="space-y-2 font-mono text-on-surface-variant">
              <div className="p-3 bg-black/5 dark:bg-white/5 rounded-lg border border-black/10 dark:border-white/5 space-y-1.5 leading-normal">
                <p><span className="text-on-surface font-bold">SYSTEM OVERVIEW</span></p>
                <p>OS: Lumina Core Desktop OS (v4.2.883)</p>
                <p>Shell Ingress: Containerized Port 3000 Node Environment</p>
                <p>Architecture: Virtualized Sandbox Hypervisor</p>
              </div>

              <div className="p-3 bg-black/5 dark:bg-white/5 rounded-lg border border-black/10 dark:border-white/5 space-y-1.5 leading-normal">
                <p><span className="text-on-surface font-bold">RESOURCE LIMITS</span></p>
                <p>CPU Core Cap: 4 threads maximum affinity</p>
                <p>Max Heap Allocation: 4,096 MB memory heap limit</p>
                <p>HMR Sockets: Disabled dynamically</p>
              </div>

              <div className="p-3 bg-black/5 dark:bg-white/5 rounded-lg border border-black/10 dark:border-white/5 space-y-1.5 leading-normal">
                <p><span className="text-on-surface font-bold">LEGAL COMPLIANCE</span></p>
                <p>Hardened Sandbox Enclosures compliant with ISO-27001 public sector specifications. Transaction logs are preserved in temporary memory buffers and do not route to public analytics channels unless explicit cloud sync modes are authorized by operators.</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
