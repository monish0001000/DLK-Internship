import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';

import Dashboard from './pages/Dashboard';

import Endpoints from './pages/Endpoints';

import Alerts from './pages/Alerts';

import Investigations from './pages/Investigations';

import Cases from './pages/Cases';
import ThreatHunting from './pages/ThreatHunting';

import DetectionRules from './pages/DetectionRules';
import Simulation from './pages/Simulation';
import Settings from './pages/Settings';

import AuditLogs from './pages/AuditLogs';
import HealthDashboard from './pages/HealthDashboard';
import Login from './pages/Login';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import { PERMISSIONS } from './utils/permissions';
import SessionTimeoutWarning from './components/common/SessionTimeoutWarning';

function App() {
  return (
    <AuthProvider>
      <SessionTimeoutWarning />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<ProtectedRoute requiredPermission={PERMISSIONS.VIEW_DASHBOARD}><Dashboard /></ProtectedRoute>} />
            <Route path="endpoints" element={<ProtectedRoute requiredPermission={PERMISSIONS.VIEW_ENDPOINTS}><Endpoints /></ProtectedRoute>} />
            <Route path="alerts" element={<ProtectedRoute requiredPermission={PERMISSIONS.VIEW_ALERTS}><Alerts /></ProtectedRoute>} />
            <Route path="investigations" element={<ProtectedRoute requiredPermission={PERMISSIONS.VIEW_INVESTIGATIONS}><Investigations /></ProtectedRoute>} />
            <Route path="cases" element={<ProtectedRoute requiredPermission={PERMISSIONS.VIEW_CASES}><Cases /></ProtectedRoute>} />
            <Route path="hunting" element={<ProtectedRoute requiredPermission={PERMISSIONS.VIEW_HUNTING}><ThreatHunting /></ProtectedRoute>} />
            <Route path="rules" element={<ProtectedRoute requiredPermission={PERMISSIONS.VIEW_RULES}><DetectionRules /></ProtectedRoute>} />
            <Route path="simulation" element={<ProtectedRoute requiredPermission={PERMISSIONS.VIEW_SIMULATIONS}><Simulation /></ProtectedRoute>} />
            <Route path="settings" element={<ProtectedRoute requiredPermission={PERMISSIONS.VIEW_SETTINGS}><Settings /></ProtectedRoute>} />
            <Route path="audit" element={<ProtectedRoute requiredPermission={PERMISSIONS.VIEW_AUDIT}><AuditLogs /></ProtectedRoute>} />
            <Route path="health" element={<ProtectedRoute requiredPermission={PERMISSIONS.VIEW_HEALTH}><HealthDashboard /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
