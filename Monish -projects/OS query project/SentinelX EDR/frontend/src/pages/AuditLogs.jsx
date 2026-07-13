import React, { useState, useEffect } from 'react';
import { getAuditLogs } from '../services/api';
import { format } from 'date-fns';
import { Download, ChevronLeft, ChevronRight } from 'lucide-react';

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Pagination
  const [page, setPage] = useState(1);
  const [limit] = useState(50);
  const [hasMore, setHasMore] = useState(false);

  // Filters
  const [filters, setFilters] = useState({
    user: '',
    action: '',
    status: '',
    endpoint: '',
    request_id: '',
    start_date: '',
    end_date: ''
  });

  // Track applied filters separately to avoid fetching on every keystroke
  const [appliedFilters, setAppliedFilters] = useState({ ...filters });

  useEffect(() => {
    fetchLogs(page, appliedFilters);
  }, [page, appliedFilters]);

  const fetchLogs = async (currentPage, currentFilters) => {
    setLoading(true);
    try {
      const activeFilters = Object.fromEntries(Object.entries(currentFilters).filter(([_, v]) => v !== ''));
      const offset = (currentPage - 1) * limit;
      
      const response = await getAuditLogs({ ...activeFilters, limit: limit + 1, offset });
      
      const data = response.data || [];
      if (data.length > limit) {
        setHasMore(true);
        setLogs(data.slice(0, limit));
      } else {
        setHasMore(false);
        setLogs(data);
      }
    } catch (error) {
      console.error('Failed to fetch audit logs', error);
      setLogs([]);
    }
    setLoading(false);
  };

  const applyFilters = () => {
    setPage(1);
    setAppliedFilters({ ...filters });
  };

  const clearFilters = () => {
    const empty = { user: '', action: '', status: '', endpoint: '', request_id: '', start_date: '', end_date: '' };
    setFilters(empty);
    setPage(1);
    setAppliedFilters(empty);
  };

  const exportCSV = async (mode) => {
    let dataToExport = logs;
    
    if (mode === 'all') {
      try {
        const activeFilters = Object.fromEntries(Object.entries(appliedFilters).filter(([_, v]) => v !== ''));
        const response = await getAuditLogs({ ...activeFilters, limit: 10000 }); // Large limit for server-side
        dataToExport = response.data || [];
      } catch (e) {
        console.error('Export failed', e);
        return;
      }
    }

    if (dataToExport.length === 0) return;

    const headers = ['Timestamp', 'User', 'Action', 'Endpoint', 'Request ID', 'Status', 'IP Address'];
    const csvRows = [headers.join(',')];
    
    dataToExport.forEach(log => {
      csvRows.push([
        log.timestamp,
        log.user,
        `"${log.action || ''}"`,
        `"${log.endpoint || log.target || ''}"`,
        log.request_id || '',
        log.status,
        log.ip_address || ''
      ].join(','));
    });
    
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', `audit_logs_${format(new Date(), 'yyyyMMdd')}.csv`);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">Audit Logs</h1>
          <p className="text-sm text-gray-400">Track user activity and system events</p>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => exportCSV('page')}
            className="inline-flex items-center px-3 py-1.5 border border-gray-600 rounded-md shadow-sm text-sm font-medium text-white bg-gray-700 hover:bg-gray-600 focus:outline-none transition-colors"
          >
            <Download className="-ml-1 mr-2 h-4 w-4" />
            Export Page
          </button>
          <button
            onClick={() => exportCSV('all')}
            className="inline-flex items-center px-3 py-1.5 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none transition-colors"
          >
            <Download className="-ml-1 mr-2 h-4 w-4" />
            Export All (Filtered)
          </button>
        </div>
      </div>

      {/* Advanced Filters */}
      <div className="bg-gray-800 rounded-lg shadow border border-gray-700 p-5">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">User</label>
            <input
              type="text"
              className="block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm px-3 py-2"
              placeholder="Username..."
              value={filters.user}
              onChange={(e) => setFilters({ ...filters, user: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Action</label>
            <input
              type="text"
              className="block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm px-3 py-2"
              placeholder="E.g. user.login"
              value={filters.action}
              onChange={(e) => setFilters({ ...filters, action: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Endpoint</label>
            <input
              type="text"
              className="block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm px-3 py-2"
              placeholder="Hostname or IP..."
              value={filters.endpoint}
              onChange={(e) => setFilters({ ...filters, endpoint: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Status</label>
            <select
              className="block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm px-3 py-2"
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            >
              <option value="">All Statuses</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
              <option value="denied">Denied</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Request ID</label>
            <input
              type="text"
              className="block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm px-3 py-2"
              placeholder="Req ID..."
              value={filters.request_id}
              onChange={(e) => setFilters({ ...filters, request_id: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Start Date</label>
            <input
              type="datetime-local"
              className="block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm px-3 py-2"
              value={filters.start_date}
              onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">End Date</label>
            <input
              type="datetime-local"
              className="block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm px-3 py-2"
              value={filters.end_date}
              onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
            />
          </div>
          <div className="flex items-end space-x-2">
            <button
              onClick={applyFilters}
              className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors"
            >
              Search
            </button>
            <button
              onClick={clearFilters}
              className="flex-1 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-md text-sm font-medium transition-colors"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-gray-800 shadow rounded-lg border border-gray-700 flex flex-col min-h-[500px]">
        <div className="overflow-x-auto flex-1">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="bg-gray-900 sticky top-0 z-10">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Timestamp</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">User</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Action</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Endpoint</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Request ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700 bg-gray-800">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-sm text-gray-400">Loading logs...</td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-sm text-gray-400">No audit logs found matching criteria.</td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-700/50 transition-colors">
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-300">
                      {log.timestamp ? format(new Date(log.timestamp), 'yyyy-MM-dd HH:mm:ss') : '-'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-white">{log.user || '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-300">{log.action || '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-400 font-mono text-xs">{log.endpoint || log.target || '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        log.status === 'success' ? 'bg-green-100 text-green-800' : 
                        log.status === 'denied' ? 'bg-orange-100 text-orange-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {log.status || 'unknown'}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 font-mono text-xs">{log.request_id || '-'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination Footer */}
        <div className="bg-gray-900 px-4 py-3 border-t border-gray-700 flex items-center justify-between sm:px-6">
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-400">
                Showing <span className="font-medium text-white">{logs.length > 0 ? (page - 1) * limit + 1 : 0}</span> to <span className="font-medium text-white">{Math.min(page * limit, (page - 1) * limit + logs.length)}</span> results
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1 || loading}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-600 bg-gray-800 text-sm font-medium text-gray-400 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="sr-only">Previous</span>
                  <ChevronLeft className="h-5 w-5" aria-hidden="true" />
                </button>
                <span className="relative inline-flex items-center px-4 py-2 border border-gray-600 bg-gray-800 text-sm font-medium text-white">
                  Page {page}
                </span>
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={!hasMore || loading}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-600 bg-gray-800 text-sm font-medium text-gray-400 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="sr-only">Next</span>
                  <ChevronRight className="h-5 w-5" aria-hidden="true" />
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
