import React from 'react';

const Settings = () => {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-textMain">Settings</h1>
        <p className="text-textMuted mt-1">Configure SentinelX EDR preferences and integrations.</p>
      </div>

      <div className="glass-panel p-6">
        <h3 className="text-lg font-semibold text-textMain mb-4">API Integrations</h3>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-textMuted block mb-1">Gemini API Key</label>
            <input 
              type="password" 
              defaultValue="************************"
              className="w-full bg-background border border-border rounded-lg px-4 py-2 text-textMain focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-textMuted block mb-1">AbuseIPDB API Key</label>
            <input 
              type="password" 
              placeholder="Enter key..."
              className="w-full bg-background border border-border rounded-lg px-4 py-2 text-textMain focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <button className="btn-primary mt-4">Save Configuration</button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
