import React, { useState, useEffect } from 'react';
import ThreatGraph from '../components/common/ThreatGraph';
import { Search, Database, Terminal, Filter, History, Bookmark, Save } from 'lucide-react';
import { runThreatHunt, getHuntHistory, getSavedHunts, saveHunt } from '../services/api';

const ThreatHunting = () => {
  const [activeTab, setActiveTab] = useState('table'); // 'table' or 'graph'
  const [rightPanel, setRightPanel] = useState('builder'); // 'builder', 'history', 'saved'
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [queryText, setQueryText] = useState("");
  
  // Structured query state
  const [queryTable, setQueryTable] = useState('processes');
  const [queryTime, setQueryTime] = useState('24h');
  const [filters, setFilters] = useState([]); // [{key: "", val: ""}]
  
  const [history, setHistory] = useState([]);
  const [savedHunts, setSavedHunts] = useState([]);
  const [saveName, setSaveName] = useState("");

  const fetchHistoryAndSaved = async () => {
    try {
      const [histRes, savedRes] = await Promise.all([getHuntHistory(), getSavedHunts()]);
      setHistory(histRes.data);
      setSavedHunts(savedRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchHistoryAndSaved();
  }, []);

  const handleRunQuery = async (overrideQuery = null) => {
    setLoading(true);
    try {
      let payload = overrideQuery;
      if (!payload) {
        const filtersObj = {};
        filters.forEach(f => {
          if (f.key && f.val) filtersObj[f.key] = f.val;
        });
        payload = {
          table: queryTable,
          time_range: queryTime,
          filters: filtersObj,
          limit: 100
        };
      }
      const res = await runThreatHunt(payload);
      setResults(res.data.results || []);
      setQueryText(res.data.query_text);
      fetchHistoryAndSaved(); // Refresh history
      setActiveTab('table');
    } catch (err) {
      console.error(err);
      alert("Query failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSaveHunt = async () => {
    if (!saveName) return alert("Please enter a name for the hunt.");
    try {
      const filtersObj = {};
      filters.forEach(f => {
        if (f.key && f.val) filtersObj[f.key] = f.val;
      });
      const payload = {
        name: saveName,
        query: {
          table: queryTable,
          time_range: queryTime,
          filters: filtersObj,
          limit: 100
        }
      };
      await saveHunt(payload);
      setSaveName("");
      alert("Hunt saved successfully!");
      fetchHistoryAndSaved();
      setRightPanel('saved');
    } catch (err) {
      console.error(err);
      alert("Failed to save hunt.");
    }
  };

  const loadQuery = (queryObj) => {
    setQueryTable(queryObj.table || 'processes');
    setQueryTime(queryObj.time_range || '24h');
    if (queryObj.filters) {
      setFilters(Object.entries(queryObj.filters).map(([k, v]) => ({ key: k, val: v })));
    } else {
      setFilters([]);
    }
    setRightPanel('builder');
  };

  // Convert results to simple graph nodes for visualization if graph tab is active
  const graphNodes = results.map(r => ({
    id: `node-${r.id || r.pid || Math.random()}`,
    label: r.name || r.remote_address || r.username || 'Item',
    type: queryTable
  }));

  return (
    <div className="space-y-6 h-[calc(100vh-2rem)] flex flex-col">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 flex-shrink-0">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-textMain">Threat Hunting</h1>
          <p className="text-textMuted mt-1">Structured query interface over real telemetry.</p>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6 min-h-0">
        {/* Left pane: Results / Graph */}
        <div className="lg:col-span-3 glass-panel flex flex-col min-h-0 relative">
          <div className="border-b border-border p-4 flex justify-between items-center bg-surface/50">
            <div className="flex gap-2">
              <button onClick={() => setActiveTab('table')} className={`text-sm px-4 py-2 rounded-lg transition-colors ${activeTab === 'table' ? 'bg-primary text-white' : 'text-textMuted hover:bg-surfaceHighlight'}`}>Table View</button>
              <button onClick={() => setActiveTab('graph')} className={`text-sm px-4 py-2 rounded-lg transition-colors ${activeTab === 'graph' ? 'bg-primary text-white' : 'text-textMuted hover:bg-surfaceHighlight'}`}>Graph View</button>
            </div>
            {queryText && <div className="text-xs font-mono text-primary truncate max-w-lg">{queryText}</div>}
          </div>
          
          <div className="flex-1 overflow-auto p-4">
            {loading ? (
              <div className="flex items-center justify-center h-full text-textMuted">Executing query...</div>
            ) : activeTab === 'table' ? (
              results.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="text-xs uppercase text-textMuted border-b border-border">
                      <tr>
                        {Object.keys(results[0]).map(key => (
                          <th key={key} className="px-4 py-3">{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {results.map((row, i) => (
                        <tr key={i} className="border-b border-border/50 hover:bg-surfaceHighlight/30">
                          {Object.values(row).map((val, j) => (
                            <td key={j} className="px-4 py-3 max-w-[200px] truncate">{String(val)}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-textMuted">No results found or run a query to start.</div>
              )
            ) : (
               <ThreatGraph nodes={graphNodes} links={[]} />
            )}
          </div>
        </div>

        {/* Right pane */}
        <div className="glass-panel flex flex-col min-h-0">
          <div className="flex border-b border-border">
            <button onClick={() => setRightPanel('builder')} className={`flex-1 py-3 text-sm font-medium ${rightPanel === 'builder' ? 'text-primary border-b-2 border-primary' : 'text-textMuted'}`}>Builder</button>
            <button onClick={() => setRightPanel('history')} className={`flex-1 py-3 text-sm font-medium ${rightPanel === 'history' ? 'text-primary border-b-2 border-primary' : 'text-textMuted'}`}>History</button>
            <button onClick={() => setRightPanel('saved')} className={`flex-1 py-3 text-sm font-medium ${rightPanel === 'saved' ? 'text-primary border-b-2 border-primary' : 'text-textMuted'}`}>Saved</button>
          </div>

          <div className="p-4 flex-1 overflow-y-auto">
            {rightPanel === 'builder' && (
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-medium text-textMuted uppercase">Table</label>
                  <select value={queryTable} onChange={(e) => setQueryTable(e.target.value)} className="mt-1 w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-textMain focus:outline-none focus:ring-1 focus:ring-primary">
                    <option value="processes">Processes</option>
                    <option value="network_connections">Network Connections</option>
                    <option value="startup_items">Startup Items</option>
                    <option value="services">Services</option>
                  </select>
                </div>
                
                <div>
                  <label className="text-xs font-medium text-textMuted uppercase">Time Range</label>
                  <select value={queryTime} onChange={(e) => setQueryTime(e.target.value)} className="mt-1 w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-textMain focus:outline-none focus:ring-1 focus:ring-primary">
                    <option value="1h">Last 1 Hour</option>
                    <option value="24h">Last 24 Hours</option>
                    <option value="7d">Last 7 Days</option>
                  </select>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="text-xs font-medium text-textMuted uppercase">Filters</label>
                    <button onClick={() => setFilters([...filters, {key: '', val: ''}])} className="text-xs text-primary hover:underline">+ Add</button>
                  </div>
                  {filters.map((f, i) => (
                    <div key={i} className="flex gap-2 mb-2">
                      <input type="text" placeholder="Field" value={f.key} onChange={(e) => { const nf = [...filters]; nf[i].key = e.target.value; setFilters(nf); }} className="w-1/2 bg-background border border-border rounded px-2 py-1 text-sm text-textMain" />
                      <input type="text" placeholder="Value" value={f.val} onChange={(e) => { const nf = [...filters]; nf[i].val = e.target.value; setFilters(nf); }} className="w-1/2 bg-background border border-border rounded px-2 py-1 text-sm text-textMain" />
                      <button onClick={() => setFilters(filters.filter((_, idx) => idx !== i))} className="text-error text-xs px-1">✕</button>
                    </div>
                  ))}
                </div>
                
                <button onClick={() => handleRunQuery()} className="w-full btn-primary py-2 flex items-center justify-center mt-4">
                  <Search className="w-4 h-4 mr-2" /> Run Query
                </button>

                <div className="pt-4 border-t border-border mt-4">
                  <input type="text" placeholder="Hunt Name" value={saveName} onChange={(e) => setSaveName(e.target.value)} className="w-full bg-background border border-border rounded px-3 py-2 text-sm text-textMain mb-2" />
                  <button onClick={handleSaveHunt} className="w-full btn-secondary py-2 flex items-center justify-center">
                    <Save className="w-4 h-4 mr-2" /> Save Hunt
                  </button>
                </div>
              </div>
            )}

            {rightPanel === 'history' && (
              <div className="space-y-3">
                {history.map((h, i) => (
                  <div key={i} className="p-3 bg-surface rounded-lg border border-border/50 hover:border-primary/50 cursor-pointer transition-colors" onClick={() => loadQuery(h.query_payload)}>
                    <div className="text-xs text-primary mb-1 font-mono">{h.query_text}</div>
                    <div className="text-[10px] text-textMuted">{new Date(h.timestamp).toLocaleString()} by {h.user}</div>
                  </div>
                ))}
                {history.length === 0 && <div className="text-sm text-textMuted text-center mt-4">No history yet.</div>}
              </div>
            )}

            {rightPanel === 'saved' && (
              <div className="space-y-3">
                {savedHunts.map((h, i) => (
                  <div key={i} className="p-3 bg-surface rounded-lg border border-border/50 hover:border-primary/50 cursor-pointer transition-colors" onClick={() => loadQuery(h.query)}>
                    <div className="text-sm font-medium text-textMain mb-1">{h.name}</div>
                    <div className="text-xs text-textMuted mb-2">{h.description || "Custom saved hunt"}</div>
                    <div className="flex gap-2">
                      <span className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded uppercase">{h.query.table}</span>
                      <span className="text-[10px] bg-surfaceHighlight text-textMain px-2 py-0.5 rounded">{h.query.time_range}</span>
                    </div>
                  </div>
                ))}
                {savedHunts.length === 0 && <div className="text-sm text-textMuted text-center mt-4">No saved hunts.</div>}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThreatHunting;
