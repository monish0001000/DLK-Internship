import React, { useState, useEffect, useRef } from 'react';
import { Bell, Search, User, X, ShieldAlert, Activity, Server, Info } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const TopBar = () => {
  const [notifications, setNotifications] = useState([]);
  const [hasUnread, setHasUnread] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);
  const { user } = useAuth();

  useEffect(() => {
    // Close dropdown on click outside
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    // Connect to WebSocket for real-time notifications
    const wsUrl = 'ws://localhost:8000/api/v1/ws/notifications'; // Using a generic notifications WS
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Connected to real-time notifications WebSocket');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        let newNotification = null;

        if (data.type === 'new_alert') {
          newNotification = {
            id: data.alert?.id || Date.now(),
            type: 'alert',
            title: data.alert?.title || 'New Security Alert',
            message: `Endpoint: ${data.alert?.endpoint_id || 'Unknown'}`,
            severity: data.alert?.severity || 'medium',
            time: new Date().toLocaleTimeString(),
            isRead: false
          };
        } else if (data.type === 'agent_status') {
          newNotification = {
            id: Date.now(),
            type: 'agent',
            title: 'Agent Status Change',
            message: `Endpoint ${data.endpoint_id} is now ${data.status}`,
            severity: data.status === 'offline' ? 'warning' : 'info',
            time: new Date().toLocaleTimeString(),
            isRead: false
          };
        } else if (data.type === 'system') {
          newNotification = {
            id: Date.now(),
            type: 'system',
            title: 'System Event',
            message: data.message || 'System update',
            severity: data.severity || 'info',
            time: new Date().toLocaleTimeString(),
            isRead: false
          };
        }

        if (newNotification) {
          setNotifications(prev => [newNotification, ...prev].slice(0, 20)); // Keep last 20 in dropdown
          setHasUnread(true);
        }
      } catch (err) {
        console.error('Error parsing websocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, []);

  const markAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
    setHasUnread(false);
  };

  const getIconForType = (type, severity) => {
    switch (type) {
      case 'alert':
        return <ShieldAlert className={`w-5 h-5 ${severity === 'critical' ? 'text-danger' : severity === 'high' ? 'text-warning' : 'text-primary'}`} />;
      case 'agent':
        return <Activity className={`w-5 h-5 ${severity === 'warning' ? 'text-warning' : 'text-green-500'}`} />;
      case 'system':
        return <Server className={`w-5 h-5 ${severity === 'warning' ? 'text-warning' : 'text-primary'}`} />;
      default:
        return <Info className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <header className="h-16 bg-surface/90 backdrop-blur-md border-b border-border flex items-center justify-between px-6 z-10 sticky top-0 shadow-sm">
      {/* Search */}
      <div className="flex-1 max-w-xl">
        <div className="relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-textMuted group-focus-within:text-primary transition-colors" />
          <input 
            type="text" 
            placeholder="Search endpoints, alerts, IPs, hashes (Ctrl+K)..." 
            className="w-full bg-background/50 border border-border rounded-xl pl-10 pr-4 py-2 text-sm text-textMain focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300 placeholder:text-textMuted/70 shadow-inner"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 hidden md:flex items-center space-x-1">
            <kbd className="px-2 py-0.5 text-xs font-mono bg-surface rounded border border-border text-textMuted">Ctrl</kbd>
            <kbd className="px-2 py-0.5 text-xs font-mono bg-surface rounded border border-border text-textMuted">K</kbd>
          </div>
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center space-x-4 ml-6 relative">
        <div className="relative" ref={dropdownRef}>
          <button 
            className="relative p-2 text-textMuted hover:text-textMain hover:bg-surfaceHighlight rounded-xl transition-all duration-200"
            onClick={() => {
              setShowDropdown(!showDropdown);
              if (!showDropdown) setHasUnread(false);
            }}
          >
            <Bell className="w-5 h-5" />
            {hasUnread && (
              <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-danger border-2 border-surface rounded-full animate-pulse"></span>
            )}
          </button>
          
          {/* Notifications Dropdown */}
          {showDropdown && (
            <div className="absolute right-0 mt-2 w-80 bg-surfaceHighlight border border-border rounded-xl shadow-2xl z-50 overflow-hidden flex flex-col max-h-[400px]">
              <div className="p-3 border-b border-border flex justify-between items-center bg-surface/50">
                <h3 className="text-sm font-semibold text-textMain">Notifications</h3>
                <button onClick={markAllRead} className="text-xs text-primary hover:text-primaryHover">Mark all as read</button>
              </div>
              <div className="overflow-y-auto flex-1">
                {notifications.length === 0 ? (
                  <div className="p-6 text-center text-sm text-textMuted">No notifications</div>
                ) : (
                  notifications.map(notif => (
                    <div key={notif.id} className={`p-3 border-b border-border/50 hover:bg-surface/50 flex items-start ${!notif.isRead ? 'bg-primary/5' : ''}`}>
                      <div className="mr-3 mt-0.5">
                        {getIconForType(notif.type, notif.severity)}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-textMain">{notif.title}</p>
                        <p className="text-xs text-textMuted mt-0.5">{notif.message}</p>
                        <p className="text-[10px] text-textMuted mt-1">{notif.time}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
        
        <div className="h-8 w-px bg-border"></div>
        
        <button className="flex items-center space-x-2 p-1.5 hover:bg-surfaceHighlight rounded-xl transition-all duration-200">
          <div className="text-right hidden md:block">
            <p className="text-sm font-medium text-textMain">{user?.username || 'User'}</p>
            <p className="text-xs text-textMuted">{user?.role || 'Guest'}</p>
          </div>
          <div className="w-8 h-8 rounded-full bg-surfaceHighlight flex items-center justify-center border border-border">
            <User className="w-4 h-4 text-textMuted" />
          </div>
        </button>
      </div>
    </header>
  );
};

export default TopBar;
