import React, { useState, useEffect } from 'react';
import { FileCode, Clipboard, Check, ChevronRight, BookOpen, Terminal } from 'lucide-react';
import { APP_SOURCE_CODES, CodeFile } from '../data/sourceCode';

interface WindowsCodeViewerProps {
  activeApp: string;
  addLog?: (msg: string) => void;
}

export default function WindowsCodeViewer({ activeApp, addLog }: WindowsCodeViewerProps) {
  const files = APP_SOURCE_CODES[activeApp] || [];
  const [selectedFile, setSelectedFile] = useState<CodeFile | null>(null);
  const [copied, setCopied] = useState(false);

  // Set the first file as active by default when activeApp changes
  useEffect(() => {
    if (files.length > 0) {
      setSelectedFile(files[0]);
    } else {
      setSelectedFile(null);
    }
  }, [activeApp]);

  if (files.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-on-surface-variant font-mono text-center">
        <Terminal size={32} className="text-error/60 mb-2 animate-pulse" />
        <p className="text-xs">NO WINDOWS PLATFORM SOURCE CODES LOADED FOR THIS MODULE.</p>
      </div>
    );
  }

  const handleCopy = () => {
    if (!selectedFile) return;
    navigator.clipboard.writeText(selectedFile.content);
    setCopied(true);
    if (addLog) addLog(`Copied file workspace source code: ${selectedFile.name}`);
    setTimeout(() => setCopied(false), 2000);
  };

  // Safe and ultra-fast syntax highlighter matching major WPF/UWP C# and XAML lexical patterns
  const highlightCode = (code: string, language: 'xml' | 'csharp' | 'json') => {
    const escaped = code
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    if (language === 'xml') {
      return escaped
        // Comments
        .replace(/(&lt;!--[\s\S]*?--&gt;)/g, '<span class="text-zinc-500 italic">$1</span>')
        // Attributes
        .replace(/\s([a-zA-Z0-9:\.]+)=/g, ' <span class="text-teal-400 font-medium">$1</span>=')
        // Tags
        .replace(/(&lt;\/?[a-zA-Z0-9:\.]+)/g, '<span class="text-indigo-400 font-semibold">$1</span>')
        .replace(/(\/?&gt;)/g, '<span class="text-indigo-400 font-semibold">$1</span>')
        // Strings
        .replace(/"([^"]*)"/g, '"<span class="text-amber-300">$1</span>"');
    } else if (language === 'csharp') {
      return escaped
        // Comments
        .replace(/(\/\/.*)/g, '<span class="text-zinc-500 italic">$1</span>')
        // Keywords
        .replace(/\b(using|namespace|partial|class|public|private|sealed|void|async|await|try|catch|new|var|string|bool|double|byte|uint|int|return|this|if|else|switch|case|break|default|typeof)\b/g, '<span class="text-pink-400 font-semibold">$1</span>')
        // Core framework Objects/Types
        .replace(/\b(MediaCapture|CaptureElement|ImageEncodingProperties|StorageFolder|KnownFolders|StorageFile|CreationCollisionOption|FileAccessMode|PixelDataProvider|BitmapDecoder|BitmapEncoder|BitmapPixelFormat|BitmapAlphaMode|IRandomAccessStream|TextSetOptions|TextGetOptions|RichEditBox|Button|Page|Grid|RowDefinition|ColumnDefinition|TextBlock|TextBox|SheetRow|ObservableCollection|PdfDocument|PdfPage|BitmapImage|InMemoryRandomAccessStream|SymbolIcon|NavigationView|Frame|KioskConfigPage|TelemetryViewPage|AuditLogsViewPage|FileIO)\b/g, '<span class="text-cyan-400 font-medium">$1</span>')
        // Methods
        .replace(/\.([a-zA-Z0-9_]+)\(/g, '.<span class="text-emerald-300">$1</span>(')
        // Strings
        .replace(/"([^"]*)"/g, '"<span class="text-amber-300">$1</span>"');
    }
    return escaped;
  };

  const codeLines = selectedFile ? selectedFile.content.split('\n') : [];

  return (
    <div className="flex flex-col lg:flex-row h-full text-on-surface bg-surface-dim/90 rounded-xl overflow-hidden border border-white/5 font-sans">
      
      {/* File Navigation Panel */}
      <div className="w-full lg:w-64 bg-surface-container-low/40 p-4 border-b lg:border-b-0 lg:border-r border-white/5 flex flex-col gap-3">
        <div className="flex items-center gap-1.5 opacity-70">
          <FileCode size={13} className="text-primary" />
          <h4 className="text-[10px] font-mono uppercase tracking-widest font-semibold">Solution Explorer</h4>
        </div>

        <div className="space-y-1">
          {files.map((file) => (
            <button
              key={file.name}
              onClick={() => setSelectedFile(file)}
              className={`w-full text-left p-2.5 rounded-lg text-xs flex items-center justify-between transition-all cursor-pointer ${
                selectedFile?.name === file.name
                  ? 'bg-primary/10 text-primary border border-primary/20 font-semibold'
                  : 'bg-white/5 border border-white/5 text-on-surface-variant hover:bg-white/10'
              }`}
              id={`solution-file-${file.name.replace('.', '-')}`}
            >
              <div className="flex items-center gap-2 truncate">
                <FileCode size={12} className={selectedFile?.name === file.name ? 'text-primary' : 'text-on-surface-variant'} />
                <span className="font-mono truncate">{file.name}</span>
              </div>
              <ChevronRight size={12} className="opacity-40" />
            </button>
          ))}
        </div>

        {/* Documentation Context Box */}
        {selectedFile && (
          <div className="mt-auto p-3.5 bg-primary/5 rounded-xl border border-primary/10 text-left space-y-1.5">
            <div className="flex items-center gap-1.5 text-primary">
              <BookOpen size={12} />
              <span className="text-[10px] font-mono uppercase tracking-wider font-bold">API Context</span>
            </div>
            <p className="text-[11px] leading-relaxed text-on-surface-variant/90">
              {selectedFile.description}
            </p>
          </div>
        )}
      </div>

      {/* Editor Canvas Pane */}
      <div className="flex-1 flex flex-col overflow-hidden bg-[#0c0e0e] text-left">
        {selectedFile ? (
          <>
            {/* Toolbar */}
            <div className="h-11 border-b border-white/5 px-4 flex items-center justify-between select-none">
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono text-primary font-bold px-1.5 py-0.5 rounded bg-primary/10 border border-primary/20 uppercase">
                  {selectedFile.language === 'xml' ? 'XAML / XML' : 'C# / CSHARP'}
                </span>
                <span className="text-xs font-mono text-on-surface-variant font-semibold">
                  {selectedFile.name}
                </span>
              </div>

              <button
                onClick={handleCopy}
                className={`px-3 py-1.5 rounded-md text-[11px] font-semibold flex items-center gap-1.5 border transition-all cursor-pointer ${
                  copied
                    ? 'bg-tertiary/10 border-tertiary/30 text-tertiary'
                    : 'bg-white/5 border-white/5 hover:bg-white/10 text-on-surface'
                }`}
                id="ide-copy-code"
              >
                {copied ? (
                  <>
                    <Check size={12} />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Clipboard size={12} />
                    <span>Copy Code</span>
                  </>
                )}
              </button>
            </div>

            {/* Code display with line numbers */}
            <div className="flex-1 overflow-auto custom-scrollbar font-mono text-xs p-4 flex select-text leading-relaxed">
              {/* Line Numbers column */}
              <div className="text-on-surface-variant opacity-30 select-none text-right pr-4 border-r border-white/5 select-none shrink-0 space-y-0.5 font-semibold">
                {codeLines.map((_, i) => (
                  <div key={i}>{i + 1}</div>
                ))}
              </div>

              {/* Syntax Colored Code */}
              <pre className="pl-4 overflow-x-auto whitespace-pre space-y-0.5 select-text w-full text-zinc-300">
                {codeLines.map((line, i) => (
                  <code
                    key={i}
                    className="block min-h-[1.25rem] select-text"
                    dangerouslySetInnerHTML={{
                      __html: highlightCode(line, selectedFile.language) || '&nbsp;'
                    }}
                  />
                ))}
              </pre>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center font-mono text-on-surface-variant text-xs p-10 text-center select-none">
            Please select a file from Solution Explorer to inspect.
          </div>
        )}
      </div>
    </div>
  );
}
