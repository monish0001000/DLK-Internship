import React, { useRef, useState, useEffect } from 'react';
import { Palette, Eraser, Brush, Trash2, Undo, Redo, Save, HelpCircle, Check } from 'lucide-react';

interface PaintAppProps {
  onSaveFile?: (name: string, type: 'image', content: string) => void;
}

export default function PaintApp({ onSaveFile }: PaintAppProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [color, setColor] = useState('#b4e4ff'); // Lumina Primary as default
  const [brushSize, setBrushSize] = useState(5);
  const [tool, setTool] = useState<'brush' | 'eraser'>('brush');
  const [isDrawing, setIsDrawing] = useState(false);
  const [saveName, setSaveName] = useState('My_Sketch');
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Undo/Redo stacks
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  // Default color list (harmonized with Lumina theme)
  const defaultColors = [
    '#b4e4ff', // Primary
    '#65f897', // Success (Tertiary)
    '#ffb4ab', // Error
    '#a3c9ff', // Secondary
    '#ffd700', // Warning Gold
    '#ff79c6', // Pink
    '#ffffff', // White
    '#121414', // Background/Dark
  ];

  // Set up canvas default transparent white or filled background on mount
  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        // Fill canvas with deep charcoal background to look beautiful
        ctx.fillStyle = '#1e2020';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Save initial state
        const initialData = canvas.toDataURL();
        setHistory([initialData]);
        setHistoryIndex(0);
      }
    }
  }, []);

  // Update brush characteristics when color/size/tool change
  const saveState = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      const dataUrl = canvas.toDataURL();
      const nextHistory = history.slice(0, historyIndex + 1);
      nextHistory.push(dataUrl);
      setHistory(nextHistory);
      setHistoryIndex(nextHistory.length - 1);
    }
  };

  const getCoordinates = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };

    const rect = canvas.getBoundingClientRect();
    
    // Support touch events
    if ('touches' in e) {
      if (e.touches.length === 0) return { x: 0, y: 0 };
      const touch = e.touches[0];
      return {
        x: touch.clientX - rect.left,
        y: touch.clientY - rect.top
      };
    } else {
      return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      };
    }
  };

  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { x, y } = getCoordinates(e);

    ctx.beginPath();
    ctx.moveTo(x, y);
    setIsDrawing(true);
    
    // Slight dot on click
    ctx.fillStyle = tool === 'eraser' ? '#1e2020' : color;
    ctx.arc(x, y, brushSize / 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(x, y);
  };

  const draw = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    e.preventDefault();

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { x, y } = getCoordinates(e);

    ctx.lineWidth = brushSize;
    ctx.strokeStyle = tool === 'eraser' ? '#1e2020' : color;
    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const stopDrawing = () => {
    if (isDrawing) {
      setIsDrawing(false);
      saveState();
    }
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.fillStyle = '#1e2020';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        saveState();
      }
    }
  };

  const handleUndo = () => {
    if (historyIndex > 0) {
      const prevIndex = historyIndex - 1;
      setHistoryIndex(prevIndex);
      loadHistoryState(prevIndex);
    }
  };

  const handleRedo = () => {
    if (historyIndex < history.length - 1) {
      const nextIndex = historyIndex + 1;
      setHistoryIndex(nextIndex);
      loadHistoryState(nextIndex);
    }
  };

  const loadHistoryState = (index: number) => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        const img = new Image();
        img.src = history[index];
        img.onload = () => {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0);
        };
      }
    }
  };

  const handleSave = () => {
    const canvas = canvasRef.current;
    if (canvas && onSaveFile) {
      const filename = saveName.trim().endsWith('.png') ? saveName.trim() : `${saveName.trim()}.png`;
      onSaveFile(filename, 'image', canvas.toDataURL());
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row h-full gap-4 text-on-surface">
      {/* Control Panel */}
      <div className="w-full lg:w-64 flex flex-col gap-3 p-4 bg-surface-container/40 rounded-xl border border-black/10 dark:border-white/5">
        <div>
          <h3 className="text-sm font-semibold opacity-70 uppercase tracking-wider mb-2">Tools</h3>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setTool('brush')}
              className={`p-2.5 rounded-lg border flex items-center justify-center gap-2 transition-all cursor-pointer ${
                tool === 'brush'
                  ? 'bg-primary text-on-primary border-primary font-semibold'
                  : 'bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 border-black/10 dark:border-white/5 text-on-surface-variant'
              }`}
              id="paint-tool-brush"
            >
              <Brush size={16} />
              <span className="text-xs">Brush</span>
            </button>
            <button
              onClick={() => setTool('eraser')}
              className={`p-2.5 rounded-lg border flex items-center justify-center gap-2 transition-all cursor-pointer ${
                tool === 'eraser'
                  ? 'bg-primary text-on-primary border-primary font-semibold'
                  : 'bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 border-black/10 dark:border-white/5 text-on-surface-variant'
              }`}
              id="paint-tool-eraser"
            >
              <Eraser size={16} />
              <span className="text-xs">Eraser</span>
            </button>
          </div>
        </div>

        {/* Brush Size */}
        <div>
          <div className="flex justify-between items-center mb-1 text-xs">
            <span className="font-semibold opacity-70 uppercase tracking-wider">Size</span>
            <span className="font-mono text-primary font-semibold">{brushSize}px</span>
          </div>
          <input
            type="range"
            min="1"
            max="40"
            value={brushSize}
            onChange={(e) => setBrushSize(parseInt(e.target.value))}
            className="w-full accent-primary h-1 bg-black/10 dark:bg-white/10 rounded-lg appearance-none cursor-pointer"
            id="paint-size-slider"
          />
        </div>

        {/* Color Palette */}
        {tool === 'brush' && (
          <div>
            <h3 className="text-sm font-semibold opacity-70 uppercase tracking-wider mb-2">Palette</h3>
            <div className="grid grid-cols-4 gap-2 mb-2">
              {defaultColors.map((c) => (
                <button
                  key={c}
                  onClick={() => setColor(c)}
                  className={`w-10 h-10 rounded-lg transition-transform border cursor-pointer flex items-center justify-center ${
                    color === c ? 'scale-110 border-white shadow-md' : 'border-black/20 hover:scale-105'
                  }`}
                  style={{ backgroundColor: c }}
                  title={c}
                  id={`paint-color-${c.replace('#', '')}`}
                >
                  {color === c && (
                    <span className={`w-2 h-2 rounded-full ${c === '#ffffff' ? 'bg-black' : 'bg-white'}`} />
                  )}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2 mt-2 bg-black/5 dark:bg-black/15 p-2 rounded-lg border border-black/10 dark:border-white/5">
              <input
                type="color"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                className="w-7 h-7 rounded border-0 cursor-pointer p-0 bg-transparent"
                id="paint-color-custom"
              />
              <span className="text-xs font-mono text-on-surface-variant">{color.toUpperCase()}</span>
            </div>
          </div>
        )}

        {/* History Controls */}
        <div>
          <h3 className="text-sm font-semibold opacity-70 uppercase tracking-wider mb-2">History</h3>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={handleUndo}
              disabled={historyIndex <= 0}
              className="p-2 bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 disabled:opacity-40 disabled:hover:bg-black/5 dark:disabled:hover:bg-white/5 border border-black/10 dark:border-white/5 rounded-lg flex items-center justify-center gap-1.5 text-xs text-on-surface-variant transition-colors cursor-pointer"
              id="paint-undo"
            >
              <Undo size={14} />
              Undo
            </button>
            <button
              onClick={handleRedo}
              disabled={historyIndex >= history.length - 1}
              className="p-2 bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 disabled:opacity-40 disabled:hover:bg-black/5 dark:disabled:hover:bg-white/5 border border-black/10 dark:border-white/5 rounded-lg flex items-center justify-center gap-1.5 text-xs text-on-surface-variant transition-colors cursor-pointer"
              id="paint-redo"
            >
              <Redo size={14} />
              Redo
            </button>
          </div>
        </div>

        {/* Save Work */}
        <div className="mt-auto pt-3 border-t border-black/10 dark:border-white/5">
          <h3 className="text-xs font-semibold opacity-70 uppercase tracking-wider mb-2">Save to Kiosk Files</h3>
          <div className="space-y-2">
            <input
              type="text"
              value={saveName}
              onChange={(e) => setSaveName(e.target.value.replace(/[^a-zA-Z0-9_-]/g, ''))}
              placeholder="sketch_name"
              className="w-full text-xs bg-black/5 dark:bg-black/30 border border-black/10 dark:border-white/10 focus:border-primary/50 rounded p-2 text-on-surface font-mono outline-none"
              id="paint-save-name"
            />
            <button
              onClick={handleSave}
              className={`w-full p-2.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                saveSuccess
                  ? 'bg-tertiary text-on-tertiary shadow-[0_0_12px_rgba(101,248,151,0.3)]'
                  : 'bg-primary hover:bg-primary-container text-on-primary'
              }`}
              id="paint-save-btn"
            >
              {saveSuccess ? (
                <>
                  <Check size={14} />
                  Saved to Explorer!
                </>
              ) : (
                <>
                  <Save size={14} />
                  Export to File Explorer
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Canvas Drawing Board */}
      <div className="flex-1 bg-surface-container-low/60 rounded-xl border border-black/10 dark:border-white/5 p-3 flex flex-col items-center justify-center relative overflow-hidden">
        {/* Helper info overlay */}
        <div className="absolute top-4 left-4 z-10 flex items-center gap-1 bg-black/40 px-2.5 py-1 rounded-full text-[10px] text-on-surface-variant opacity-80 backdrop-blur-sm">
          <HelpCircle size={10} className="text-primary" />
          <span>Click and drag to sketch. Canvas will scale on mobile.</span>
        </div>

        <button
          onClick={clearCanvas}
          className="absolute top-4 right-4 z-10 p-2 bg-black/40 hover:bg-error-container/30 border border-black/10 dark:border-white/5 hover:border-error-container/50 text-on-surface-variant hover:text-error rounded-full transition-all backdrop-blur-sm cursor-pointer"
          title="Clear Canvas"
          id="paint-clear"
        >
          <Trash2 size={14} />
        </button>

        {/* Main interactive Canvas */}
        <div className="w-full h-full min-h-[320px] max-h-[500px] border border-black/10 dark:border-white/10 rounded-lg overflow-hidden bg-[#1e2020] flex items-center justify-center">
          <canvas
            ref={canvasRef}
            width={640}
            height={440}
            onMouseDown={startDrawing}
            onMouseMove={draw}
            onMouseUp={stopDrawing}
            onMouseLeave={stopDrawing}
            onTouchStart={startDrawing}
            onTouchMove={draw}
            onTouchEnd={stopDrawing}
            className="cursor-crosshair max-w-full max-h-full object-contain shadow-lg"
          />
        </div>
      </div>
    </div>
  );
}
