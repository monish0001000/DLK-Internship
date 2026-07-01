import React, { useState, useEffect } from 'react';
import {
  ShieldAlert, 
  Server, 
  Activity, 
  Crosshair,
  TrendingUp,
  Cpu,
  Globe,
  Database
} from 'lucide-react';
import StatCard from '../components/common/StatCard';
import ActivityFeed from '../components/dashboard/ActivityFeed';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import { getMetrics, getMttd, getAlerts } from '../services/api';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    total_alerts: 0,
    mttd_seconds: 0,
    mitre_coverage_pct: 0,
    alerts_trend: [],
    alerts_by_severity: {},
    endpoint_coverage: { total: 0, online: 0 }
  });
  const [mttd, setMttd] = useState({ mttd_formatted: '0m 0s' });
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [metricsRes, mttdRes, alertsRes] = await Promise.all([
          getMetrics(),
          getMttd(),
          getAlerts()
        ]);
        
        setMetrics(metricsRes.data);
        setMttd(mttdRes.data);
        
        // Sort alerts by created_at or id descending and take top 5
        const sortedAlerts = alertsRes.data.sort((a, b) => b.id - a.id).slice(0, 5);
        setRecentAlerts(sortedAlerts);
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    // In a real app, you might want to set up an interval to refresh data
    const interval = setInterval(fetchDashboardData, 30000); // 30s
    return () => clearInterval(interval);
  }, []);

  const mitreData = [
    { name: 'Execution', value: 85 },
    { name: 'Persistence', value: 62 },
    { name: 'Privilege Escalation', value: 45 },
    { name: 'Defense Evasion', value: 92 },
    { name: 'Credential Access', value: 54 },
    { name: 'Lateral Movement', value: 38 },
  ]; // This could be replaced with real data from endpoint coverage metrics if available

  if (loading) {
    return <div className="flex items-center justify-center h-full"><div className="animate-pulse text-primary">Loading Dashboard...</div></div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-textMain">SOC Dashboard</h1>
          <p className="text-textMuted mt-1">Real-time overview of your security posture.</p>
        </div>
        <div className="flex items-center space-x-3">
          <span className="flex items-center text-sm font-medium bg-accent/10 text-accent px-3 py-1.5 rounded-lg border border-accent/20">
            <span className="w-2 h-2 rounded-full bg-accent mr-2 animate-pulse"></span>
            System Healthy
          </span>
          <button className="btn-secondary flex items-center">
            <Database className="w-4 h-4 mr-2" />
            Generate Report
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Active Alerts" 
          value={metrics.total_alerts?.toString() || "0"} 
          icon={ShieldAlert} 
          trend="up" 
          trendValue="+12%"
          colorClass="bg-danger/10 text-danger"
        />
        <StatCard 
          title="Monitored Endpoints" 
          value={metrics.endpoint_coverage?.total?.toString() || "0"} 
          icon={Server} 
          trend="up" 
          trendValue="+24"
          colorClass="bg-primary/10 text-primary"
        />
        <StatCard 
          title="Events Analyzed" 
          value="1.2M" 
          icon={Activity} 
          trend="up" 
          trendValue="+150k"
          colorClass="bg-secondary/10 text-secondary"
        />
        <StatCard 
          title="Mean Time To Detect" 
          value={mttd.mttd_formatted} 
          icon={TrendingUp} 
          trend="down" 
          trendValue="-30s"
          colorClass="bg-accent/10 text-accent"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart */}
        <div className="glass-panel p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-textMain">Alert Trends (24h)</h3>
            <select className="bg-surface border border-border rounded-lg px-3 py-1 text-sm text-textMain focus:outline-none focus:ring-1 focus:ring-primary">
              <option>Last 24 Hours</option>
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
            </select>
          </div>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={metrics.alerts_trend.length > 0 ? metrics.alerts_trend : [{time: 'Now', critical:0, high:0, medium:0}]} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorCritical" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorHigh" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                <XAxis dataKey="date" stroke="#9CA3AF" tick={{fontSize: 12}} axisLine={false} tickLine={false} />
                <YAxis stroke="#9CA3AF" tick={{fontSize: 12}} axisLine={false} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '0.5rem' }}
                  itemStyle={{ color: '#F9FAFB' }}
                />
                <Area type="monotone" dataKey="critical" stroke="#EF4444" strokeWidth={2} fillOpacity={1} fill="url(#colorCritical)" />
                <Area type="monotone" dataKey="high" stroke="#F59E0B" strokeWidth={2} fillOpacity={1} fill="url(#colorHigh)" />
                <Area type="monotone" dataKey="medium" stroke="#3B82F6" strokeWidth={2} fillOpacity={0.1} fill="#3B82F6" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* MITRE ATT&CK Coverage */}
        <div className="glass-panel p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-textMain">MITRE ATT&CK</h3>
            <button className="text-primary hover:text-primaryHover text-sm font-medium">View Matrix</button>
          </div>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mitreData} layout="vertical" margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={true} vertical={false} />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" width={110} stroke="#9CA3AF" tick={{fontSize: 11}} axisLine={false} tickLine={false} />
                <Tooltip 
                  cursor={{fill: '#1F2937'}}
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '0.5rem' }}
                />
                <Bar dataKey="value" fill="#8B5CF6" radius={[0, 4, 4, 0]} barSize={16}>
                  {
                    mitreData.map((entry, index) => (
                      <cell key={`cell-${index}`} fill={entry.value > 80 ? '#EF4444' : entry.value > 60 ? '#F59E0B' : '#8B5CF6'} />
                    ))
                  }
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Alerts List */}
        <div className="glass-panel p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-textMain">Recent Alerts</h3>
            <button className="text-primary hover:text-primaryHover text-sm font-medium">View All</button>
          </div>
          <div className="space-y-4">
            {recentAlerts.length > 0 ? recentAlerts.map((alert) => (
              <div key={alert.id} className="flex items-start p-3 bg-surfaceHighlight/50 rounded-lg hover:bg-surfaceHighlight transition-colors border border-border/50">
                <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                  alert.severity === 'critical' ? 'bg-danger' : 
                  alert.severity === 'high' ? 'bg-warning' : 
                  alert.severity === 'medium' ? 'bg-primary' : 'bg-accent'
                }`}></div>
                <div className="ml-3 flex-1">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-textMain">{alert.title}</p>
                    <span className="text-xs text-textMuted">{new Date(alert.detected_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                  </div>
                  <p className="text-xs text-textMuted mt-1">{alert.endpoint_id} • {alert.mitre_tactic || alert.rule_type}</p>
                </div>
                <button className="ml-4 text-xs font-medium text-primary hover:text-primaryHover">Investigate</button>
              </div>
            )) : (
              <div className="text-center py-8 text-textMuted text-sm">No recent alerts found.</div>
            )}
          </div>
        </div>

        {/* Live Activity Feed */}
        <div className="glass-panel p-6 flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-textMain">Live Activity Feed</h3>
          </div>
          <div className="flex-1 overflow-hidden">
            <ActivityFeed />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
