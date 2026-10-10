import React, { useRef, useState, useEffect } from 'react';
import {
  Camera,
  Video,
  RefreshCw,
  Sparkles,
  AlertCircle,
  FileImage,
  ShieldCheck,
  Check,
  Grid3X3,
  Sliders,
  Settings,
  Timer,
  Volume2,
  VolumeX,
  Maximize2,
  Trash2,
  Download,
  X,
  ChevronLeft,
  ChevronRight,
  Eye,
  CameraOff
} from 'lucide-react';

interface CameraAppProps {
  onSaveFile?: (name: string, type: 'image', content: string) => void;
  addLog?: (msg: string) => void;
}

type FilterType = 'none' | 'grayscale' | 'sepia' | 'invert' | 'emerald' | 'cyberpunk' | 'warm' | 'cool';
type AspectRatio = '16:9' | '4:3';
type Resolution = '4K Ultra HD' | '1080p Full HD' | '720p HD';
type GridType = 'none' | 'thirds' | 'golden';

export default function CameraApp({ onSaveFile, addLog }: CameraAppProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const fallbackCanvasRef = useRef<HTMLCanvasElement | null>(null);

  // Core camera state
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [cameraState, setCameraState] = useState<'requesting' | 'active' | 'blocked' | 'unsupported'>('requesting');
  const [mode, setMode] = useState<'photo' | 'video'>('photo');
  const [filter, setFilter] = useState<FilterType>('none');
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>('16:9');
  const [resolution, setResolution] = useState<Resolution>('1080p Full HD');
  const [gridLines, setGridLines] = useState<GridType>('none');
  const [timerDelay, setTimerDelay] = useState<number>(0);
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);

  // Timer, flash and recording state
  const [countdown, setCountdown] = useState<number | null>(null);
  const [flashActive, setFlashActive] = useState<boolean>(false);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordDuration, setRecordDuration] = useState<number>(0);
  const [savedSnaps, setSavedSnaps] = useState<string[]>([]);
  const [galleryOpenIndex, setGalleryOpenIndex] = useState<number | null>(null);
  const [snapSuccess, setSnapSuccess] = useState<boolean>(false);

  // Simulator tracking parameters (for high-fidelity rotating terrain / focus tracking)
  const [focusPoint, setFocusPoint] = useState<{ x: number; y: number }>({ x: 320, y: 220 });
  const [showFocusRing, setShowFocusRing] = useState<boolean>(false);
  const [simAngle, setSimAngle] = useState<number>(0);

  // Initialize stream
  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  // Video recording duration tracker
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordDuration((prev) => prev + 1);
      }, 1000);
    } else {
      setRecordDuration(0);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  // Simulator background animation loop
  useEffect(() => {
    let animationId: number;
    let angle = 0;

    const drawSimulator = () => {
      angle += 0.015;
      setSimAngle(angle);

      const canvas = fallbackCanvasRef.current;
      if (canvas && cameraState !== 'active') {
        const ctx = canvas.getContext('2d');
        if (ctx) {
          const w = canvas.width;
          const h = canvas.height;

          // Clear with high contrast space background
          ctx.fillStyle = '#0a0d0d';
          ctx.fillRect(0, 0, w, h);

          // Draw grid network lines matching aspect ratio
          ctx.strokeStyle = 'rgba(96, 205, 255, 0.03)';
          ctx.lineWidth = 1;
          const spacing = 30;
          for (let x = 0; x < w; x += spacing) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, h);
            ctx.stroke();
          }
          for (let y = 0; y < h; y += spacing) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(w, y);
            ctx.stroke();
          }

          // Draw simulated scenic mountains / futuristic horizon
          ctx.strokeStyle = 'rgba(96, 205, 255, 0.15)';
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.moveTo(0, h * 0.7);
          for (let x = 0; x <= w; x += 10) {
            const yOffset = Math.sin(x * 0.01 + angle) * 20 + Math.cos(x * 0.005 - angle * 0.5) * 15;
            ctx.lineTo(x, h * 0.7 + yOffset);
          }
          ctx.stroke();

          // Draw orbiting high-tech satellites / focus target spheres
          const satX = w / 2 + Math.cos(angle * 0.8) * 120;
          const satY = h / 2 - 30 + Math.sin(angle * 1.2) * 50;

          ctx.fillStyle = 'rgba(96, 205, 255, 0.2)';
          ctx.beginPath();
          ctx.arc(satX, satY, 15, 0, Math.PI * 2);
          ctx.fill();
          ctx.strokeStyle = '#60cdff';
          ctx.lineWidth = 1;
          ctx.stroke();

          // Draw lens flare simulation
          ctx.fillStyle = 'rgba(96, 205, 255, 0.04)';
          ctx.beginPath();
          ctx.arc(satX - 40, satY + 20, 30, 0, Math.PI * 2);
          ctx.fill();

          // If showing a focus ring, draw a circle around focusPoint
          if (showFocusRing) {
            ctx.strokeStyle = '#34d399';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(focusPoint.x, focusPoint.y, 25, 0, Math.PI * 2);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(focusPoint.x - 35, focusPoint.y);
            ctx.lineTo(focusPoint.x + 35, focusPoint.y);
            ctx.moveTo(focusPoint.x, focusPoint.y - 35);
            ctx.lineTo(focusPoint.x, focusPoint.y + 35);
            ctx.stroke();
          }
        }
      }
      animationId = requestAnimationFrame(drawSimulator);
    };

    drawSimulator();
    return () => cancelAnimationFrame(animationId);
  }, [cameraState, focusPoint, showFocusRing]);

  // Audio synthesis triggers using standard web audio
  const playBeep = (freq = 880, duration = 0.05) => {
    if (!soundEnabled) return;
    try {
      const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch (e) {
      console.warn('Audio synthesis warning:', e);
    }
  };

  const playShutterSound = () => {
    if (!soundEnabled) return;
    try {
      const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const bufferSize = ctx.sampleRate * 0.12;
      const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
      }
      const noise = ctx.createBufferSource();
      noise.buffer = buffer;
      const filter = ctx.createBiquadFilter();
      filter.type = 'highpass';
      filter.frequency.setValueAtTime(1200, ctx.currentTime);
      const gain = ctx.createGain();
      gain.gain.setValueAtTime(0.35, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
      noise.connect(filter);
      filter.connect(gain);
      gain.connect(ctx.destination);
      noise.start();
    } catch (e) {
      console.warn('Shutter sound failed:', e);
    }
  };

  const playRecordSound = (start: boolean) => {
    if (!soundEnabled) return;
    playBeep(start ? 660 : 440, 0.15);
    setTimeout(() => {
      playBeep(start ? 880 : 330, 0.15);
    }, 150);
  };

  const startCamera = async () => {
    setCameraState('requesting');
    if (addLog) addLog('Initializing Windows Camera Pipeline...');
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setCameraState('unsupported');
        if (addLog) addLog('MediaDevices API not supported by client sandbox.');
        return;
      }
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720, facingMode: 'user' },
        audio: false,
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setCameraState('active');
      if (addLog) addLog('Windows Live Camera Device recognized and streaming.');
    } catch (err) {
      setCameraState('blocked');
      if (addLog) addLog('Physical camera blocked or denied. Launching virtual high-definition emulator.');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
  };

  // Focus interactive click on viewfinder
  const handleViewfinderClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setFocusPoint({ x, y });
    setShowFocusRing(true);
    playBeep(1200, 0.03);
    setTimeout(() => {
      setShowFocusRing(false);
    }, 1000);
  };

  // Shutter trigger with timer countdown
  const triggerShutter = () => {
    if (countdown !== null || isRecording) return;

    if (timerDelay > 0) {
      let currentCount = timerDelay;
      setCountdown(currentCount);
      playBeep(880, 0.06);

      const interval = setInterval(() => {
        currentCount -= 1;
        if (currentCount <= 0) {
          clearInterval(interval);
          setCountdown(null);
          executeSnap();
        } else {
          setCountdown(currentCount);
          playBeep(880, 0.06);
        }
      }, 1000);
    } else {
      executeSnap();
    }
  };

  // Video capture trigger
  const triggerRecording = () => {
    if (countdown !== null) return;
    if (isRecording) {
      // Stop recording and save a video snapshot
      setIsRecording(false);
      playRecordSound(false);
      executeSnap(true);
      if (addLog) addLog('Stopped video recording session.');
    } else {
      // Start recording
      setIsRecording(true);
      playRecordSound(true);
      if (addLog) addLog('Started high-fidelity simulated MP4 video capture.');
    }
  };

  // Final capture & file storage compilation
  const executeSnap = (isVideoFrame = false) => {
    // Shutter flash effect
    setFlashActive(true);
    playShutterSound();
    setTimeout(() => setFlashActive(false), 150);

    let finalDataUrl = '';
    const namePrefix = isVideoFrame ? 'Video_Clip' : 'Camera_Snap';
    const snapFilename = `${namePrefix}_${savedSnaps.length + 1}.png`;

    if (cameraState === 'active' && videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        // Clear and draw active video frame
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Apply selected digital filters
        applyFiltersToCtx(ctx, canvas.width, canvas.height);
        finalDataUrl = canvas.toDataURL('image/png');
      }
    } else {
      // Draw simulated frame on secondary canvas
      const canvas = canvasRef.current;
      const fallback = fallbackCanvasRef.current;
      if (canvas && fallback) {
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(fallback, 0, 0, canvas.width, canvas.height);

          // Add some cool telemetry HUD overlays directly into the saved file
          ctx.fillStyle = '#ffffff';
          ctx.font = '12px "JetBrains Mono"';
          ctx.fillText(`CAPTURE MODE: ${mode.toUpperCase()}`, 30, 40);
          ctx.fillText(`RES: ${resolution}`, 30, 60);
          ctx.fillText(`FILTER: ${filter.toUpperCase()}`, 30, 80);
          ctx.fillText(`TIMESTAMP: ${new Date().toLocaleTimeString()}`, 30, 100);

          if (isVideoFrame) {
            ctx.fillStyle = '#ef4444';
            ctx.beginPath();
            ctx.arc(35, 125, 6, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#ffffff';
            ctx.fillText('RECORDED STREAM EXPORT', 50, 129);
          }

          applyFiltersToCtx(ctx, canvas.width, canvas.height);
          finalDataUrl = canvas.toDataURL('image/png');
        }
      }
    }

    if (finalDataUrl) {
      setSavedSnaps((prev) => [...prev, finalDataUrl]);
      setSnapSuccess(true);
      setTimeout(() => setSnapSuccess(false), 1500);

      if (onSaveFile) {
        onSaveFile(snapFilename, 'image', finalDataUrl);
      }
      if (addLog) {
        addLog(`Camera successfully saved ${isVideoFrame ? 'recording' : 'photograph'} as: ${snapFilename}`);
      }
    }
  };

  // Pixel filters mapper helper
  const applyFiltersToCtx = (ctx: CanvasRenderingContext2D, w: number, h: number) => {
    if (filter === 'none') return;
    const imgData = ctx.getImageData(0, 0, w, h);
    const data = imgData.data;

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];

      if (filter === 'grayscale') {
        const gray = 0.3 * r + 0.59 * g + 0.11 * b;
        data[i] = gray;
        data[i + 1] = gray;
        data[i + 2] = gray;
      } else if (filter === 'sepia') {
        data[i] = Math.min(255, r * 0.393 + g * 0.769 + b * 0.189);
        data[i + 1] = Math.min(255, r * 0.349 + g * 0.686 + b * 0.168);
        data[i + 2] = Math.min(255, r * 0.272 + g * 0.534 + b * 0.131);
      } else if (filter === 'invert') {
        data[i] = 255 - r;
        data[i + 1] = 255 - g;
        data[i + 2] = 255 - b;
      } else if (filter === 'emerald') {
        const gray = 0.3 * r + 0.59 * g + 0.11 * b;
        data[i] = gray * 0.4;
        data[i + 1] = gray * 0.95;
        data[i + 2] = gray * 0.55;
      } else if (filter === 'cyberpunk') {
        data[i] = r * 0.85;
        data[i + 1] = g * 0.15;
        data[i + 2] = b * 0.95;
      } else if (filter === 'warm') {
        data[i] = Math.min(255, r * 1.15);
        data[i + 2] = Math.max(0, b * 0.88);
      } else if (filter === 'cool') {
        data[i] = Math.max(0, r * 0.85);
        data[i + 2] = Math.min(255, b * 1.18);
      }
    }
    ctx.putImageData(imgData, 0, 0);
  };

  // CSS Filter values for interactive browser live display
  const filterClasses: Record<FilterType, string> = {
    none: '',
    grayscale: 'grayscale',
    sepia: 'sepia',
    invert: 'invert',
    emerald: 'grayscale hue-rotate-[100deg] saturate-[200%] brightness-[90%]',
    cyberpunk: 'hue-rotate-[290deg] saturate-[220%] contrast-[110%]',
    warm: 'sepia-[20%] saturate-[110%] brightness-[102%]',
    cool: 'hue-rotate-[15deg] saturate-[110%] brightness-[98%]',
  };

  // Clean formatted time string for video record HUD
  const formatRecordTime = (totalSec: number) => {
    const mins = Math.floor(totalSec / 60);
    const secs = totalSec % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Export downloaded local image directly
  const exportImageDownload = (imgUrl: string, index: number) => {
    const link = document.createElement('a');
    link.href = imgUrl;
    link.download = `WindowsCamera_Capture_${index + 1}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    if (addLog) addLog(`Downloaded camera snapshot: WindowsCamera_Capture_${index + 1}.png`);
  };

  const deleteSnapIndex = (index: number) => {
    const updated = savedSnaps.filter((_, i) => i !== index);
    setSavedSnaps(updated);
    if (galleryOpenIndex === index) {
      setGalleryOpenIndex(updated.length > 0 ? Math.max(0, index - 1) : null);
    }
    playBeep(400, 0.08);
    if (addLog) addLog('Deleted photograph from camera roll buffer.');
  };

  return (
    <div className="flex flex-col lg:flex-row h-full gap-5 text-on-surface select-none">
      {/* 1. Sidebar Configurations Panel */}
      <aside className="w-full lg:w-72 flex flex-col gap-4 p-4 bg-surface-container/40 rounded-2xl border border-black/10 dark:border-white/5 shrink-0">
        
        {/* Connection Diagnostics HUD */}
        <div>
          <h3 className="text-xs font-bold opacity-60 uppercase tracking-widest mb-2 flex items-center gap-1">
            <Settings size={12} className="text-primary" />
            Device Controller
          </h3>
          <div className="flex items-center gap-2 p-3 bg-black/5 dark:bg-black/20 rounded-xl border border-black/10 dark:border-white/5">
            {cameraState === 'active' ? (
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-tertiary status-glow animate-pulse" />
                <span className="text-xs font-semibold text-tertiary">HD Live Webcam Engaged</span>
              </div>
            ) : cameraState === 'requesting' ? (
              <div className="flex items-center gap-2">
                <RefreshCw size={13} className="animate-spin text-primary" />
                <span className="text-xs text-primary font-semibold">Configuring Frame Grabber...</span>
              </div>
            ) : (
              <div className="flex items-center gap-1.5">
                <AlertCircle size={14} className="text-primary" />
                <span className="text-xs text-primary font-bold">HD Virtual Cam Active</span>
              </div>
            )}
          </div>
        </div>

        {/* Shutter Countdown Settings */}
        <div>
          <h3 className="text-xs font-bold opacity-60 uppercase tracking-widest mb-2 flex items-center gap-1">
            <Timer size={12} className="text-primary" />
            Self Timer Delay
          </h3>
          <div className="grid grid-cols-4 gap-1">
            {[0, 2, 5, 10].map((sec) => (
              <button
                key={sec}
                onClick={() => {
                  setTimerDelay(sec);
                  playBeep(700, 0.04);
                }}
                className={`p-2 rounded-lg text-xs font-mono border cursor-pointer transition-all ${
                  timerDelay === sec
                    ? 'bg-primary text-on-primary border-primary font-bold'
                    : 'bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 border-black/10 dark:border-white/5'
                }`}
                id={`cam-timer-${sec}`}
              >
                {sec === 0 ? 'Off' : `${sec}s`}
              </button>
            ))}
          </div>
        </div>

        {/* Viewfinder Gridlines Option */}
        <div>
          <h3 className="text-xs font-bold opacity-60 uppercase tracking-widest mb-2 flex items-center gap-1">
            <Grid3X3 size={12} className="text-primary" />
            Grid Overlays
          </h3>
          <div className="grid grid-cols-3 gap-1">
            {[
              { id: 'none', label: 'None' },
              { id: 'thirds', label: '3x3 Grid' },
              { id: 'golden', label: 'Golden' },
            ].map((g) => (
              <button
                key={g.id}
                onClick={() => {
                  setGridLines(g.id as GridType);
                  playBeep(700, 0.04);
                }}
                className={`p-2 rounded-lg text-xs border cursor-pointer transition-all ${
                  gridLines === g.id
                    ? 'bg-primary text-on-primary border-primary font-bold'
                    : 'bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 border-black/10 dark:border-white/5'
                }`}
                id={`cam-grid-${g.id}`}
              >
                {g.label}
              </button>
            ))}
          </div>
        </div>

        {/* Filters and Creative Presets */}
        <div>
          <h3 className="text-xs font-bold opacity-60 uppercase tracking-widest mb-2 flex items-center gap-1">
            <Sparkles size={12} className="text-primary" />
            Image Presets
          </h3>
          <div className="grid grid-cols-2 gap-1.5 max-h-40 overflow-y-auto custom-scrollbar pr-1">
            {[
              { id: 'none', label: 'Default' },
              { id: 'grayscale', label: 'Noir Black' },
              { id: 'sepia', label: 'Vintage Sepia' },
              { id: 'invert', label: 'Inverted' },
              { id: 'emerald', label: 'Emerald Matrix' },
              { id: 'cyberpunk', label: 'Neon Cyber' },
              { id: 'warm', label: 'Warm Sunlight' },
              { id: 'cool', label: 'Cool Marine' },
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => {
                  setFilter(f.id as FilterType);
                  playBeep(900, 0.03);
                }}
                className={`p-2 text-left px-3 rounded-lg text-xs font-sans border cursor-pointer transition-all truncate ${
                  filter === f.id
                    ? 'bg-primary/20 text-primary border-primary font-semibold'
                    : 'bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 border-black/10 dark:border-white/5 text-on-surface-variant'
                }`}
                id={`cam-preset-${f.id}`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Advanced Hardware Specifications */}
        <div className="mt-auto space-y-2 border-t border-black/10 dark:border-white/5 pt-3">
          <div className="flex justify-between text-[11px] font-mono opacity-60">
            <span>Aspect Ratio:</span>
            <select
              value={aspectRatio}
              onChange={(e) => {
                setAspectRatio(e.target.value as AspectRatio);
                playBeep(600, 0.05);
              }}
              className="bg-transparent text-primary border-0 outline-none cursor-pointer font-bold"
              id="cam-aspect-ratio"
            >
              <option value="16:9" className="bg-surface-bright text-on-surface">16:9 Wide</option>
              <option value="4:3" className="bg-surface-bright text-on-surface">4:3 Std</option>
            </select>
          </div>

          <div className="flex justify-between text-[11px] font-mono opacity-60">
            <span>Video Res:</span>
            <select
              value={resolution}
              onChange={(e) => {
                setResolution(e.target.value as Resolution);
                playBeep(600, 0.05);
              }}
              className="bg-transparent text-primary border-0 outline-none cursor-pointer font-bold"
              id="cam-resolution"
            >
              <option value="4K Ultra HD" className="bg-surface-bright text-on-surface">3840x2160 (4K)</option>
              <option value="1080p Full HD" className="bg-surface-bright text-on-surface">1920x1080 (1080p)</option>
              <option value="720p HD" className="bg-surface-bright text-on-surface">1280x720 (720p)</option>
            </select>
          </div>

          <div className="flex items-center justify-between border-t border-black/10 dark:border-white/5 pt-2">
            <span className="text-[11px] font-mono opacity-60">Audio Feedback:</span>
            <button
              onClick={() => {
                setSoundEnabled(!soundEnabled);
                playBeep(1000, 0.04);
              }}
              className="text-on-surface-variant hover:text-primary transition-colors cursor-pointer"
              title={soundEnabled ? 'Mute Shutter Sounds' : 'Unmute Shutter Sounds'}
              id="cam-sound-toggle"
            >
              {soundEnabled ? <Volume2 size={15} className="text-primary" /> : <VolumeX size={15} className="text-error" />}
            </button>
          </div>
        </div>
      </aside>

      {/* 2. Interactive Viewfinder and Camera HUD */}
      <section className="flex-1 bg-surface-container-low/60 rounded-2xl border border-black/10 dark:border-white/5 p-4 flex flex-col justify-between relative overflow-hidden">
        
        {/* Hidden active camera snap canvas */}
        <canvas ref={canvasRef} width={640} height={480} className="hidden" />

        {/* Viewfinder Monitor with layout aspect ratio bounding */}
        <div className="flex-1 flex items-center justify-center min-h-[340px]">
          <div
            onClick={handleViewfinderClick}
            className={`relative rounded-xl overflow-hidden bg-black border border-black/15 shadow-2xl transition-all duration-300 cursor-crosshair flex items-center justify-center ${
              aspectRatio === '16:9' ? 'w-full aspect-[16/9]' : 'w-full max-w-[580px] aspect-[4/3]'
            }`}
          >
            {/* Countdown overlay indicator */}
            {countdown !== null && (
              <div className="absolute inset-0 bg-black/60 z-30 flex items-center justify-center animate-pulse">
                <span className="text-8xl font-sans font-black text-primary drop-shadow-[0_0_24px_rgba(96,205,255,0.6)] animate-ping">
                  {countdown}
                </span>
              </div>
            )}

            {/* Camera flash shutter flash overlay */}
            {flashActive && (
              <div className="absolute inset-0 bg-white z-40 animate-fade-out" />
            )}

            {/* Video recording blink banner overlay */}
            {isRecording && (
              <div className="absolute top-4 left-4 z-20 flex items-center gap-2 bg-black/60 px-3 py-1.5 rounded-full text-xs text-white font-mono border border-error/30 animate-pulse">
                <span className="w-2.5 h-2.5 rounded-full bg-error" />
                <span>REC {formatRecordTime(recordDuration)}</span>
              </div>
            )}

            {/* Rule of Thirds or Golden gridlines */}
            {gridLines === 'thirds' && (
              <div className="absolute inset-0 z-10 pointer-events-none flex">
                <div className="w-1/3 border-r border-white/25 h-full" />
                <div className="w-1/3 border-r border-white/25 h-full" />
                <div className="absolute top-1/3 h-[1px] w-full bg-white/25" />
                <div className="absolute top-2/3 h-[1px] w-full bg-white/25" />
              </div>
            )}

            {gridLines === 'golden' && (
              <div className="absolute inset-0 z-10 pointer-events-none">
                {/* Simulated concentric phi ratio rings */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[61.8%] h-[61.8%] border border-dashed border-white/20 rounded-xl" />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[38.2%] h-[38.2%] border border-dashed border-white/20 rounded-xl" />
                <div className="absolute top-1/3 left-1/3 h-[1px] w-[61.8%] bg-white/15" />
                <div className="absolute top-2/3 left-1/3 h-[1px] w-[61.8%] bg-white/15" />
              </div>
            )}

            {/* Interactive watermark brand */}
            <div className="absolute bottom-4 left-4 z-10 text-[10px] text-white/40 font-mono flex items-center gap-1.5 px-2.5 py-1 bg-black/40 rounded-full backdrop-blur-md">
              <Eye size={10} className="text-primary animate-pulse" />
              <span>Lumina Optical Engine</span>
            </div>

            {/* Active stream video versus simulated high-fidelity canvas stream */}
            {cameraState === 'active' ? (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className={`w-full h-full object-cover select-none pointer-events-none ${filterClasses[filter]}`}
              />
            ) : (
              <div className="w-full h-full relative">
                <canvas
                  ref={fallbackCanvasRef}
                  width={640}
                  height={480}
                  className={`w-full h-full object-cover pointer-events-none ${filterClasses[filter]}`}
                />
                {/* Virtual Camera Indicator Shield on bottom right */}
                <div className="absolute bottom-4 right-4 z-10 bg-black/70 px-3 py-1 rounded-full text-[10px] font-mono text-[#60cdff] border border-primary/20 flex items-center gap-1">
                  <ShieldCheck size={11} className="text-primary" />
                  <span>PREVIEW EMULATED</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Camera Control Panel footer */}
        <div className="mt-4 flex items-center justify-between bg-black/5 dark:bg-black/20 p-3 rounded-2xl border border-black/10 dark:border-white/5">
          
          {/* Snap mode select */}
          <div className="flex bg-black/10 dark:bg-black/30 p-1 rounded-xl border border-black/5 dark:border-white/5">
            <button
              onClick={() => {
                if (isRecording) return;
                setMode('photo');
                playBeep(800, 0.04);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 cursor-pointer transition-all ${
                mode === 'photo'
                  ? 'bg-primary text-on-primary font-bold shadow-md'
                  : 'text-on-surface-variant hover:text-on-surface opacity-70'
              }`}
              id="cam-mode-photo"
            >
              <Camera size={13} />
              <span>Photo</span>
            </button>
            <button
              onClick={() => {
                setMode('video');
                playBeep(800, 0.04);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 cursor-pointer transition-all ${
                mode === 'video'
                  ? 'bg-primary text-on-primary font-bold shadow-md'
                  : 'text-on-surface-variant hover:text-on-surface opacity-70'
              }`}
              id="cam-mode-video"
            >
              <Video size={13} />
              <span>Video</span>
            </button>
          </div>

          {/* Core circular Shutter execution trigger */}
          <div className="flex items-center justify-center">
            {mode === 'photo' ? (
              <button
                onClick={triggerShutter}
                disabled={countdown !== null}
                className="w-14 h-14 rounded-full bg-primary border-4 border-surface-bright hover:scale-105 active:scale-90 transition-all shadow-[0_0_20px_rgba(96,205,255,0.4)] cursor-pointer flex items-center justify-center text-on-primary"
                title="Capture Picture"
                id="shutter-trigger-photo"
              >
                <Camera size={22} className="animate-pulse" />
              </button>
            ) : (
              <button
                onClick={triggerRecording}
                className={`w-14 h-14 rounded-full border-4 border-surface-bright hover:scale-105 active:scale-90 transition-all cursor-pointer flex items-center justify-center ${
                  isRecording
                    ? 'bg-error shadow-[0_0_20px_rgba(239,68,68,0.5)] animate-pulse'
                    : 'bg-primary shadow-[0_0_20px_rgba(96,205,255,0.4)]'
                }`}
                title={isRecording ? 'Stop Recording' : 'Start Recording'}
                id="shutter-trigger-video"
              >
                {isRecording ? (
                  <span className="w-5 h-5 rounded bg-white" />
                ) : (
                  <Video size={22} className="text-on-primary" />
                )}
              </button>
            )}
          </div>

          {/* Quick Photo Roll Album preview */}
          <div className="flex items-center gap-2">
            {savedSnaps.length > 0 ? (
              <button
                onClick={() => setGalleryOpenIndex(savedSnaps.length - 1)}
                className="w-12 h-12 rounded-xl overflow-hidden border-2 border-primary/40 hover:border-primary cursor-pointer hover:scale-105 active:scale-95 transition-all shadow-md relative group"
                id="cam-gallery-preview"
              >
                <img
                  src={savedSnaps[savedSnaps.length - 1]}
                  alt="Snapshot"
                  className="w-full h-full object-cover group-hover:brightness-110"
                />
                <span className="absolute bottom-0 right-0 bg-primary text-on-primary text-[9px] font-bold px-1.5 rounded-tl-lg">
                  {savedSnaps.length}
                </span>
              </button>
            ) : (
              <div className="w-12 h-12 rounded-xl bg-black/10 dark:bg-white/5 border border-black/10 dark:border-white/10 flex flex-col items-center justify-center opacity-40">
                <CameraOff size={16} />
              </div>
            )}
          </div>
        </div>
      </section>

      {/* 3. High-fidelity Microsoft Photos App Simulation Gallery Modal */}
      {galleryOpenIndex !== null && (
        <div className="absolute inset-0 bg-black/90 backdrop-blur-md z-[500] flex flex-col justify-between p-4 rounded-2xl border border-white/10">
          
          {/* Header toolbar */}
          <header className="flex justify-between items-center bg-white/5 p-2 rounded-xl border border-white/5 px-4">
            <div className="flex items-center gap-2 text-white">
              <FileImage size={14} className="text-primary" />
              <span className="text-xs font-mono font-bold">
                Windows Photos Roll // Image_{galleryOpenIndex + 1}.png
              </span>
            </div>

            <div className="flex items-center gap-1.5">
              <button
                onClick={() => exportImageDownload(savedSnaps[galleryOpenIndex], galleryOpenIndex)}
                className="p-1.5 bg-white/5 hover:bg-white/10 text-white hover:text-primary rounded-lg transition-colors cursor-pointer"
                title="Download snapshot"
                id="photos-export"
              >
                <Download size={14} />
              </button>
              <button
                onClick={() => deleteSnapIndex(galleryOpenIndex)}
                className="p-1.5 bg-white/5 hover:bg-white/10 text-white hover:text-error rounded-lg transition-colors cursor-pointer"
                title="Delete photo"
                id="photos-delete"
              >
                <Trash2 size={14} />
              </button>
              <div className="w-[1px] h-3 bg-white/20 mx-1"></div>
              <button
                onClick={() => setGalleryOpenIndex(null)}
                className="p-1.5 bg-white/5 hover:bg-error-container/30 text-white hover:text-error rounded-lg transition-colors cursor-pointer"
                id="photos-close"
              >
                <X size={14} />
              </button>
            </div>
          </header>

          {/* Mid section view with carousels */}
          <div className="flex-1 flex items-center justify-between relative px-6">
            <button
              onClick={() => {
                setGalleryOpenIndex((prev) => (prev !== null && prev > 0 ? prev - 1 : savedSnaps.length - 1));
                playBeep(900, 0.03);
              }}
              className="p-3 bg-white/5 hover:bg-white/10 text-white rounded-full transition-all cursor-pointer hover:scale-105 active:scale-95"
              id="photos-prev"
            >
              <ChevronLeft size={20} />
            </button>

            <div className="max-w-xl max-h-[380px] rounded-lg overflow-hidden border border-white/10 bg-black shadow-2xl">
              <img
                src={savedSnaps[galleryOpenIndex]}
                alt="Active roll view"
                className="max-w-full max-h-[380px] object-contain"
              />
            </div>

            <button
              onClick={() => {
                setGalleryOpenIndex((prev) => (prev !== null && prev < savedSnaps.length - 1 ? prev + 1 : 0));
                playBeep(900, 0.03);
              }}
              className="p-3 bg-white/5 hover:bg-white/10 text-white rounded-full transition-all cursor-pointer hover:scale-105 active:scale-95"
              id="photos-next"
            >
              <ChevronRight size={20} />
            </button>
          </div>

          {/* Bottom quick thumbnail bar */}
          <footer className="bg-white/5 p-2 rounded-xl border border-white/5 flex gap-2 justify-center max-w-full overflow-x-auto py-3 custom-scrollbar">
            {savedSnaps.map((snap, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setGalleryOpenIndex(idx);
                  playBeep(800, 0.03);
                }}
                className={`w-11 h-11 rounded-lg overflow-hidden border-2 transition-all shrink-0 cursor-pointer ${
                  galleryOpenIndex === idx ? 'border-primary scale-110 shadow-lg' : 'border-transparent opacity-60 hover:opacity-100'
                }`}
              >
                <img src={snap} alt="roll thumbnail" className="w-full h-full object-cover" />
              </button>
            ))}
          </footer>
        </div>
      )}
    </div>
  );
}
