import React, { useState } from 'react';
import { BookOpen, ZoomIn, ZoomOut, Search, Download, Printer, ShieldAlert, Check } from 'lucide-react';

interface PdfViewerProps {
  addLog?: (msg: string) => void;
}

export default function PdfViewer({ addLog }: PdfViewerProps) {
  const [activeDoc, setActiveDoc] = useState<'manual' | 'firewall' | 'compliance'>('manual');
  const [zoom, setZoom] = useState(100);
  const [search, setSearch] = useState('');
  const [printSuccess, setPrintSuccess] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const handlePrint = () => {
    setPrintSuccess(true);
    if (addLog) addLog(`PDF printed virtual spool request: ${activeDoc}`);
    setTimeout(() => setPrintSuccess(false), 2000);
  };

  const handleDownload = () => {
    setDownloadSuccess(true);
    if (addLog) addLog(`PDF downloaded offline bundle for: ${activeDoc}`);
    setTimeout(() => setDownloadSuccess(false), 2000);
  };

  // Helper to highlight search terms
  const highlightText = (text: string) => {
    if (!search.trim()) return text;
    const parts = text.split(new RegExp(`(${search})`, 'gi'));
    return (
      <>
        {parts.map((part, i) =>
          part.toLowerCase() === search.toLowerCase() ? (
            <span key={i} className="bg-primary/40 text-white font-semibold px-0.5 rounded">
              {part}
            </span>
          ) : (
            part
          )
        )}
      </>
    );
  };

  const renderManual = () => (
    <div className="space-y-6" style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }}>
      {/* PDF Page 1 */}
      <div className="bg-white text-black p-8 rounded shadow-md aspect-[1/1.41] max-w-[550px] mx-auto border border-gray-300 font-sans text-left text-xs leading-relaxed relative">
        <div className="absolute top-4 right-4 border border-red-600 text-red-600 px-2 py-0.5 font-mono font-bold text-[9px] uppercase tracking-widest rotate-6">
          Restricted access
        </div>

        <div className="border-b-2 border-primary pb-3 mb-6">
          <h1 className="text-xl font-bold font-serif tracking-tight text-gray-900">LUMINA KIOSK WORKSTATION</h1>
          <p className="text-[10px] font-mono font-bold text-gray-500 uppercase">Operator Manual v4.2 // Lumina Systems</p>
        </div>

        <h2 className="text-sm font-bold text-gray-800 mb-2 mt-4">1. SYSTEM INTENT</h2>
        <p className="text-gray-700 mb-4">
          {highlightText(
            'The Lumina Secure Terminal Kiosk is engineered to serve as a hardened, single-purpose dashboard in public and enterprise settings. It features high-visibility glassmorphic interfaces designed to offer clear information density while enforcing strict security constraints.'
          )}
        </p>

        <h2 className="text-sm font-bold text-gray-800 mb-2">2. SANDBOX ARCHITECTURE</h2>
        <p className="text-gray-700 mb-3">
          {highlightText(
            'Lumina Kiosks employ an offline-first containerized environment. All diagnostic modules (such as Edge Browser, Word Processor, and camera feed loops) execute isolated from root storage channels. The persistent container state is dynamically monitored for integrity.'
          )}
        </p>

        {/* Mock Flowchart diagram */}
        <div className="border border-dashed border-gray-300 p-4 rounded bg-gray-50 my-6 text-center">
          <p className="font-mono text-[9px] text-gray-400 mb-2 uppercase tracking-wide">Diagram 1.2: Core Namespace Isolation</p>
          <div className="flex justify-around items-center gap-1 font-mono text-[10px]">
            <div className="p-1.5 bg-blue-100 text-blue-800 rounded border border-blue-200">Kiosk Shell</div>
            <div className="text-gray-400">⟶</div>
            <div className="p-1.5 bg-red-100 text-red-800 rounded border border-red-200">Sandbox App</div>
            <div className="text-gray-400">⟶</div>
            <div className="p-1.5 bg-green-100 text-green-800 rounded border border-green-200">Encrypted FS</div>
          </div>
        </div>

        <h2 className="text-sm font-bold text-gray-800 mb-2">3. SECURITY MODE REGULATIONS</h2>
        <p className="text-gray-700 mb-4">
          Under standard <b>Mode 1</b>, the kiosk prevents raw console commands. Only verified, compiled applications listed in the main welcome catalog are executable. Attempted integrity bypasses automatically write logs to local node telemetry.
        </p>

        <div className="mt-8 pt-4 border-t border-gray-200 flex justify-between items-center text-[10px] text-gray-400 font-mono">
          <span>SEC_MAN_LUM_4.2</span>
          <span>Page 1 of 2</span>
        </div>
      </div>

      {/* PDF Page 2 */}
      <div className="bg-white text-black p-8 rounded shadow-md aspect-[1/1.41] max-w-[550px] mx-auto border border-gray-300 font-sans text-left text-xs leading-relaxed mt-4">
        <h2 className="text-sm font-bold text-gray-800 mb-2">4. OPERATIONAL CHECKS</h2>
        <p className="text-gray-700 mb-4">
          {highlightText(
            'Operators should periodically run systemic health logs through the diagnostics menu. Active core performance and network packet configurations should remain within standard operating ranges.'
          )}
        </p>

        <h2 className="text-sm font-bold text-gray-800 mb-2">5. POWER RECOVERY AND FAILSAFE</h2>
        <p className="text-gray-700 mb-4">
          Should a process stall, use the bottom power tray controls to trigger a soft reload. The kiosk will flush its ephemeral virtual sandbox memory and restart into clean secure defaults in less than 3 seconds.
        </p>

        {/* Stamp / Seal decoration */}
        <div className="mt-20 flex justify-end gap-3 items-center">
          <div className="text-right">
            <p className="font-semibold text-gray-800">Approved by:</p>
            <p className="text-gray-500 font-mono text-[10px]">Lumina Security Commission</p>
          </div>
          <div className="w-12 h-12 rounded-full border-4 border-double border-green-700 flex items-center justify-center font-mono font-extrabold text-[8px] text-green-700 uppercase tracking-tighter rotate-12 select-none">
            Approved Seal
          </div>
        </div>

        <div className="mt-20 pt-4 border-t border-gray-200 flex justify-between items-center text-[10px] text-gray-400 font-mono">
          <span>SEC_MAN_LUM_4.2</span>
          <span>Page 2 of 2</span>
        </div>
      </div>
    </div>
  );

  const renderFirewall = () => (
    <div className="space-y-6" style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }}>
      <div className="bg-white text-black p-8 rounded shadow-md aspect-[1/1.41] max-w-[550px] mx-auto border border-gray-300 font-sans text-left text-xs leading-relaxed relative">
        <div className="absolute top-4 right-4 border-2 border-double border-red-500 text-red-500 px-3 py-1 font-mono font-bold text-xs uppercase tracking-widest rotate-[-12deg]">
          Secret
        </div>

        <div className="border-b-2 border-red-700 pb-3 mb-6">
          <h1 className="text-xl font-bold font-mono tracking-tight text-red-700">FIREWALL ACCESS LIST (ACL)</h1>
          <p className="text-[10px] font-mono font-bold text-gray-500 uppercase">Document Ref: ACL-FWR-909 // CONFIDENTIAL</p>
        </div>

        <h2 className="text-sm font-bold text-gray-800 mb-2">1. OVERVIEW</h2>
        <p className="text-gray-700 mb-4">
          This document defines inbound and outbound firewall filtering rules applied specifically to the kiosk nodes. Under the sandboxed proxy framework, standard ports are closed to prevent unauthorized intrusion.
        </p>

        <h2 className="text-sm font-bold text-gray-800 mb-2">2. PORT BLOCK LISTS</h2>
        <div className="overflow-x-auto my-4">
          <table className="w-full text-[11px] font-mono border-collapse border border-gray-200">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-200 p-1">Rule ID</th>
                <th className="border border-gray-200 p-1">Port</th>
                <th className="border border-gray-200 p-1">Protocol</th>
                <th className="border border-gray-200 p-1">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="border border-gray-200 p-1">RL-101</td>
                <td className="border border-gray-200 p-1">80 / 443</td>
                <td className="border border-gray-200 p-1">TCP (HTTPS)</td>
                <td className="border border-gray-200 p-1 text-green-700 font-bold">PROXY_ONLY</td>
              </tr>
              <tr>
                <td className="border border-gray-200 p-1">RL-102</td>
                <td className="border border-gray-200 p-1">22</td>
                <td className="border border-gray-200 p-1">TCP (SSH)</td>
                <td className="border border-gray-200 p-1 text-red-600 font-bold">DROP_ALL</td>
              </tr>
              <tr>
                <td className="border border-gray-200 p-1">RL-103</td>
                <td className="border border-gray-200 p-1">3000</td>
                <td className="border border-gray-200 p-1">TCP (Ingress)</td>
                <td className="border border-gray-200 p-1 text-green-700 font-bold">ALLOW_LOCAL</td>
              </tr>
              <tr>
                <td className="border border-gray-200 p-1">RL-104</td>
                <td className="border border-gray-200 p-1">5432</td>
                <td className="border border-gray-200 p-1">TCP (DB)</td>
                <td className="border border-gray-200 p-1 text-red-600 font-bold">DROP_OUT</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2 className="text-sm font-bold text-gray-800 mb-2">3. DNS POLICY AND ENFORCEMENT</h2>
        <p className="text-gray-700 mb-4">
          All external host requests are resolved using an internal filtered nameserver. Domains like <b>google.com</b> and <b>wikipedia.org</b> are vetted and cached locally to prevent leaks.
        </p>

        <div className="mt-20 pt-4 border-t border-gray-200 flex justify-between items-center text-[10px] text-gray-400 font-mono">
          <span>ACL_CONFIDENTIAL_NODE</span>
          <span>Page 1 of 1</span>
        </div>
      </div>
    </div>
  );

  const renderCompliance = () => (
    <div className="space-y-6" style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }}>
      <div className="bg-white text-black p-8 rounded shadow-md aspect-[1/1.41] max-w-[550px] mx-auto border border-gray-300 font-sans text-left text-xs leading-relaxed relative">
        <div className="border-b-2 border-green-600 pb-3 mb-6">
          <h1 className="text-xl font-bold tracking-tight text-gray-800 font-serif">SECURITY COMPLIANCE AUDIT</h1>
          <p className="text-[10px] font-mono font-bold text-gray-500 uppercase">ISO-27001 / SOC2 Terminal Standards</p>
        </div>

        <h2 className="text-sm font-bold text-gray-800 mb-2">STANDARD 109 - UNATTENDED KIOSKS</h2>
        <p className="text-gray-700 mb-4">
          Unattended kiosk hardware in high-traffic physical areas must maintain specific physical and logical defenses.
        </p>

        <div className="p-3 bg-green-50 border border-green-200 rounded text-green-800 font-mono text-[10px] space-y-2 mb-4">
          <p className="font-bold">✔ CHECKLIST ISO-K-109:</p>
          <p>1. Local file encryption - ENABLED (AES-256)</p>
          <p>2. Frame permissions request - STRICTLY GUARDED</p>
          <p>3. Keyboard stroke hijacking block - ACTIVE</p>
          <p>4. Dynamic session timeouts - ENABLED</p>
        </div>

        <h2 className="text-sm font-bold text-gray-800 mb-2">RESTRICTIONS AND VIOLATIONS</h2>
        <p className="text-gray-700 mb-4">
          Any attempt to plug in unauthorized USB devices or inject commands via browser frames will trigger an automated session purge. Intrusion metrics will immediately dispatch reports to the administrator.
        </p>

        <div className="mt-40 pt-4 border-t border-gray-200 flex justify-between items-center text-[10px] text-gray-400 font-mono">
          <span>COMPLIANCE_CERT_109</span>
          <span>Page 1 of 1</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-full text-on-surface">
      {/* PDF Tool bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-surface-container-highest/60 border-b border-white/10 rounded-t-xl">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-red-600/10 text-error rounded border border-error/20">
            <BookOpen size={16} />
          </div>
          {/* Doc selector */}
          <select
            value={activeDoc}
            onChange={(e) => {
              const doc = e.target.value as 'manual' | 'firewall' | 'compliance';
              setActiveDoc(doc);
              if (addLog) addLog(`PDF Viewer loaded document: ${doc}`);
            }}
            className="bg-black/30 text-xs font-semibold text-on-surface border border-white/10 rounded p-1.5 focus:outline-none focus:border-primary/50"
            id="pdf-doc-selector"
          >
            <option value="manual">Lumina_Operator_Manual.pdf</option>
            <option value="firewall">Kiosk_Firewall_ACL_Confidential.pdf</option>
            <option value="compliance">ISO_Kiosk_Security_Standard.pdf</option>
          </select>
        </div>

        {/* Zoom & Search */}
        <div className="flex items-center gap-3">
          <div className="flex items-center bg-black/25 rounded border border-white/10 px-1 py-0.5">
            <button
              onClick={() => setZoom(Math.max(50, zoom - 10))}
              className="p-1 text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer"
              title="Zoom Out"
              id="pdf-zoom-out"
            >
              <ZoomOut size={13} />
            </button>
            <span className="text-[10px] font-mono font-semibold text-primary px-1.5">{zoom}%</span>
            <button
              onClick={() => setZoom(Math.min(150, zoom + 10))}
              className="p-1 text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer"
              title="Zoom In"
              id="pdf-zoom-in"
            >
              <ZoomIn size={13} />
            </button>
          </div>

          {/* Search keyword inside PDF */}
          <div className="relative flex items-center bg-black/25 rounded border border-white/10 px-2 py-1">
            <Search size={12} className="text-on-surface-variant opacity-60 mr-1.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search page..."
              className="bg-transparent border-0 outline-none text-[11px] p-0 w-24 text-on-surface font-mono"
              id="pdf-search-input"
            />
          </div>

          <div className="h-4 w-[1px] bg-white/10 mx-1"></div>

          {/* Action buttons */}
          <button
            onClick={handlePrint}
            className={`p-2 rounded hover:bg-white/5 transition-all text-on-surface flex items-center justify-center cursor-pointer ${
              printSuccess ? 'text-tertiary bg-tertiary/10 border border-tertiary/20' : 'text-on-surface-variant'
            }`}
            title="Spool Print Work"
            id="pdf-print-btn"
          >
            {printSuccess ? <Check size={14} className="animate-bounce" /> : <Printer size={14} />}
          </button>

          <button
            onClick={handleDownload}
            className={`p-2 rounded hover:bg-white/5 transition-all text-on-surface flex items-center justify-center cursor-pointer ${
              downloadSuccess ? 'text-tertiary bg-tertiary/10 border border-tertiary/20' : 'text-on-surface-variant'
            }`}
            title="Save Secure Copy"
            id="pdf-download-btn"
          >
            {downloadSuccess ? <Check size={14} className="animate-bounce" /> : <Download size={14} />}
          </button>
        </div>
      </div>

      {/* Sheet Space */}
      <div className="flex-1 min-h-[300px] overflow-y-auto custom-scrollbar bg-surface-container-low/40 p-6 flex flex-col items-center justify-start rounded-b-xl">
        {activeDoc === 'manual' && renderManual()}
        {activeDoc === 'firewall' && renderFirewall()}
        {activeDoc === 'compliance' && renderCompliance()}
      </div>
    </div>
  );
}
