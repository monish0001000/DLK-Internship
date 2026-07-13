import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const cn = (...inputs) => twMerge(clsx(inputs));

const StatCard = ({ title, value, icon: Icon, trend, trendValue, colorClass }) => {
  return (
    <div className="glass-panel p-6 hover:-translate-y-1 transition-transform duration-300">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-textMuted text-sm font-medium">{title}</p>
          <h3 className="text-3xl font-bold mt-2 text-textMain tracking-tight">{value}</h3>
          
          {trend && (
            <div className="flex items-center mt-4">
              <span className={cn(
                "text-xs font-semibold px-2 py-1 rounded-full",
                trend === 'up' ? "text-danger bg-danger/10" : 
                trend === 'down' ? "text-accent bg-accent/10" : "text-textMuted bg-surfaceHighlight"
              )}>
                {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {trendValue}
              </span>
              <span className="text-xs text-textMuted ml-2">vs last 24h</span>
            </div>
          )}
        </div>
        
        <div className={cn("p-3 rounded-xl", colorClass || "bg-primary/10 text-primary")}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
};

export default StatCard;
