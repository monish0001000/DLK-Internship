import React, { useState, useEffect } from 'react';
import Timeline from '../components/common/Timeline';
import { Search, Bot, Download, FileText, AlertCircle, Loader2 } from 'lucide-react';
import { getInvestigations, simulateResponse } from '../services/api';

const Investigations = () => {
  const [investigations, setInvestigations] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const response = await getInvestigations();
        if (response.data) {
          setInvestigations(response.data);
          if (response.data.length > 0) {
            setSelectedId(response.data[0].id);
          }
        }
      } catch (error) {
        console.error('Error fetching investigations:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const handleResponseAction = async (actionType, target) => {
    const inv = investigations.find(i => i.id === selectedId);
    if (!inv) return;
    
    try {
      await simulateResponse({
        action_type: actionType,
        target: target,
        endpoint_id: "demo-1", // Should ideally be inv.alert.endpoint_id if included
        execution_mode: "simulation",
        reason: `Triggered from Investigation ${inv.id}`
      });
      alert(`Response action '${actionType}' simulated successfully. Check ResponseLog in backend.`);
    } catch (err) {
      alert("Failed to execute response action.");
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full py-20">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  if (investigations.length === 0) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-textMain">Investigations</h1>
            <p className="text-textMuted mt-1">AI-driven analysis of security alerts.</p>
          </div>
        </div>
        <div className="glass-panel p-10 flex flex-col items-center justify-center text-center">
          <AlertCircle className="w-12 h-12 text-textMuted mb-4" />
          <h2 className="text-xl font-semibold text-textMain">No Investigations Found</h2>
          <p className="text-textMuted mt-2 max-w-md">There are currently no active AI investigations. Investigations are triggered automatically for high-severity alerts or manually from the alerts page.</p>
        </div>
      </div>
    );
  }

  const investigation = investigations.find(i => i.id === selectedId);
  const events = investigation.timeline ? (typeof investigation.timeline === 'string' ? JSON.parse(investigation.timeline) : investigation.timeline) : [];
  const mitreMapping = investigation.mitre_mapping ? (typeof investigation.mitre_mapping === 'string' ? JSON.parse(investigation.mitre_mapping) : investigation.mitre_mapping) : {};

  return (
    <div className="h-[calc(100vh-2rem)] flex flex-col space-y-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 flex-shrink-0">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-textMain">Investigations</h1>
          <p className="text-textMuted mt-1">AI-driven analysis of security alerts.</p>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6 min-h-0">
        {/* Left pane: List */}
        <div className="glass-panel flex flex-col min-h-0 overflow-y-auto">
          <div className="p-4 border-b border-border bg-surface/50">
            <h3 className="font-semibold text-textMain">All Investigations</h3>
          </div>
          <div className="flex-1 p-2 space-y-2">
            {investigations.map(inv => (
              <div 
                key={inv.id} 
                onClick={() => setSelectedId(inv.id)}
                className={`p-3 rounded-lg cursor-pointer transition-colors border ${selectedId === inv.id ? 'bg-primary/10 border-primary text-textMain' : 'bg-surface border-border hover:border-primary/50 text-textMuted'}`}
              >
                <div className="text-xs font-mono mb-1">#{String(inv.id).substring(0,8).toUpperCase()}</div>
                <div className="text-sm font-medium truncate">Alert {inv.alert_id}</div>
                <div className="text-xs mt-2 flex justify-between">
                  <span className={inv.risk_score > 70 ? 'text-danger' : inv.risk_score > 40 ? 'text-warning' : 'text-primary'}>Score: {inv.risk_score}</span>
                  <span>{new Date(inv.started_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content Area */}
        <div className="lg:col-span-2 space-y-6 overflow-y-auto pr-2">
          {/* AI Analysis Summary */}
          <div className="glass-panel p-6 border-primary/20 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
              <Bot className="w-32 h-32 text-primary" />
            </div>
            
            <div className="flex items-center mb-4">
              <Bot className="w-6 h-6 text-primary mr-2" />
              <h3 className="text-lg font-semibold text-textMain">AI Analysis Summary</h3>
            </div>
            
            <div className="prose prose-invert max-w-none text-sm text-textMuted">
              <p className="whitespace-pre-wrap">{investigation.summary || 'Summary is being generated...'}</p>
              
              {Object.keys(mitreMapping).length > 0 && (
                <div className="mt-4">
                  <h4 className="text-textMain font-medium mb-2">Mapped Techniques:</h4>
                  <div className="flex flex-wrap gap-2">
                    {Object.keys(mitreMapping).map(t => (
                      <span key={t} className="bg-surfaceHighlight px-2 py-1 rounded text-xs border border-border">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Timeline */}
          <div className="glass-panel p-6">
            <h3 className="text-lg font-semibold text-textMain mb-6">Attack Timeline</h3>
            {events.length > 0 ? (
              <Timeline events={events} />
            ) : (
              <div className="text-sm text-textMuted text-center py-4 border border-dashed border-border rounded-lg">
                No timeline events extracted.
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Context */}
        <div className="space-y-6 overflow-y-auto">
          <div className="glass-panel p-6">
            <h3 className="text-sm font-semibold text-textMuted uppercase tracking-wider mb-4">Investigation Details</h3>
            <div className="space-y-3">
              <div className="p-3 bg-surfaceHighlight/50 rounded-lg border border-border">
                <p className="text-xs text-textMuted mb-1">Status</p>
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-textMain capitalize">{investigation.status}</p>
                </div>
              </div>
              <div className="p-3 bg-surfaceHighlight/50 rounded-lg border border-border">
                <p className="text-xs text-textMuted mb-1">Risk Score</p>
                <div className="flex items-center justify-between">
                  <p className={`text-sm font-medium ${investigation.risk_score > 70 ? 'text-danger' : investigation.risk_score > 40 ? 'text-warning' : 'text-primary'}`}>
                    {investigation.risk_score}/100
                  </p>
                </div>
              </div>
              <div className="p-3 bg-surfaceHighlight/50 rounded-lg border border-border">
                <p className="text-xs text-textMuted mb-1">Started At</p>
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-textMain">{new Date(investigation.started_at).toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="glass-panel p-6">
            <h3 className="text-sm font-semibold text-textMuted uppercase tracking-wider mb-4">Response Actions</h3>
            <div className="space-y-2">
              <button onClick={() => handleResponseAction('isolate_endpoint', 'all')} className="w-full text-left p-3 rounded-lg border border-danger/20 bg-danger/10 text-danger hover:bg-danger/20 transition-colors">
                <span className="font-semibold block text-sm">Isolate Endpoint</span>
                <span className="text-xs opacity-80">Disconnect from network except for EDR.</span>
              </button>
              <button onClick={() => handleResponseAction('kill_process', 'malicious_pid')} className="w-full text-left p-3 rounded-lg border border-warning/20 bg-warning/10 text-warning hover:bg-warning/20 transition-colors">
                <span className="font-semibold block text-sm">Kill Process Tree</span>
                <span className="text-xs opacity-80">Terminate malicious processes.</span>
              </button>
              <button className="w-full text-left p-3 rounded-lg border border-primary/20 bg-primary/10 text-primary hover:bg-primary/20 transition-colors cursor-not-allowed opacity-50">
                <span className="font-semibold block text-sm">Create Case</span>
                <span className="text-xs opacity-80">Phase 13 Feature.</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Investigations;
