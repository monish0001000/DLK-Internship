import React, { useState, useEffect } from 'react';
import DataTable from '../components/common/DataTable';
import { Briefcase, User, MessageSquare, Paperclip, CheckCircle } from 'lucide-react';
import { getCases } from '../services/api';

const columns = [
  { key: 'id', header: 'Case ID' },
  { 
    key: 'title', 
    header: 'Title',
    render: (val) => <span className="font-medium text-textMain">{val}</span>
  },
  { 
    key: 'priority', 
    header: 'Priority',
    render: (val) => {
      const priorityStr = val || 'low';
      return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize ${
        priorityStr === 'critical' ? 'bg-danger/10 text-danger border-danger/20' :
        priorityStr === 'high' ? 'bg-warning/10 text-warning border-warning/20' :
        'bg-surfaceHighlight text-textMuted border-border'
      }`}>
        {priorityStr}
      </span>
    )}
  },
  { 
    key: 'status', 
    header: 'Status',
    render: (val) => {
      const statusStr = val || 'open';
      return (
      <span className={`inline-flex items-center text-sm font-medium capitalize ${
        statusStr === 'open' ? 'text-primary' :
        statusStr === 'in_progress' ? 'text-warning' :
        'text-accent'
      }`}>
        {statusStr === 'resolved' && <CheckCircle className="w-4 h-4 mr-1.5" />}
        {statusStr.replace('_', ' ')}
      </span>
    )}
  },
  { 
    key: 'assignee', 
    header: 'Assignee',
    render: (val) => {
      const assigneeStr = val || 'Unassigned';
      return (
      <div className="flex items-center text-sm text-textMuted">
        <div className="w-5 h-5 rounded-full bg-surfaceHighlight flex items-center justify-center mr-2">
          {assigneeStr === 'Unassigned' ? <User className="w-3 h-3" /> : <span className="text-[10px] text-textMain capitalize">{assigneeStr.charAt(0)}</span>}
        </div>
        <span className="capitalize">{assigneeStr}</span>
      </div>
    )}
  },
  { 
    key: 'updated_at', 
    header: 'Last Updated',
    render: (val) => <span className="text-sm">{val ? new Date(val).toLocaleString() : 'Never'}</span>
  }
];

const Cases = () => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const response = await getCases();
        setCases(response.data || []);
      } catch (error) {
        console.error('Error fetching cases:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchCases();
    const interval = setInterval(fetchCases, 30000);
    return () => clearInterval(interval);
  }, []);

  const openCases = cases.filter(c => c.status === 'open' || c.status === 'in_progress').length;
  const criticalHighCases = cases.filter(c => c.priority === 'critical' || c.priority === 'high').length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-textMain">Case Management</h1>
          <p className="text-textMuted mt-1">Track and collaborate on security incidents.</p>
        </div>
        <button className="btn-primary">
          <Briefcase className="w-4 h-4 mr-2 inline" />
          New Case
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="glass-panel p-5">
          <h3 className="text-sm font-medium text-textMuted uppercase tracking-wider mb-2">Open Cases</h3>
          <p className="text-4xl font-bold text-textMain">{loading ? '...' : openCases}</p>
        </div>
        <div className="glass-panel p-5">
          <h3 className="text-sm font-medium text-textMuted uppercase tracking-wider mb-2">Critical / High</h3>
          <p className="text-4xl font-bold text-danger">{loading ? '...' : criticalHighCases}</p>
        </div>
        <div className="glass-panel p-5">
          <h3 className="text-sm font-medium text-textMuted uppercase tracking-wider mb-2">Avg Resolution</h3>
          {cases.length > 0 ? (
            <p className="text-4xl font-bold text-textMain">1.4 <span className="text-xl text-textMuted font-normal">days</span></p>
          ) : (
            <p className="text-xl font-bold text-textMuted mt-2">No historical data available</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-pulse text-primary">Loading Cases...</div>
            </div>
          ) : cases.length === 0 ? (
            <div className="glass-panel p-10 flex flex-col items-center justify-center text-center">
              <Briefcase className="w-12 h-12 text-textMuted mb-4" />
              <h2 className="text-xl font-semibold text-textMain">No Cases Available</h2>
              <p className="text-textMuted mt-2 max-w-md">There are no cases in the system yet. Cases are created from alerts or investigations.</p>
            </div>
          ) : (
            <DataTable 
              columns={columns} 
              data={cases} 
              searchPlaceholder="Search cases..."
            />
          )}
        </div>
        
        {/* Quick Details Pane for selected case (Mock) */}
        <div className="glass-panel p-6 flex flex-col h-[500px]">
          <h3 className="text-lg font-semibold text-textMain mb-4">Case Details</h3>
          <div className="flex-1 overflow-y-auto pr-2 space-y-6">
            <p className="text-textMuted text-sm italic">Select a case to view details.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cases;
