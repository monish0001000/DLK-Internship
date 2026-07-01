import React, { useState, useEffect } from 'react';
import DataTable from '../components/common/DataTable';
import { ShieldCheck, FileCode, Play, Plus, Search } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { getDetectionRules } from '../services/api';
import HasPermission from '../components/common/HasPermission';
import { PERMISSIONS } from '../utils/permissions';

const cn = (...inputs) => twMerge(clsx(inputs));

const columns = [
  { key: 'name', header: 'Rule Name', render: (val) => <span className="font-medium text-textMain">{val}</span> },
  { 
    key: 'rule_type', 
    header: 'Type',
    render: (val) => (
      <span className="inline-flex items-center px-2 py-0.5 rounded bg-surfaceHighlight text-xs font-medium text-textMuted border border-border capitalize">
        {val}
      </span>
    )
  },
  { 
    key: 'severity', 
    header: 'Severity',
    render: (val) => {
      const severityStr = val || 'low';
      return (
      <span className={cn(
        "inline-flex items-center text-sm font-medium capitalize",
        severityStr === 'critical' ? "text-danger" : severityStr === 'high' ? "text-warning" : "text-primary"
      )}>
        {severityStr}
      </span>
    )}
  },
  { 
    key: 'is_enabled', 
    header: 'Status',
    render: (val) => (
      <div className="flex items-center">
        <div className={cn(
          "w-8 h-4 rounded-full relative transition-colors cursor-pointer",
          val ? "bg-primary" : "bg-surfaceHighlight border border-border"
        )}>
          <div className={cn(
            "absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform",
            val ? "translate-x-4" : "translate-x-0.5 bg-textMuted"
          )}></div>
        </div>
        <span className="ml-2 text-xs text-textMuted">{val ? 'Enabled' : 'Disabled'}</span>
      </div>
    )
  },
  { key: 'author', header: 'Author' },
  {
    key: 'actions',
    header: '',
    sortable: false,
    render: () => (
      <div className="flex space-x-2">
        <HasPermission requiredPermission={PERMISSIONS.EDIT_RULE}>
          <button className="p-1.5 hover:bg-surfaceHighlight rounded text-textMuted hover:text-primary transition-colors" title="Edit">
            <FileCode className="w-4 h-4" />
          </button>
        </HasPermission>
        <HasPermission requiredPermission={PERMISSIONS.CREATE_RULE}>
          <button className="p-1.5 hover:bg-surfaceHighlight rounded text-textMuted hover:text-accent transition-colors" title="Test Rule">
            <Play className="w-4 h-4" />
          </button>
        </HasPermission>
      </div>
    )
  }
];

const DetectionRules = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRules = async () => {
      try {
        const response = await getDetectionRules();
        setRules(response.data);
      } catch (error) {
        console.error('Error fetching rules:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchRules();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-textMain">Detection Rules</h1>
          <p className="text-textMuted mt-1">Manage Sigma, Behavioral, and IOC detection logic.</p>
        </div>
        <div className="flex space-x-3">
          <button className="btn-secondary flex items-center">
            <Search className="w-4 h-4 mr-2" />
            Rule Marketplace
          </button>
          <HasPermission requiredPermission={PERMISSIONS.CREATE_RULE}>
            <button className="btn-primary flex items-center">
              <Plus className="w-4 h-4 mr-2" />
              Create Rule
            </button>
          </HasPermission>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-pulse text-primary">Loading Rules...</div>
            </div>
          ) : (
            <DataTable 
              columns={columns} 
              data={rules} 
              searchPlaceholder="Search rules..."
            />
          )}
        </div>
        
        <div className="space-y-6">
          <div className="glass-panel p-6">
            <h3 className="text-sm font-semibold text-textMuted uppercase tracking-wider mb-4">Coverage</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-textMain">Execution</span>
                  <span className="text-accent">85%</span>
                </div>
                <div className="w-full bg-surfaceHighlight rounded-full h-1.5">
                  <div className="bg-accent h-1.5 rounded-full" style={{ width: '85%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-textMain">Persistence</span>
                  <span className="text-warning">62%</span>
                </div>
                <div className="w-full bg-surfaceHighlight rounded-full h-1.5">
                  <div className="bg-warning h-1.5 rounded-full" style={{ width: '62%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-textMain">Defense Evasion</span>
                  <span className="text-accent">92%</span>
                </div>
                <div className="w-full bg-surfaceHighlight rounded-full h-1.5">
                  <div className="bg-accent h-1.5 rounded-full" style={{ width: '92%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-textMain">Lateral Movement</span>
                  <span className="text-danger">38%</span>
                </div>
                <div className="w-full bg-surfaceHighlight rounded-full h-1.5">
                  <div className="bg-danger h-1.5 rounded-full" style={{ width: '38%' }}></div>
                </div>
              </div>
            </div>
            <button className="w-full mt-6 text-sm text-primary hover:text-primaryHover font-medium">View Full Matrix</button>
          </div>

          <div className="glass-panel p-6 border-primary/20 bg-primary/5">
            <div className="flex items-center mb-2">
              <ShieldCheck className="w-5 h-5 text-primary mr-2" />
              <h3 className="text-sm font-semibold text-textMain">AI Rule Suggestion</h3>
            </div>
            <p className="text-xs text-textMuted mb-4">
              Based on recent alerts, we recommend enabling the "Suspicious Parent-Child Process" rule to improve coverage against Living-off-the-Land (LotL) techniques.
            </p>
            <HasPermission requiredPermission={PERMISSIONS.EDIT_RULE}>
              <button className="w-full btn-primary text-xs py-1.5">Enable Rule</button>
            </HasPermission>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DetectionRules;
