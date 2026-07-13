import React, { useState, useEffect } from 'react';
import { getAuditLogs } from '../../services/api';
import { Activity, ShieldAlert, Server, LogIn, Database } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const ActivityFeed = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  // Initial load from Audit Logs API
  useEffect(() => {
    const fetchRecentActivity = async () => {
      try {
        const response = await getAuditLogs({ limit: 20 });
        // Map audit logs to activity feed format
        const formattedLogs = (response.data || []).map(log => ({
          id: `audit-${log.id}`,
          type: log.action.includes('login') ? 'auth' : log.action.includes('endpoint') ? 'agent' : 'system',
          title: log.action,
          description: `User ${log.user} performed ${log.action} on ${log.target || 'system'}`,
          timestamp: new Date(log.timestamp),
          status: log.status
        }));
        setActivities(formattedLogs);
      } catch (err) {
        console.error('Failed to fetch initial activity', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecentActivity();
  }, []);

  // WebSocket for Real-Time merged feed
  useEffect(() => {
    const wsUrl = 'ws://localhost:8000/api/v1/ws/notifications';
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        let newActivity = null;

        if (data.type === 'new_alert') {
          newActivity = {
            id: `ws-${Date.now()}`,
            type: 'alert',
            title: 'Security Alert',
            description: data.alert?.title,
            timestamp: new Date(),
            status: 'warning'
          };
        } else if (data.type === 'agent_status') {
          newActivity = {
            id: `ws-${Date.now()}`,
            type: 'agent',
            title: 'Agent Status',
            description: `Endpoint ${data.endpoint_id} is ${data.status}`,
            timestamp: new Date(),
            status: data.status === 'offline' ? 'failed' : 'success'
          };
        } else if (data.type === 'system') {
          newActivity = {
            id: `ws-${Date.now()}`,
            type: 'system',
            title: 'System Event',
            description: data.message,
            timestamp: new Date(),
            status: 'success'
          };
        }

        if (newActivity) {
          setActivities(prev => [newActivity, ...prev].slice(0, 50));
        }
      } catch (e) {
        console.error(e);
      }
    };

    return () => ws.close();
  }, []);

  const getIcon = (type) => {
    switch(type) {
      case 'auth': return <LogIn className="w-4 h-4 text-blue-500" />;
      case 'alert': return <ShieldAlert className="w-4 h-4 text-red-500" />;
      case 'agent': return <Activity className="w-4 h-4 text-green-500" />;
      case 'system': return <Server className="w-4 h-4 text-purple-500" />;
      default: return <Database className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    if (status === 'failed' || status === 'denied' || status === 'warning') return 'border-red-500/50 bg-red-500/10';
    if (status === 'success') return 'border-green-500/50 bg-green-500/10';
    return 'border-gray-700 bg-surfaceHighlight';
  };

  if (loading) {
    return <div className="p-6 text-center text-textMuted animate-pulse">Loading activity feed...</div>;
  }

  return (
    <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
      {activities.length === 0 ? (
        <div className="text-center text-sm text-textMuted py-4">No recent activity.</div>
      ) : (
        activities.map((act) => (
          <div key={act.id} className={`flex items-start p-3 rounded-lg border ${getStatusColor(act.status)} transition-colors`}>
            <div className="mt-0.5 mr-3 flex-shrink-0 bg-surface p-1.5 rounded-md border border-border">
              {getIcon(act.type)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-textMain truncate">{act.title}</p>
              <p className="text-xs text-textMuted mt-0.5 line-clamp-2">{act.description}</p>
            </div>
            <div className="ml-3 flex-shrink-0 whitespace-nowrap">
              <span className="text-[10px] text-textMuted">{formatDistanceToNow(act.timestamp, { addSuffix: true })}</span>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default ActivityFeed;
