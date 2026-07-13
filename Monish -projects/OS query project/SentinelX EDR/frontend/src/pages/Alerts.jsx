import React, { useState, useEffect } from 'react';
import DataTable from '../components/common/DataTable';
import { ShieldAlert, AlertTriangle, Info, MoreVertical } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { getAlerts } from '../services/api';

const cn = (...inputs) => twMerge(clsx(inputs));

const columns = [
  { key: 'id', header: 'Alert ID' },
  {
    key: 'severity',
    header: 'Severity',
    render: (val) => {
      let icon = Info;
      let colorClass = "text-blue-400 bg-blue-400/10 border-blue-400/20";
      
      if (val === 'critical') {
        icon = ShieldAlert;
        colorClass = "text-danger bg-danger/10 border-danger/20";
      } else if (val === 'high') {
        icon = AlertTriangle;
        colorClass = "text-warning bg-warning/10 border-warning/20";
      } else if (val === 'medium') {
        icon = AlertTriangle;
        colorClass = "text-yellow-400 bg-yellow-400/10 border-yellow-400/20";
      }

      const Icon = icon;

      return (
        <span className={cn("inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border capitalize", colorClass)}>
          <Icon className="w-3 h-3 mr-1" />
          {val}
        </span>
      );
    }
  },
  { 
    key: 'title', 
    header: 'Detection Title',
    render: (val) => <span className="font-medium text-textMain">{val}</span>
  },
  { key: 'endpoint_id', header: 'Endpoint' },
  { 
    key: 'mitre', 
    header: 'MITRE ATT&CK',
    render: (val, row) => (
      <span className="inline-flex items-center px-2 py-0.5 rounded bg-surfaceHighlight text-xs font-mono text-textMuted border border-border">
        {row.mitre_technique || val || row.rule_type}
      </span>
    )
  },
  { 
    key: 'status', 
    header: 'Status',
    render: (val) => (
      <span className={cn(
        "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize",
        val === 'open' || val === 'new' ? "text-primary bg-primary/10" :
        val === 'investigating' ? "text-warning bg-warning/10" :
        "text-accent bg-accent/10"
      )}>
        {val}
      </span>
    )
  },
  { 
    key: 'detected_at', 
    header: 'Time',
    render: (val) => <span className="text-sm">{new Date(val).toLocaleString()}</span>
  },
  {
    key: 'actions',
    header: '',
    sortable: false,
    render: () => (
      <button className="p-1 hover:bg-surfaceHighlight rounded text-textMuted hover:text-textMain transition-colors">
        <MoreVertical className="w-4 h-4" />
      </button>
    )
  }
];

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await getAlerts();
        setAlerts(response.data);
      } catch (error) {
        console.error('Error fetching alerts:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000); // 10s refresh
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-textMain">Alerts</h1>
          <p className="text-textMuted mt-1">Review and triage security detections.</p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-pulse text-primary">Loading Alerts...</div>
        </div>
      ) : (
        <DataTable 
          columns={columns} 
          data={alerts} 
          searchPlaceholder="Search alerts by title, endpoint, or MITRE ID..."
          onRowClick={(row) => console.log('Clicked', row)}
        />
      )}
    </div>
  );
};

export default Alerts;
