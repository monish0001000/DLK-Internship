import React, { useState } from 'react';
import { Folder, Search, FileText, FileSpreadsheet, FileImage, FileCode, Trash2, ExternalLink, HelpCircle, ArrowLeftRight } from 'lucide-react';
import { VirtualFile, AppID } from '../types';

interface FileExplorerProps {
  files: VirtualFile[];
  onOpenFile: (file: VirtualFile) => void;
  onDeleteFile: (name: string) => void;
}

export default function FileExplorer({ files, onOpenFile, onDeleteFile }: FileExplorerProps) {
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'doc' | 'sheet' | 'pdf' | 'text' | 'image'>('all');

  const fileTypeIcons = {
    doc: <FileText className="text-primary" size={24} />,
    sheet: <FileSpreadsheet className="text-secondary" size={24} />,
    pdf: <FileCode className="text-error" size={24} />,
    text: <FileText className="text-on-surface-variant opacity-70" size={24} />,
    image: <FileImage className="text-tertiary" size={24} />,
  };

  const getReadableType = (type: string) => {
    switch (type) {
      case 'doc': return 'Word Document';
      case 'sheet': return 'Excel Sheet';
      case 'pdf': return 'Acrobat PDF';
      case 'text': return 'Text Document';
      case 'image': return 'Image Snapshot';
      default: return 'System File';
    }
  };

  const filteredFiles = files.filter(file => {
    const matchesSearch = file.name.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filterType === 'all' || file.type === filterType;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="flex flex-col md:flex-row h-full gap-4 text-on-surface">
      {/* Sidebar - Quick Access Links */}
      <div className="w-full md:w-56 p-4 bg-surface-container/40 rounded-xl border border-white/5 flex flex-col justify-between gap-3">
        <div className="space-y-3">
          <h3 className="text-xs font-semibold opacity-70 uppercase tracking-wider">Storage Nodes</h3>
          <div className="space-y-1">
            <button
              onClick={() => setFilterType('all')}
              className={`w-full text-left p-2.5 rounded-lg text-xs flex items-center gap-2.5 transition-colors cursor-pointer ${
                filterType === 'all' ? 'bg-primary/10 text-primary border border-primary/25 font-semibold' : 'bg-white/5 border border-white/5 text-on-surface-variant hover:bg-white/10'
              }`}
              id="files-filter-all"
            >
              <Folder size={14} />
              <span>All Storage (C:)</span>
            </button>
            <button
              onClick={() => setFilterType('doc')}
              className={`w-full text-left p-2.5 rounded-lg text-xs flex items-center gap-2.5 transition-colors cursor-pointer ${
                filterType === 'doc' ? 'bg-primary/10 text-primary border border-primary/25 font-semibold' : 'bg-white/5 border border-white/5 text-on-surface-variant hover:bg-white/10'
              }`}
              id="files-filter-doc"
            >
              <FileText size={14} className="text-primary" />
              <span>Documents</span>
            </button>
            <button
              onClick={() => setFilterType('sheet')}
              className={`w-full text-left p-2.5 rounded-lg text-xs flex items-center gap-2.5 transition-colors cursor-pointer ${
                filterType === 'sheet' ? 'bg-primary/10 text-primary border border-primary/25 font-semibold' : 'bg-white/5 border border-white/5 text-on-surface-variant hover:bg-white/10'
              }`}
              id="files-filter-sheet"
            >
              <FileSpreadsheet size={14} className="text-secondary" />
              <span>Spreadsheets</span>
            </button>
            <button
              onClick={() => setFilterType('pdf')}
              className={`w-full text-left p-2.5 rounded-lg text-xs flex items-center gap-2.5 transition-colors cursor-pointer ${
                filterType === 'pdf' ? 'bg-primary/10 text-primary border border-primary/25 font-semibold' : 'bg-white/5 border border-white/5 text-on-surface-variant hover:bg-white/10'
              }`}
              id="files-filter-pdf"
            >
              <FileCode size={14} className="text-error" />
              <span>Manual PDFs</span>
            </button>
            <button
              onClick={() => setFilterType('image')}
              className={`w-full text-left p-2.5 rounded-lg text-xs flex items-center gap-2.5 transition-colors cursor-pointer ${
                filterType === 'image' ? 'bg-primary/10 text-primary border border-primary/25 font-semibold' : 'bg-white/5 border border-white/5 text-on-surface-variant hover:bg-white/10'
              }`}
              id="files-filter-image"
            >
              <FileImage size={14} className="text-tertiary" />
              <span>Sketches & Photos</span>
            </button>
          </div>
        </div>

        <div className="p-3 bg-black/15 border border-white/5 rounded-lg text-[10px] text-on-surface-variant leading-normal space-y-1">
          <p className="font-semibold text-secondary flex items-center gap-1">
            <ArrowLeftRight size={10} />
            Workspace Pipeline
          </p>
          <p className="opacity-70">Saved files go to RAM memory and can be launched inside respective apps instantly.</p>
        </div>
      </div>

      {/* Main Folder Grid */}
      <div className="flex-1 bg-surface-container-low/60 rounded-xl border border-white/5 p-4 flex flex-col gap-3 overflow-hidden">
        {/* Search header bar */}
        <div className="flex items-center bg-black/25 rounded-lg border border-white/10 px-3 py-1.5 gap-2 text-xs">
          <Search size={14} className="text-on-surface-variant opacity-60" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search virtual system directory..."
            className="flex-1 bg-transparent border-0 outline-none text-xs text-on-surface font-mono"
            id="files-search-input"
          />
        </div>

        {/* File Bento Grid */}
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {filteredFiles.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center opacity-40 py-16">
              <Folder size={44} className="text-primary mb-3" />
              <p className="text-xs font-semibold">Directory Empty</p>
              <p className="text-[11px] mt-1">No files match your filter or keyword.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {filteredFiles.map((file) => (
                <div
                  key={file.name}
                  onClick={() => onOpenFile(file)}
                  className="p-3 bg-white/5 hover:bg-white/10 rounded-xl border border-white/5 hover:border-primary/20 transition-all cursor-pointer flex flex-col justify-between group h-32 relative overflow-hidden"
                  id={`file-item-${file.name.replace(/[^a-zA-Z0-9]/g, '_')}`}
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2.5 bg-black/20 rounded-lg">
                      {fileTypeIcons[file.type]}
                    </div>
                    <div className="truncate pr-4">
                      <h4 className="text-xs font-semibold truncate text-white mb-0.5 leading-normal" title={file.name}>
                        {file.name}
                      </h4>
                      <p className="text-[10px] text-on-surface-variant opacity-60 font-mono">
                        {getReadableType(file.type)}
                      </p>
                    </div>
                  </div>

                  <div className="flex justify-between items-end border-t border-white/5 pt-2 mt-2 font-mono text-[9px] text-on-surface-variant opacity-50">
                    <div className="flex flex-col">
                      <span>Size: {file.size}</span>
                      <span>Modified: {file.updatedAt}</span>
                    </div>

                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all">
                      {/* Delete option for user files */}
                      {file.name !== 'Lumina_Systems_Specs.doc' &&
                       file.name !== 'Core_Kiosk_Telemetry.sheet' &&
                       file.name !== 'Lumina_Kiosk_Operator_Manual.pdf' && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteFile(file.name);
                          }}
                          className="p-1.5 hover:bg-error-container/30 border border-transparent hover:border-error-container/50 hover:text-error rounded transition-all"
                          title="Delete File"
                          id={`delete-file-${file.name.replace(/[^a-zA-Z0-9]/g, '_')}`}
                        >
                          <Trash2 size={12} />
                        </button>
                      )}
                      
                      <div className="p-1 bg-primary/20 border border-primary/20 rounded text-primary" title="Launch File">
                        <ExternalLink size={10} />
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Informative Footer */}
        <div className="flex items-center justify-between text-[11px] text-on-surface-variant opacity-60 font-mono px-1">
          <span>Total Virtual Nodes: {files.length} items</span>
          <span className="flex items-center gap-1">
            <HelpCircle size={10} />
            Double-click or click launch to boot files inside tools.
          </span>
        </div>
      </div>
    </div>
  );
}
