import React, { useState, useEffect } from 'react';
import { PenTool, Trash2, Plus, Calendar, HelpCircle, Save, Check } from 'lucide-react';

interface Note {
  id: string;
  title: string;
  content: string;
  date: string;
}

interface NotepadProps {
  onSaveFile?: (name: string, type: 'text', content: string) => void;
  addLog?: (msg: string) => void;
}

export default function Notepad({ onSaveFile, addLog }: NotepadProps) {
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Initialize with some default note
  useEffect(() => {
    const defaultNotes: Note[] = [
      {
        id: '1',
        title: 'Quick Scratchpad',
        content: `# KIOSK SCRATCHPAD LOG
Date: ${new Date().toLocaleDateString()}
Temp Status: Stable

- Enforce Mode 1 DNS restrictions.
- Ensure Paint images export properly.
- Run terminal diagnostic checks weekly.`,
        date: new Date().toLocaleDateString()
      }
    ];
    setNotes(defaultNotes);
    setSelectedNoteId('1');
    setTitle(defaultNotes[0].title);
    setContent(defaultNotes[0].content);
  }, []);

  const handleSelectNote = (id: string) => {
    const note = notes.find(n => n.id === id);
    if (note) {
      setSelectedNoteId(id);
      setTitle(note.title);
      setContent(note.content);
    }
  };

  const handleAddNote = () => {
    const newNote: Note = {
      id: Date.now().toString(),
      title: 'New Note',
      content: '',
      date: new Date().toLocaleDateString()
    };
    setNotes([newNote, ...notes]);
    setSelectedNoteId(newNote.id);
    setTitle(newNote.title);
    setContent(newNote.content);
    if (addLog) addLog('Created new empty scratchpad note.');
  };

  const handleDeleteNote = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = notes.filter(n => n.id !== id);
    setNotes(updated);
    if (addLog) addLog('Deleted scratchpad note.');

    if (selectedNoteId === id) {
      if (updated.length > 0) {
        setSelectedNoteId(updated[0].id);
        setTitle(updated[0].title);
        setContent(updated[0].content);
      } else {
        setSelectedNoteId(null);
        setTitle('');
        setContent('');
      }
    }
  };

  const handleSave = () => {
    if (!selectedNoteId) return;
    
    // Save locally
    const updatedNotes = notes.map(n => {
      if (n.id === selectedNoteId) {
        return { ...n, title, content, date: new Date().toLocaleDateString() };
      }
      return n;
    });
    setNotes(updatedNotes);

    // Export to file system too!
    const filename = `${title.trim().replace(/[^a-zA-Z0-9_-]/g, '_')}.txt`;
    if (onSaveFile) {
      onSaveFile(filename, 'text', content);
      setSaveSuccess(true);
      if (addLog) addLog(`Scratchpad document exported to files: ${filename}`);
      setTimeout(() => setSaveSuccess(false), 2000);
    }
  };

  return (
    <div className="flex flex-col md:flex-row h-full gap-4 text-on-surface">
      {/* Sidebar - Note List */}
      <div className="w-full md:w-64 p-4 bg-surface-container/40 rounded-xl border border-black/10 dark:border-white/5 flex flex-col justify-between gap-3">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold opacity-70 uppercase tracking-wider">Scratchpad List</h3>
            <button
              onClick={handleAddNote}
              className="p-1.5 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 rounded-lg flex items-center justify-center transition-colors cursor-pointer"
              title="Add Note"
              id="notepad-add"
            >
              <Plus size={12} />
            </button>
          </div>

          <div className="space-y-1.5 max-h-60 overflow-y-auto custom-scrollbar">
            {notes.map(note => {
              const isSelected = selectedNoteId === note.id;
              return (
                <div
                  key={note.id}
                  onClick={() => handleSelectNote(note.id)}
                  className={`p-2.5 rounded-lg border transition-all cursor-pointer flex justify-between items-center group ${
                    isSelected
                      ? 'bg-primary/15 border-primary/40 text-primary font-bold'
                      : 'bg-black/5 dark:bg-white/5 border-black/5 dark:border-white/5 hover:bg-black/10 dark:hover:bg-white/10 text-on-surface-variant hover:text-on-surface'
                  }`}
                  id={`notepad-note-${note.id}`}
                >
                  <div className="truncate flex-1 pr-2">
                    <p className="text-xs font-semibold truncate leading-normal">{note.title}</p>
                    <span className="text-[10px] opacity-50 flex items-center gap-1 mt-0.5 font-mono">
                      <Calendar size={8} />
                      {note.date}
                    </span>
                  </div>
                  <button
                    onClick={(e) => handleDeleteNote(note.id, e)}
                    className="p-1 text-on-surface-variant hover:text-error opacity-0 group-hover:opacity-100 transition-all rounded"
                    title="Delete note"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        <p className="text-[10px] text-on-surface-variant opacity-40 leading-normal">
          Keep raw diagnostic logs, credentials, or simple clipboard segments safe here.
        </p>
      </div>

      {/* Editor Space */}
      <div className="flex-1 bg-surface-container-low/60 rounded-xl border border-black/10 dark:border-white/5 p-4 flex flex-col gap-3">
        {selectedNoteId ? (
          <>
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-black/10 dark:border-white/5 pb-3">
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Note Title"
                className="bg-transparent border-0 font-sans text-sm font-semibold text-on-surface outline-none p-0 focus:ring-0 w-full sm:w-auto"
                id="notepad-title-input"
              />

              <button
                onClick={handleSave}
                className={`p-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-all px-3 cursor-pointer ${
                  saveSuccess
                    ? 'bg-tertiary text-on-tertiary shadow-[0_0_10px_rgba(101,248,151,0.2)]'
                    : 'bg-primary hover:bg-primary/80 text-on-primary'
                }`}
                id="notepad-save"
              >
                {saveSuccess ? (
                  <>
                    <Check size={12} />
                    Exported!
                  </>
                ) : (
                  <>
                    <Save size={12} />
                    Export to Files (.txt)
                  </>
                )}
              </button>
            </div>

            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Start drafting content log..."
              className="flex-1 bg-transparent border-0 outline-none p-0 text-xs font-mono text-on-surface leading-relaxed resize-none focus:ring-0"
              id="notepad-textarea"
            />
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center opacity-40 py-10">
            <PenTool size={36} className="text-primary mb-3" />
            <p className="text-xs">No active note selected.</p>
            <p className="text-[11px] mt-1">Click '+' to draft a scratchpad record.</p>
          </div>
        )}

        <div className="flex items-center justify-between text-[11px] text-on-surface-variant opacity-60 font-mono px-1 border-t border-black/10 dark:border-white/5 pt-2">
          <span>Length: {content.length} characters</span>
          <span className="flex items-center gap-1">
            <HelpCircle size={10} />
            Export saves as txt inside the local File Explorer.
          </span>
        </div>
      </div>
    </div>
  );
}
