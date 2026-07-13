import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { ShieldAlert, AlertTriangle, Info, Terminal, Globe, FileKey, User } from 'lucide-react';

const cn = (...inputs) => twMerge(clsx(inputs));

const getIcon = (type) => {
  switch(type) {
    case 'process': return Terminal;
    case 'network': return Globe;
    case 'file': return FileKey;
    case 'user': return User;
    case 'alert': return ShieldAlert;
    case 'warning': return AlertTriangle;
    default: return Info;
  }
};

const getColorClass = (severity) => {
  switch(severity) {
    case 'critical': return "text-danger bg-danger/10 border-danger/30";
    case 'high': return "text-warning bg-warning/10 border-warning/30";
    case 'medium': return "text-yellow-400 bg-yellow-400/10 border-yellow-400/30";
    case 'info': return "text-primary bg-primary/10 border-primary/30";
    default: return "text-textMuted bg-surfaceHighlight border-border";
  }
};

const Timeline = ({ events }) => {
  return (
    <div className="relative border-l-2 border-border ml-4 space-y-8 py-4">
      {events.map((event, index) => {
        const Icon = getIcon(event.type);
        const colorClass = getColorClass(event.severity);
        
        return (
          <div key={event.id || index} className="relative pl-8 animate-slide-up" style={{ animationDelay: `${index * 50}ms` }}>
            {/* Timeline Node */}
            <div className={cn(
              "absolute -left-[17px] top-1 w-8 h-8 rounded-full border-2 border-background flex items-center justify-center shadow-lg",
              colorClass
            )}>
              <Icon className="w-4 h-4" />
            </div>
            
            {/* Event Content */}
            <div className="glass-panel p-4 hover:border-primary/50 transition-colors cursor-pointer group">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <span className="text-xs font-mono text-textMuted mb-1 block">{event.timestamp}</span>
                  <h4 className="text-sm font-semibold text-textMain group-hover:text-primary transition-colors">{event.title}</h4>
                </div>
                {event.mitre && (
                  <span className="text-xs font-mono px-2 py-1 bg-surfaceHighlight text-textMuted rounded border border-border">
                    {event.mitre}
                  </span>
                )}
              </div>
              <p className="text-sm text-textMuted">{event.description}</p>
              
              {/* Optional Code/Metadata Block */}
              {event.metadata && (
                <div className="mt-3 p-3 bg-background/50 border border-border rounded text-xs font-mono text-textMuted overflow-x-auto">
                  {Object.entries(event.metadata).map(([k, v]) => (
                    <div key={k} className="flex">
                      <span className="text-primary/70 w-24 flex-shrink-0">{k}:</span>
                      <span className="text-textMain">{String(v)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default Timeline;
