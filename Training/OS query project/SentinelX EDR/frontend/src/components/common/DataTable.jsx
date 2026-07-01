import React from 'react';
import { Search, ChevronUp, ChevronDown, Filter } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const cn = (...inputs) => twMerge(clsx(inputs));

const DataTable = ({ 
  columns, 
  data, 
  onRowClick,
  searchPlaceholder = "Search...",
  className
}) => {
  const [searchTerm, setSearchTerm] = React.useState("");
  const [sortConfig, setSortConfig] = React.useState({ key: null, direction: 'asc' });

  // Handle Search
  const filteredData = React.useMemo(() => {
    if (!searchTerm) return data;
    
    const lowercasedSearch = searchTerm.toLowerCase();
    return data.filter(item => {
      return Object.values(item).some(
        val => val && String(val).toLowerCase().includes(lowercasedSearch)
      );
    });
  }, [data, searchTerm]);

  // Handle Sort
  const sortedData = React.useMemo(() => {
    let sortableItems = [...filteredData];
    if (sortConfig.key !== null) {
      sortableItems.sort((a, b) => {
        const aVal = a[sortConfig.key];
        const bVal = b[sortConfig.key];
        
        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }
    return sortableItems;
  }, [filteredData, sortConfig]);

  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  return (
    <div className={cn("glass-panel flex flex-col overflow-hidden", className)}>
      {/* Toolbar */}
      <div className="p-4 border-b border-border flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-textMuted" />
          <input
            type="text"
            placeholder={searchPlaceholder}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-background/50 border border-border rounded-lg pl-9 pr-4 py-2 text-sm text-textMain focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-200"
          />
        </div>
        <button className="btn-secondary flex items-center text-sm py-2">
          <Filter className="w-4 h-4 mr-2" />
          Filters
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-surfaceHighlight/30 border-b border-border">
              {columns.map((column) => (
                <th 
                  key={column.key}
                  className={cn(
                    "p-4 text-sm font-semibold text-textMuted whitespace-nowrap select-none",
                    column.sortable !== false && "cursor-pointer hover:text-textMain transition-colors"
                  )}
                  onClick={() => column.sortable !== false && requestSort(column.key)}
                >
                  <div className="flex items-center">
                    {column.header}
                    {column.sortable !== false && (
                      <span className="ml-2 inline-flex flex-col">
                        <ChevronUp className={cn("w-3 h-3 -mb-1", sortConfig.key === column.key && sortConfig.direction === 'asc' ? "text-primary" : "text-textMuted/50")} />
                        <ChevronDown className={cn("w-3 h-3", sortConfig.key === column.key && sortConfig.direction === 'desc' ? "text-primary" : "text-textMuted/50")} />
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedData.length > 0 ? (
              sortedData.map((row, i) => (
                <tr 
                  key={row.id || i} 
                  onClick={() => onRowClick && onRowClick(row)}
                  className={cn(
                    "border-b border-border/50 hover:bg-surfaceHighlight/30 transition-colors",
                    onRowClick && "cursor-pointer"
                  )}
                >
                  {columns.map((column) => (
                    <td key={`${row.id || i}-${column.key}`} className="p-4 text-sm text-textMain">
                      {column.render ? column.render(row[column.key], row) : row[column.key]}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="p-8 text-center text-textMuted">
                  No data found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      {/* Footer / Pagination Placeholder */}
      <div className="p-4 border-t border-border flex items-center justify-between text-sm text-textMuted">
        <span>Showing {sortedData.length} entries</span>
        <div className="flex space-x-1">
          <button className="px-3 py-1 rounded hover:bg-surfaceHighlight disabled:opacity-50" disabled>Prev</button>
          <button className="px-3 py-1 rounded bg-primary text-white">1</button>
          <button className="px-3 py-1 rounded hover:bg-surfaceHighlight disabled:opacity-50" disabled>Next</button>
        </div>
      </div>
    </div>
  );
};

export default DataTable;
