import React, { useState } from 'react';
import { Bold, Italic, Underline, AlignLeft, AlignCenter, AlignRight, Save, HelpCircle, Check, FileText, Sparkles } from 'lucide-react';

interface WordEditorProps {
  onSaveFile?: (name: string, type: 'doc', content: string) => void;
  addLog?: (msg: string) => void;
}

export default function WordEditor({ onSaveFile, addLog }: WordEditorProps) {
  const [content, setContent] = useState('');
  const [docName, setDocName] = useState('Security_Audit');
  const [isBold, setIsBold] = useState(false);
  const [isItalic, setIsItalic] = useState(false);
  const [isUnderline, setIsUnderline] = useState(false);
  const [alignment, setAlignment] = useState<'left' | 'center' | 'right'>('left');
  const [saveSuccess, setSaveSuccess] = useState(false);

  const templates = {
    empty: '',
    protocol: `==================================================
SECURE KIOSK SYSTEM TERMINAL SECURITY PROTOCOL
==================================================
CLASSIFICATION: CONFIDENTIAL
DEVICE STATUS: ACTIVE SANBDX-1
LOG DATE: ${new Date().toLocaleDateString()}

1. SYSTEM ACCESS CONTROLS
- This workstation (NEX-WIN-001) is restricted under Mode 1.
- Only authorized diagnostic utilities and internal browsers are enabled.
- User sessions are audited dynamically for integrity.

2. FIREWALL REGULATION
- DNS Resolution is configured server-side.
- Attempted external outbound pings are automatically containerized.

3. RECOVERY & FALLBACK
- To reset system state, press the Kiosk Power control in the bottom tray.
- Self-recovering sandboxes will reload standard variables instantly.`,
    
    diagnostic: `==================================================
KIOSK HARDWARE & TERMINAL DIAGNOSTIC REPORT
==================================================
GENERATED: ${new Date().toLocaleString()}
INTEGRITY STATUS: SECURE

[CPU CONFIGURATION]
Intel Xeon Scalable Core @ 3.4GHz
Virtual Sockets: 4 | Threads: 8
Core Temperature: 42°C (STABLE)

[MEMORY STATISTICS]
Total Alloc: 16,384 MB
Used Cache: 4,120 MB
Free Memory: 12,264 MB

[NETWORK UTILIZATION]
Interface eth0: 1000 Mbps Full Duplex
IP Address: 172.18.0.2 (Docker Network Internal)
Ping to Host Ingress: <0.2ms

==================================================
DIAGNOSTIC STATUS: PASS (NO WARNINGS)
==================================================`,

    acceptable: `==================================================
ACCEPTABLE USE POLICY (AUP) - SYSTEM KIOSK
==================================================
1. TERMS OF SERVICE
This terminal is provided strictly for diagnostic, administrative, and authorized exploration tasks. 

2. USER ACTIONS
Users must not attempt to bypass container namespaces or modify local configuration files. 

3. NETWORK USE
Internet simulator utilities are provided to demonstrate secure sandboxing. Do not use external APIs for sensitive or private data unless secure server-side pathways are configured.

BY CONTINUING TO USE THIS SYSTEM, THE OPERATOR AGREES TO ALL FOREGOING SECURITY CLAUSES.`
  };

  const handleTemplate = (type: keyof typeof templates) => {
    setContent(templates[type]);
    if (addLog) addLog(`Word Processor loaded template: ${type}`);
  };

  const handleSave = () => {
    if (!content.trim()) return;
    const filename = docName.trim().endsWith('.doc') ? docName.trim() : `${docName.trim()}.doc`;
    if (onSaveFile) {
      onSaveFile(filename, 'doc', content);
      setSaveSuccess(true);
      if (addLog) addLog(`Document saved to virtual explorer: ${filename}`);
      setTimeout(() => setSaveSuccess(false), 2000);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row h-full gap-4 text-on-surface">
      {/* Sidebar Controls */}
      <div className="w-full lg:w-64 flex flex-col gap-3 p-4 bg-surface-container/40 rounded-xl border border-white/5">
        <div>
          <h3 className="text-sm font-semibold opacity-70 uppercase tracking-wider mb-2">Templates</h3>
          <div className="space-y-1.5">
            <button
              onClick={() => handleTemplate('protocol')}
              className="w-full text-left p-2.5 bg-white/5 hover:bg-white/10 rounded-lg text-xs flex items-center gap-2 border border-white/5 transition-colors cursor-pointer"
              id="word-temp-protocol"
            >
              <FileText size={14} className="text-primary" />
              <span>Security Audit Protocol</span>
            </button>
            <button
              onClick={() => handleTemplate('diagnostic')}
              className="w-full text-left p-2.5 bg-white/5 hover:bg-white/10 rounded-lg text-xs flex items-center gap-2 border border-white/5 transition-colors cursor-pointer"
              id="word-temp-diag"
            >
              <FileText size={14} className="text-secondary" />
              <span>Diagnostic Report</span>
            </button>
            <button
              onClick={() => handleTemplate('acceptable')}
              className="w-full text-left p-2.5 bg-white/5 hover:bg-white/10 rounded-lg text-xs flex items-center gap-2 border border-white/5 transition-colors cursor-pointer"
              id="word-temp-aup"
            >
              <FileText size={14} className="text-tertiary" />
              <span>Acceptable Use Policy</span>
            </button>
            <button
              onClick={() => handleTemplate('empty')}
              className="w-full text-left p-2 bg-black/15 hover:bg-black/25 rounded-lg text-xs text-on-surface-variant italic text-center transition-colors cursor-pointer"
              id="word-temp-clear"
            >
              Clear Workspace
            </button>
          </div>
        </div>

        {/* Save/Export */}
        <div className="mt-auto pt-3 border-t border-white/5 space-y-2">
          <h3 className="text-xs font-semibold opacity-70 uppercase tracking-wider mb-1">Save to Kiosk Files</h3>
          <input
            type="text"
            value={docName}
            onChange={(e) => setDocName(e.target.value.replace(/[^a-zA-Z0-9_-]/g, ''))}
            placeholder="document_name"
            className="w-full text-xs bg-black/30 border border-white/10 focus:border-primary/50 rounded p-2 text-on-surface font-mono outline-none"
            id="word-doc-name"
          />
          <button
            onClick={handleSave}
            disabled={!content.trim()}
            className={`w-full p-2.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer ${
              saveSuccess
                ? 'bg-tertiary text-on-tertiary shadow-[0_0_12px_rgba(101,248,151,0.3)]'
                : 'bg-primary hover:bg-primary-container text-on-primary disabled:opacity-40 disabled:hover:bg-primary'
            }`}
            id="word-save-btn"
          >
            {saveSuccess ? (
              <>
                <Check size={14} />
                Saved Draft!
              </>
            ) : (
              <>
                <Save size={14} />
                Save Document (.doc)
              </>
            )}
          </button>
        </div>
      </div>

      {/* Editor Space */}
      <div className="flex-1 bg-surface-container-low/60 rounded-xl border border-white/5 p-3 flex flex-col gap-3">
        {/* Editor Toolbar */}
        <div className="flex items-center justify-between p-2 bg-surface-container-high/60 border border-white/10 rounded-lg">
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setIsBold(!isBold)}
              className={`p-1.5 rounded transition-colors cursor-pointer ${isBold ? 'bg-primary/20 text-primary font-bold' : 'hover:bg-white/5 text-on-surface-variant'}`}
              id="word-tb-bold"
            >
              <Bold size={14} />
            </button>
            <button
              onClick={() => setIsItalic(!isItalic)}
              className={`p-1.5 rounded transition-colors cursor-pointer ${isItalic ? 'bg-primary/20 text-primary italic' : 'hover:bg-white/5 text-on-surface-variant'}`}
              id="word-tb-italic"
            >
              <Italic size={14} />
            </button>
            <button
              onClick={() => setIsUnderline(!isUnderline)}
              className={`p-1.5 rounded transition-colors cursor-pointer ${isUnderline ? 'bg-primary/20 text-primary underline' : 'hover:bg-white/5 text-on-surface-variant'}`}
              id="word-tb-underline"
            >
              <Underline size={14} />
            </button>
            <div className="w-[1px] h-4 bg-white/10 mx-1"></div>
            <button
              onClick={() => setAlignment('left')}
              className={`p-1.5 rounded transition-colors cursor-pointer ${alignment === 'left' ? 'bg-primary/20 text-primary' : 'hover:bg-white/5 text-on-surface-variant'}`}
              id="word-tb-left"
            >
              <AlignLeft size={14} />
            </button>
            <button
              onClick={() => setAlignment('center')}
              className={`p-1.5 rounded transition-colors cursor-pointer ${alignment === 'center' ? 'bg-primary/20 text-primary' : 'hover:bg-white/5 text-on-surface-variant'}`}
              id="word-tb-center"
            >
              <AlignCenter size={14} />
            </button>
            <button
              onClick={() => setAlignment('right')}
              className={`p-1.5 rounded transition-colors cursor-pointer ${alignment === 'right' ? 'bg-primary/20 text-primary' : 'hover:bg-white/5 text-on-surface-variant'}`}
              id="word-tb-right"
            >
              <AlignRight size={14} />
            </button>
          </div>

          <div className="flex items-center gap-1 text-[10px] text-on-surface-variant opacity-70">
            <Sparkles size={10} className="text-primary animate-pulse" />
            <span>Kiosk Draft Processor</span>
          </div>
        </div>

        {/* Textarea Workspace */}
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Start typing your system report, guidelines, or note document here..."
          style={{
            fontWeight: isBold ? 'bold' : 'normal',
            fontStyle: isItalic ? 'italic' : 'normal',
            textDecoration: isUnderline ? 'underline' : 'none',
            textAlign: alignment,
          }}
          className="flex-1 w-full bg-black/10 border border-white/5 focus:border-white/15 outline-none rounded-lg p-4 font-mono text-xs leading-relaxed text-on-surface resize-none focus:ring-0"
          id="word-textarea"
        />

        <div className="flex items-center justify-between text-[11px] text-on-surface-variant opacity-60 font-mono px-1">
          <span>Words: {content.trim() ? content.trim().split(/\s+/).length : 0} | Characters: {content.length}</span>
          <span className="flex items-center gap-1">
            <HelpCircle size={10} className="text-secondary" />
            Saved documents will instantly populate your File Explorer grid.
          </span>
        </div>
      </div>
    </div>
  );
}
