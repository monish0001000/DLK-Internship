import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/common/Sidebar';
import TopBar from '../components/common/TopBar';

const DashboardLayout = () => {
  return (
    <div className="flex h-screen bg-background overflow-hidden text-textMain selection:bg-primary/30">
      {/* Sidebar Navigation */}
      <Sidebar />
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopBar />
        
        {/* Page Content */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-6">
          <div className="max-w-7xl mx-auto w-full animate-fade-in">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
