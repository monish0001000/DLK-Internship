import React, { useState, useEffect } from 'react';
import DataTable from '../components/common/DataTable';
import { Monitor, Wifi, WifiOff, ShieldAlert, MoreVertical } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { getEndpoints } from '../services/api';
import HasPermission from '../components/common/HasPermission';
import { PERMISSIONS } from '../utils/permissions';

const cn = (...inputs) => twMerge(clsx(inputs));

const columns = [
  {
    key: 'hostname',
    header: 'Hostname',
    render: (val, row) => (
      <div className="flex items-center font-medium">
        <Monitor className={cn("w-4 h-4 mr-3", row.os_type?.toLowerCase().includes('windows') ? "text-blue-400" : row.os_type?.toLowerCase().includes('ubuntu') || row.os_type?.toLowerCase().includes('linux') ? "text-orange-400" : "text-gray-300")} />
        {val}
      </div>
    )
  },
  { key: 'ip_address', header: 'IP Address' },
  { key: 'os_type', header: 'OS', render: (val, row) => `${val} ${row.os_version || ''}` },
  {
    key: 'status',
    header: 'Status',
    render: (val, row) => {
      let status = val;
      if (row.is_isolated) status = 'isolated';

      let icon = Wifi;
      let colorClass = "text-accent bg-accent/10 border-accent/20";
      
      if (status === 'offline') {
        icon = WifiOff;
        colorClass = "text-textMuted bg-surfaceHighlight border-border";
      } else if (status === 'isolated') {
        icon = ShieldAlert;
        colorClass = "text-danger bg-danger/10 border-danger/20";
      }

      const Icon = icon;

      return (
        <span className={cn("inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border capitalize", colorClass)}>
          <Icon className="w-3 h-3 mr-1.5" />
          {status}
        </span>
      );
    }
  },
  {
    key: 'alerts',
    header: 'Active Alerts',
    render: (val) => (
      val > 0 ? (
        <span className="inline-flex items-center text-danger font-semibold bg-danger/10 px-2 py-0.5 rounded-full text-xs">
          <ShieldAlert className="w-3 h-3 mr-1" />
          {val}
        </span>
      ) : (
        <span className="text-textMuted text-xs font-medium">0</span>
      )
    )
  },
  { 
    key: 'last_seen', 
    header: 'Last Seen',
    render: (val) => <span className="text-sm">{val ? new Date(val).toLocaleString() : 'Never'}</span>
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

const Endpoints = () => {
  const [endpoints, setEndpoints] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEndpoints = async () => {
      try {
        const response = await getEndpoints();
        // The API might not return alerts count directly in endpoint object depending on schema
        // For now, assume it returns what we need or map it
        setEndpoints(response.data);
      } catch (error) {
        console.error('Error fetching endpoints:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchEndpoints();
    const interval = setInterval(fetchEndpoints, 30000); // 30s refresh
    return () => clearInterval(interval);
  }, []);

  const total = endpoints.length;
  const online = endpoints.filter(e => e.status === 'online' && !e.is_isolated).length;
  const offline = endpoints.filter(e => e.status === 'offline').length;
  const isolated = endpoints.filter(e => e.is_isolated).length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-textMain">Endpoints</h1>
          <p className="text-textMuted mt-1">Manage and monitor agents across your fleet.</p>
        </div>
        <div className="flex space-x-3">
          <button className="btn-secondary">Export CSV</button>
          <HasPermission requiredPermission={PERMISSIONS.ISOLATE_ENDPOINT}>
            <button className="btn-primary">Deploy Agent</button>
          </HasPermission>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="glass-panel p-4 flex items-center justify-between">
          <div>
            <p className="text-textMuted text-sm">Total Endpoints</p>
            <p className="text-2xl font-bold text-textMain mt-1">{loading ? '...' : total}</p>
          </div>
          <Monitor className="w-8 h-8 text-primary/50" />
        </div>
        <div className="glass-panel p-4 flex items-center justify-between border-accent/30">
          <div>
            <p className="text-textMuted text-sm">Online</p>
            <p className="text-2xl font-bold text-accent mt-1">{loading ? '...' : online}</p>
          </div>
          <Wifi className="w-8 h-8 text-accent/50" />
        </div>
        <div className="glass-panel p-4 flex items-center justify-between">
          <div>
            <p className="text-textMuted text-sm">Offline</p>
            <p className="text-2xl font-bold text-textMuted mt-1">{loading ? '...' : offline}</p>
          </div>
          <WifiOff className="w-8 h-8 text-textMuted/50" />
        </div>
        <div className="glass-panel p-4 flex items-center justify-between border-danger/30">
          <div>
            <p className="text-textMuted text-sm">Isolated</p>
            <p className="text-2xl font-bold text-danger mt-1">{loading ? '...' : isolated}</p>
          </div>
          <ShieldAlert className="w-8 h-8 text-danger/50" />
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-pulse text-primary">Loading Endpoints...</div>
        </div>
      ) : (
        <DataTable 
          columns={columns} 
          data={endpoints} 
          searchPlaceholder="Search hostnames, IPs, or OS..."
          onRowClick={(row) => console.log('Clicked', row)}
        />
      )}
    </div>
  );
};

export default Endpoints;
