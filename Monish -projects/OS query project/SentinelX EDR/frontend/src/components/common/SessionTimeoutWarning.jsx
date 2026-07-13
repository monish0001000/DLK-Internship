import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Clock, RefreshCw, LogOut } from 'lucide-react';

const SessionTimeoutWarning = () => {
  const { sessionWarning, timeLeft, extendSession, logout } = useAuth();

  if (!sessionWarning) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in">
      <div className="bg-surfaceHighlight border border-border shadow-2xl rounded-2xl p-6 max-w-sm w-full relative overflow-hidden">
        {/* Progress Bar background */}
        <div 
          className="absolute bottom-0 left-0 h-1 bg-primary/20 w-full"
        >
          {/* Progress Bar active */}
          <div 
            className="h-full bg-primary transition-all duration-1000 ease-linear" 
            style={{ width: `${(timeLeft / 60) * 100}%` }}
          ></div>
        </div>

        <div className="flex flex-col items-center text-center">
          <div className="w-16 h-16 bg-warning/20 rounded-full flex items-center justify-center mb-4">
            <Clock className="w-8 h-8 text-warning animate-pulse" />
          </div>
          
          <h2 className="text-xl font-bold text-textMain mb-2">Session Expiring</h2>
          <p className="text-sm text-textMuted mb-6">
            For your security, your session will automatically end in <strong className="text-white">{timeLeft} seconds</strong> due to inactivity.
          </p>

          <div className="flex w-full space-x-3">
            <button 
              onClick={logout}
              className="flex-1 py-2 px-4 bg-surface border border-border rounded-xl text-sm font-medium text-textMain hover:bg-surfaceHighlight transition-colors flex items-center justify-center"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout Now
            </button>
            <button 
              onClick={extendSession}
              className="flex-1 py-2 px-4 bg-primary text-white rounded-xl text-sm font-medium hover:bg-primaryHover transition-colors flex items-center justify-center shadow-lg shadow-primary/20"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Continue
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionTimeoutWarning;
