import React, { useState, useEffect } from 'react';
import { Target, PlayCircle, Shield, AlertTriangle, Loader2 } from 'lucide-react';
import { getSimulationScenarios, runSimulation } from '../services/api';

const ValidationLab = () => {
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(null);

  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        const res = await getSimulationScenarios();
        // The API returns an object with scenario keys mapped to details
        const scenarioList = Object.entries(res.data).map(([key, details]) => ({
          id: key,
          name: details.name,
          description: details.description,
          attack_type: details.attack_type,
          mitre_techniques: details.mitre_techniques,
          estimated_events: details.estimated_events
        }));
        setScenarios(scenarioList);
      } catch (err) {
        console.error("Failed to load scenarios", err);
      } finally {
        setLoading(false);
      }
    };
    fetchScenarios();
  }, []);

  const handleRun = async (scenarioId) => {
    setRunning(scenarioId);
    try {
      await runSimulation({ scenario_name: scenarioId, endpoint_id: "demo-1" });
      alert("Simulation started! Check the Alerts page for generated detections.");
    } catch (err) {
      alert("Failed to start simulation.");
      console.error(err);
    } finally {
      setRunning(null);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-textMain">Detection Validation Lab</h1>
          <p className="text-textMuted mt-1">Safely validate your detections against real-world techniques without affecting production endpoints.</p>
        </div>
      </div>

      <div className="bg-warning/10 border border-warning/20 p-4 rounded-xl flex items-start">
        <AlertTriangle className="w-5 h-5 text-warning mr-3 flex-shrink-0 mt-0.5" />
        <div>
          <h4 className="text-sm font-semibold text-warning">Validation Safety Mode Enabled</h4>
          <p className="text-xs text-textMuted mt-1">
            All validations are simulated on the backend. No actual malware is executed. Payloads inject mocked telemetry behaviors directly into the detection pipeline.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center p-12"><Loader2 className="w-8 h-8 text-primary animate-spin" /></div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {scenarios.map((scenario) => (
            <div key={scenario.id} className="glass-panel p-6 flex flex-col group hover:-translate-y-1 transition-all duration-300 border border-border hover:border-primary/30">
              <div className="w-12 h-12 rounded-xl bg-surfaceHighlight flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Target className="w-6 h-6 text-primary" />
              </div>
              
              <h3 className="text-lg font-semibold text-textMain">{scenario.name}</h3>
              <p className="text-sm text-textMuted mt-2 flex-1">{scenario.description}</p>
              
              <div className="mt-4 flex flex-wrap gap-1">
                 {scenario.mitre_techniques.map(t => (
                   <span key={t} className="px-2 py-0.5 bg-primary/10 text-primary text-[10px] rounded border border-primary/20">{t}</span>
                 ))}
              </div>

              <div className="mt-6 pt-4 border-t border-border flex items-center justify-between">
                <div className="flex space-x-2 text-xs">
                  <span className="px-2 py-1 bg-surfaceHighlight text-textMuted rounded border border-border">
                    {scenario.estimated_events} events
                  </span>
                  <span className="px-2 py-1 rounded border bg-warning/10 text-warning border-warning/20">
                    {scenario.attack_type}
                  </span>
                </div>
                <button 
                  onClick={() => handleRun(scenario.id)}
                  disabled={running === scenario.id}
                  className="text-primary hover:text-primaryHover transition-colors flex items-center text-sm font-medium disabled:opacity-50">
                  {running === scenario.id ? "Running..." : "Run"} <PlayCircle className="w-4 h-4 ml-1" />
                </button>
              </div>
            </div>
          ))}

          {/* Custom Scenario Builder Card */}
          <div className="glass-panel p-6 flex flex-col items-center justify-center border border-dashed border-border hover:border-primary/50 transition-colors cursor-pointer bg-surfaceHighlight/20">
            <div className="w-12 h-12 rounded-full bg-surfaceHighlight flex items-center justify-center mb-3">
              <Shield className="w-6 h-6 text-textMuted" />
            </div>
            <h3 className="text-base font-medium text-textMain">Custom Scenario</h3>
            <p className="text-xs text-textMuted mt-1 text-center max-w-[200px]">Combine techniques to build your own custom attack chain.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ValidationLab;
