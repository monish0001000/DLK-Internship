import React, { useState } from 'react';
import { ArrowLeft, ArrowRight, RotateCw, Shield, Search, Globe, Bookmark, Star, ExternalLink, HelpCircle } from 'lucide-react';

interface EdgeBrowserProps {
  addLog?: (msg: string) => void;
}

export default function EdgeBrowser({ addLog }: EdgeBrowserProps) {
  const [url, setUrl] = useState('lumina.internal/security-dashboard');
  const [currentTab, setCurrentTab] = useState('lumina.internal/security-dashboard');
  const [history, setHistory] = useState<string[]>(['lumina.internal/security-dashboard']);
  const [historyIndex, setHistoryIndex] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchSubmitted, setSearchSubmitted] = useState(false);

  // Nav actions
  const navigateTo = (newUrl: string) => {
    const formattedUrl = newUrl.trim().toLowerCase();
    const cleanUrl = formattedUrl.startsWith('http://') || formattedUrl.startsWith('https://')
      ? formattedUrl.replace(/^(https?:\/\/)?(www\.)?/, '')
      : formattedUrl;

    const updatedHistory = history.slice(0, historyIndex + 1);
    updatedHistory.push(cleanUrl);
    setHistory(updatedHistory);
    setHistoryIndex(updatedHistory.length - 1);
    setCurrentTab(cleanUrl);
    setUrl(cleanUrl);
    setSearchSubmitted(false);
    if (addLog) addLog(`Browser navigated to: ${cleanUrl}`);
  };

  const handleBack = () => {
    if (historyIndex > 0) {
      const prevIdx = historyIndex - 1;
      setHistoryIndex(prevIdx);
      setCurrentTab(history[prevIdx]);
      setUrl(history[prevIdx]);
      setSearchSubmitted(false);
    }
  };

  const handleForward = () => {
    if (historyIndex < history.length - 1) {
      const nextIdx = historyIndex + 1;
      setHistoryIndex(nextIdx);
      setCurrentTab(history[nextIdx]);
      setUrl(history[nextIdx]);
      setSearchSubmitted(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setSearchSubmitted(true);
      if (addLog) addLog(`Browser search query submitted: "${searchQuery}"`);
    }
  };

  const renderMockPage = () => {
    const tabLower = currentTab.toLowerCase();

    // 1. Google Search engine Mock
    if (tabLower.includes('google.com')) {
      return (
        <div className="bg-surface-dim min-h-full p-6 text-on-surface flex flex-col items-center">
          <div className="my-10 flex flex-col items-center">
            <h1 className="text-4xl font-bold font-sans tracking-tight select-none">
              <span className="text-[#4285F4]">G</span>
              <span className="text-[#EA4335]">o</span>
              <span className="text-[#FBBC05]">o</span>
              <span className="text-[#4285F4]">g</span>
              <span className="text-[#34A853]">l</span>
              <span className="text-[#EA4335]">e</span>
            </h1>
            <span className="text-[10px] text-primary font-mono tracking-wider mt-1 uppercase">Kiosk Safe Search</span>
          </div>

          {!searchSubmitted ? (
            <form onSubmit={handleSearchSubmit} className="w-full max-w-lg flex flex-col items-center gap-4">
              <div className="w-full relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search the secure web or type a URL..."
                  className="w-full py-3 pl-12 pr-4 bg-surface-container-high/60 border border-black/10 dark:border-white/10 rounded-full text-sm text-on-surface focus:outline-none focus:border-primary/50"
                  id="edge-search-input"
                />
                <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant opacity-60" />
              </div>
              <div className="flex gap-2">
                <button type="submit" className="px-4 py-2 bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 rounded text-xs text-on-surface border border-black/10 dark:border-white/5 transition-colors cursor-pointer">
                  Google Search
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setSearchQuery('Lumina Terminal Architecture');
                    setSearchSubmitted(true);
                  }}
                  className="px-4 py-2 bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 rounded text-xs text-on-surface border border-black/10 dark:border-white/5 transition-colors cursor-pointer"
                >
                  I'm Feeling Lucky
                </button>
              </div>
            </form>
          ) : (
            <div className="w-full max-w-xl text-left space-y-6">
              <div className="flex items-center gap-3 border-b border-black/10 dark:border-white/10 pb-4">
                <form onSubmit={handleSearchSubmit} className="flex-1 relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full py-2 pl-10 pr-4 bg-surface-container-high/60 border border-black/10 dark:border-white/10 rounded-full text-xs text-on-surface outline-none"
                  />
                  <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant opacity-60" />
                </form>
                <button onClick={() => setSearchSubmitted(false)} className="text-xs text-primary hover:underline cursor-pointer">
                  Clear
                </button>
              </div>

              {/* Mock Results */}
              <p className="text-xs text-on-surface-variant opacity-60">About 4,200 results (0.24 seconds)</p>

              <div className="space-y-4">
                <div className="p-4 bg-black/5 dark:bg-white/5 rounded-lg border border-black/5 dark:border-white/5 hover:bg-black/10 dark:hover:bg-white/10 transition-colors">
                  <a href="#link" onClick={() => navigateTo('lumina.internal/security-dashboard')} className="text-xs font-mono text-primary hover:underline block mb-1">
                    lumina.internal &gt; security-dashboard
                  </a>
                  <h3 className="text-sm font-semibold text-primary hover:underline cursor-pointer" onClick={() => navigateTo('lumina.internal/security-dashboard')}>
                    Lumina Secure System Kiosk Terminal v4.2 - Home
                  </h3>
                  <p className="text-xs text-on-surface-variant opacity-80 mt-1">
                    Official intranet panel for the Lumina Kiosk terminal. View device logs, network statistics, and manage authorized system mode parameters.
                  </p>
                </div>

                <div className="p-4 bg-black/5 dark:bg-white/5 rounded-lg border border-black/5 dark:border-white/5 hover:bg-black/10 dark:hover:bg-white/10 transition-colors">
                  <a href="#link" onClick={() => navigateTo('wikipedia.org/wiki/kiosk_software')} className="text-xs font-mono text-primary hover:underline block mb-1">
                    wikipedia.org &gt; wiki &gt; kiosk_software
                  </a>
                  <h3 className="text-sm font-semibold text-primary hover:underline cursor-pointer" onClick={() => navigateTo('wikipedia.org/wiki/kiosk_software')}>
                    Kiosk Software & Sandbox Architectures
                  </h3>
                  <p className="text-xs text-on-surface-variant opacity-80 mt-1">
                    Kiosk software is software that locks down an application or operating system, preventing users from accessing settings, programs or key directories.
                  </p>
                </div>

                <div className="p-4 bg-black/5 dark:bg-white/5 rounded-lg border border-black/5 dark:border-white/5 hover:bg-black/10 dark:hover:bg-white/10 transition-colors">
                  <span className="text-xs font-mono text-on-surface-variant opacity-60 block mb-1">
                    web.archive.org &gt; public_dns
                  </span>
                  <h3 className="text-sm font-semibold text-primary opacity-80">
                    Search result: "{searchQuery}"
                  </h3>
                  <p className="text-xs text-on-surface-variant opacity-80 mt-1">
                    No other live internet pages match your search. You are in restricted Kiosk Mode 1. Secure proxy has routed this query internally.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      );
    }

    // 2. Wikipedia Mock Page
    if (tabLower.includes('wikipedia.org')) {
      return (
        <div className="bg-surface-dim min-h-full p-6 text-on-surface font-sans text-left">
          <div className="flex items-baseline gap-2 border-b border-black/10 dark:border-white/10 pb-3 mb-4">
            <h1 className="text-2xl font-serif tracking-wide text-on-surface">WIKIPEDIA</h1>
            <span className="text-xs text-on-surface-variant opacity-70">The Free Encyclopedia</span>
          </div>

          <div className="max-w-2xl">
            <h2 className="text-xl font-serif border-b border-black/10 dark:border-white/10 pb-1 text-primary">Kiosk Mode & Security Sandbox</h2>
            <p className="text-xs text-on-surface-variant opacity-60 mt-1">From Wikipedia, the free encyclopedia</p>

            <p className="text-xs leading-relaxed text-on-surface-variant mt-4">
              A <b>kiosk</b> (from Persian: <i>kōšk</i>) is a small, stand-alone booth used in high-traffic areas. In computer science, 
              <b> kiosk mode</b> refers to a specialized user-interface setting designed to lock down a workstation. 
              Common systems include ticketing terminals, automated teller machines (ATMs), and medical device dashboards.
            </p>

            <h3 className="text-sm font-semibold text-on-surface mt-6 mb-2">Sandbox Implementation</h3>
            <p className="text-xs leading-relaxed text-on-surface-variant">
              Kiosk architectures operate by restricting standard desktop shell functions. Users are typically prevented from executing arbitrary keyboard shortcuts (such as <kbd className="px-1.5 py-0.5 bg-black/5 dark:bg-white/10 rounded font-mono text-[10px] text-on-surface">Ctrl+Alt+Del</kbd> or <kbd className="px-1.5 py-0.5 bg-black/5 dark:bg-white/10 rounded font-mono text-[10px] text-on-surface">Alt+Tab</kbd>), accessing developer options, or changing storage directories. 
              Modern kiosks like the <b>Lumina Kiosk</b> utilize deep glassmorphic layers to blend technical clarity with strict containerization.
            </p>

            <div className="mt-6 p-3 bg-black/5 dark:bg-white/5 rounded-lg border-l-4 border-primary">
              <p className="text-xs italic text-primary">
                "Modern kiosks enforce Mode 1 configurations, allowing only authenticated diagnostic utility execution to prevent tampering."
              </p>
            </div>
          </div>
        </div>
      );
    }

    // 3. Default Intranet security portal (Lumina portal)
    return (
      <div className="bg-surface-dim min-h-full p-6 text-left">
        <div className="flex items-center gap-3 border-b border-black/10 dark:border-white/10 pb-4 mb-6">
          <div className="p-2 bg-primary/10 text-primary rounded-lg border border-primary/20">
            <Shield size={24} />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-on-surface">Lumina Intranet Security Portal</h2>
            <p className="text-[10px] font-mono text-primary">GATEWAY: SECURE_PROXY_CHAMBER_109</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-black/5 dark:bg-white/5 rounded-xl border border-black/10 dark:border-white/5 space-y-3">
            <h3 className="text-xs font-semibold text-primary uppercase tracking-wider">Device Firewall & DNS Policy</h3>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              This terminal runs a customized enterprise DNS firewall. External connections are sandboxed to pre-vetted nodes. Any attempt to reach unapproved domains will trigger an automatic system integrity audit.
            </p>
            <div className="p-3 bg-black/10 dark:bg-black/20 rounded-lg border border-black/10 dark:border-white/5 font-mono text-[10px] text-on-surface-variant space-y-1">
              <p className="text-tertiary">✔ LOCAL DNS: ACTIVE (SECURE)</p>
              <p className="text-tertiary">✔ EXTERNAL PROXY: ENCRYPTED</p>
              <p className="text-error">✖ UNFILTERED OUTBOUND: BLOCKED</p>
            </div>
          </div>

          <div className="p-4 bg-black/5 dark:bg-white/5 rounded-xl border border-black/10 dark:border-white/5 space-y-3">
            <h3 className="text-xs font-semibold text-secondary uppercase tracking-wider">Authorized Domains</h3>
            <ul className="text-xs text-on-surface-variant space-y-2">
              <li className="flex items-center justify-between p-1.5 bg-black/10 dark:bg-black/15 rounded hover:bg-black/20 dark:hover:bg-black/30 cursor-pointer text-on-surface" onClick={() => navigateTo('google.com')}>
                <span className="flex items-center gap-1.5 font-mono text-on-surface">
                  <Star size={10} className="text-primary fill-primary" />
                  google.com
                </span>
                <span className="text-[10px] text-tertiary">Vetted Hub</span>
              </li>
              <li className="flex items-center justify-between p-1.5 bg-black/10 dark:bg-black/15 rounded hover:bg-black/20 dark:hover:bg-black/30 cursor-pointer text-on-surface" onClick={() => navigateTo('wikipedia.org')}>
                <span className="flex items-center gap-1.5 font-mono text-on-surface">
                  <Star size={10} className="text-primary fill-primary" />
                  wikipedia.org
                </span>
                <span className="text-[10px] text-tertiary">Wikipedia Archive</span>
              </li>
              <li className="flex items-center justify-between p-1.5 bg-black/10 dark:bg-black/15 rounded hover:bg-black/20 dark:hover:bg-black/30 opacity-70 text-on-surface">
                <span className="flex items-center gap-1.5 font-mono text-on-surface">
                  <Bookmark size={10} />
                  lumina.internal/security-dashboard
                </span>
                <span className="text-[10px] text-primary">This Page</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Warning notification */}
        <div className="mt-6 p-4 bg-error-container/10 border border-error/20 rounded-xl flex gap-3 items-center text-xs">
          <HelpCircle size={16} className="text-error" />
          <div className="text-on-surface-variant">
            <p className="font-semibold text-error">Security Warning</p>
            <p className="opacity-80">This browser simulator implements sandbox controls. External URLs are fully simulated within this sandbox.</p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full text-on-surface">
      {/* Browser Bar */}
      <div className="flex items-center justify-between gap-3 p-3 bg-surface-container-highest/60 border-b border-black/10 dark:border-white/10 rounded-t-xl">
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleBack}
            disabled={historyIndex <= 0}
            className="p-1.5 rounded-full hover:bg-black/5 dark:hover:bg-white/5 text-on-surface disabled:opacity-30 disabled:hover:bg-transparent cursor-pointer"
            id="edge-back"
          >
            <ArrowLeft size={14} />
          </button>
          <button
            onClick={handleForward}
            disabled={historyIndex >= history.length - 1}
            className="p-1.5 rounded-full hover:bg-black/5 dark:hover:bg-white/5 text-on-surface disabled:opacity-30 disabled:hover:bg-transparent cursor-pointer"
            id="edge-forward"
          >
            <ArrowRight size={14} />
          </button>
          <button
            onClick={() => {
              navigateTo(currentTab);
              if (addLog) addLog(`Browser tab reloaded.`);
            }}
            className="p-1.5 rounded-full hover:bg-black/5 dark:hover:bg-white/5 text-on-surface cursor-pointer"
            id="edge-refresh"
          >
            <RotateCw size={14} />
          </button>
        </div>

        {/* Address Bar */}
        <div className="flex-1 flex items-center bg-black/10 dark:bg-black/30 border border-black/10 dark:border-white/10 focus-within:border-primary/50 rounded-lg px-3 py-1.5 gap-2 transition-colors">
          <Shield size={14} className="text-tertiary" />
          <span className="text-[11px] font-mono text-tertiary uppercase select-none tracking-wider">Secure</span>
          <div className="w-[1px] h-3 bg-black/15 dark:bg-white/10"></div>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') navigateTo(url);
            }}
            className="flex-1 bg-transparent border-0 outline-none p-0 text-xs text-on-surface font-mono"
            id="edge-address-input"
          />
        </div>

        {/* Quick Hub Star */}
        <button className="p-1.5 hover:bg-black/5 dark:hover:bg-white/5 text-primary rounded-full cursor-pointer" title="Bookmarks list">
          <Star size={14} className="fill-primary" />
        </button>
      </div>

      {/* Bookmarks Bar */}
      <div className="flex items-center gap-3 px-4 py-1.5 bg-surface-container/30 border-b border-black/10 dark:border-white/5 text-[11px] font-semibold text-on-surface-variant">
        <span className="text-primary opacity-60">Bookmarks:</span>
        <button onClick={() => navigateTo('lumina.internal/security-dashboard')} className="flex items-center gap-1 hover:text-on-surface transition-colors cursor-pointer">
          <Globe size={11} className="text-primary" />
          Lumina Portal
        </button>
        <button onClick={() => navigateTo('google.com')} className="flex items-center gap-1 hover:text-on-surface transition-colors cursor-pointer">
          <Globe size={11} className="text-[#4285F4]" />
          Google Search
        </button>
        <button onClick={() => navigateTo('wikipedia.org')} className="flex items-center gap-1 hover:text-on-surface transition-colors cursor-pointer">
          <Globe size={11} className="text-secondary" />
          Wikipedia Archive
        </button>
      </div>

      {/* Web Rendering Window */}
      <div className="flex-1 min-h-[300px] overflow-y-auto custom-scrollbar bg-surface-dim rounded-b-xl relative">
        {renderMockPage()}
      </div>
    </div>
  );
}
