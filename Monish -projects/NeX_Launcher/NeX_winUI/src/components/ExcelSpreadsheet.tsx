import React, { useState, useEffect } from 'react';
import { Table, Save, Check, RefreshCw, HelpCircle, FileSpreadsheet } from 'lucide-react';

interface ExcelSpreadsheetProps {
  onSaveFile?: (name: string, type: 'sheet', content: string) => void;
  addLog?: (msg: string) => void;
}

type CellData = Record<string, string>;

export default function ExcelSpreadsheet({ onSaveFile, addLog }: ExcelSpreadsheetProps) {
  const [grid, setGrid] = useState<CellData>({});
  const [activeCell, setActiveCell] = useState<string | null>(null);
  const [formulaValue, setFormulaValue] = useState('');
  const [sheetName, setSheetName] = useState('Network_Telemetry_Log');
  const [saveSuccess, setSaveSuccess] = useState(false);

  const cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];
  const rows = Array.from({ length: 10 }, (_, i) => i + 1);

  // Initialize spreadsheet with mock log data
  useEffect(() => {
    loadTemplate('telemetry');
  }, []);

  const templates: Record<string, CellData> = {
    telemetry: {
      A1: 'LOG PARAMETER', B1: 'NODE-01', C1: 'NODE-02', D1: 'NODE-03', E1: 'TOTAL', F1: 'AVERAGE',
      A2: 'Ping Rate (ms)', B2: '12', C2: '18', D2: '15', E2: '=SUM(B2:D2)', F2: '=AVERAGE(B2:D2)',
      A3: 'Packet Drop %', B3: '0.00', C3: '0.04', D3: '0.01', E3: '=SUM(B3:D3)', F3: '=AVERAGE(B3:D3)',
      A4: 'Active Cores', B4: '4', C4: '4', D4: '8', E4: '=SUM(B4:D4)', F4: '=AVERAGE(B4:D4)',
      A5: 'CPU Load %', B5: '42', C5: '68', D5: '35', E5: '=SUM(B5:D5)', F5: '=AVERAGE(B5:D5)',
      A6: 'RAM Available (GB)', B6: '12', C6: '10', D6: '15', E6: '=SUM(B6:D6)', F6: '=AVERAGE(B6:D6)',
    },
    budget: {
      A1: 'SECURITY COST', B1: 'Q1 ESTIMATE', C1: 'Q2 ESTIMATE', D1: 'Q3 ESTIMATE', E1: 'TOTAL',
      A2: 'DNS Firewall v4', B2: '2400', C2: '2400', D2: '2800', E2: '=SUM(B2:D2)',
      A3: 'SSL Portal Certs', B3: '350', C3: '350', D3: '420', E3: '=SUM(B3:D3)',
      A4: 'Kiosk Enclosure', B4: '1200', C4: '0', D4: '0', E4: '=SUM(B4:D4)',
      A5: 'Audit Hardware', B5: '850', C5: '120', D5: '450', E5: '=SUM(B5:D5)',
      A6: 'TOTAL OUTLAY', B6: '=SUM(B2:B5)', C6: '=SUM(C2:C5)', D6: '=SUM(D2:D5)', E6: '=SUM(E2:E5)',
    }
  };

  const loadTemplate = (name: string) => {
    setGrid(templates[name] || {});
    if (addLog) addLog(`Spreadsheet simulator loaded template: ${name}`);
  };

  const handleCellSelect = (cellId: string) => {
    setActiveCell(cellId);
    setFormulaValue(grid[cellId] || '');
  };

  const handleCellChange = (value: string) => {
    if (!activeCell) return;
    setGrid(prev => ({
      ...prev,
      [activeCell]: value
    }));
    setFormulaValue(value);
  };

  // Helper to parse cell references like 'B2' and return its parsed numeric value
  const getCellValue = (ref: string, currentGrid: CellData): number => {
    const cleanRef = ref.trim().toUpperCase();
    const value = currentGrid[cleanRef];
    if (!value) return 0;
    if (value.startsWith('=')) {
      // It's a formula, evaluate it recursively (or return fallback to avoid infinite loops)
      return parseFloat(evaluateFormula(value, currentGrid)) || 0;
    }
    return parseFloat(value) || 0;
  };

  // Evaluate cell range like 'B2:D2'
  const getRangeValues = (rangeStr: string, currentGrid: CellData): number[] => {
    const [start, end] = rangeStr.split(':').map(s => s.trim().toUpperCase());
    if (!start || !end) return [];

    const startCol = start.charCodeAt(0);
    const startRow = parseInt(start.substring(1));
    const endCol = end.charCodeAt(0);
    const endRow = parseInt(end.substring(1));

    if (isNaN(startRow) || isNaN(endRow)) return [];

    const values: number[] = [];
    const minCol = Math.min(startCol, endCol);
    const maxCol = Math.max(startCol, endCol);
    const minRow = Math.min(startRow, endRow);
    const maxRow = Math.max(startRow, endRow);

    for (let col = minCol; col <= maxCol; col++) {
      for (let row = minRow; row <= maxRow; row++) {
        const cellId = String.fromCharCode(col) + row;
        values.push(getCellValue(cellId, currentGrid));
      }
    }
    return values;
  };

  // Safe evaluation of simple formulas
  const evaluateFormula = (val: string, currentGrid: CellData): string => {
    if (!val || !val.startsWith('=')) return val;

    try {
      const formula = val.substring(1).trim().toUpperCase();
      
      // SUM(A1:B3)
      if (formula.startsWith('SUM(') && formula.endsWith(')')) {
        const range = formula.substring(4, formula.length - 1);
        const numbers = getRangeValues(range, currentGrid);
        const sum = numbers.reduce((acc, curr) => acc + curr, 0);
        return Number(sum.toFixed(2)).toString();
      }

      // AVERAGE(A1:B3)
      if (formula.startsWith('AVERAGE(') && formula.endsWith(')')) {
        const range = formula.substring(8, formula.length - 1);
        const numbers = getRangeValues(range, currentGrid);
        if (numbers.length === 0) return '0';
        const sum = numbers.reduce((acc, curr) => acc + curr, 0);
        const avg = sum / numbers.length;
        return Number(avg.toFixed(2)).toString();
      }

      // Simple addition A1+B1
      if (formula.includes('+')) {
        const parts = formula.split('+');
        const numbers = parts.map(p => getCellValue(p, currentGrid));
        const sum = numbers.reduce((acc, curr) => acc + curr, 0);
        return Number(sum.toFixed(2)).toString();
      }

      return 'Formula Error';
    } catch {
      return 'Error';
    }
  };

  const handleSave = () => {
    const filename = sheetName.trim().endsWith('.sheet') ? sheetName.trim() : `${sheetName.trim()}.sheet`;
    if (onSaveFile) {
      onSaveFile(filename, 'sheet', JSON.stringify(grid));
      setSaveSuccess(true);
      if (addLog) addLog(`Saved spreadsheet file to local node: ${filename}`);
      setTimeout(() => setSaveSuccess(false), 2000);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row h-full gap-4 text-on-surface">
      {/* Sidebar Controls */}
      <div className="w-full lg:w-64 flex flex-col gap-3 p-4 bg-surface-container/40 rounded-xl border border-black/10 dark:border-white/5">
        <div>
          <h3 className="text-sm font-semibold opacity-70 uppercase tracking-wider mb-2">Preset Sheets</h3>
          <div className="space-y-1.5">
            <button
              onClick={() => loadTemplate('telemetry')}
              className="w-full text-left p-2.5 bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 rounded-lg text-xs flex items-center gap-2 border border-black/5 dark:border-white/5 transition-colors cursor-pointer text-on-surface"
              id="excel-temp-tele"
            >
              <FileSpreadsheet size={14} className="text-primary" />
              <span>Network Telemetry Log</span>
            </button>
            <button
              onClick={() => loadTemplate('budget')}
              className="w-full text-left p-2.5 bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 rounded-lg text-xs flex items-center gap-2 border border-black/5 dark:border-white/5 transition-colors cursor-pointer text-on-surface"
              id="excel-temp-budget"
            >
              <FileSpreadsheet size={14} className="text-secondary" />
              <span>Security Operations Budget</span>
            </button>
            <button
              onClick={() => {
                setGrid({});
                if (addLog) addLog('Reset spreadsheet workspace to empty.');
              }}
              className="w-full text-left p-2 bg-black/10 dark:bg-black/15 hover:bg-black/20 dark:hover:bg-black/25 rounded-lg text-xs text-on-surface-variant italic text-center transition-colors cursor-pointer"
              id="excel-temp-clear"
            >
              Reset Sheet Grid
            </button>
          </div>
        </div>

        {/* Formula Instructions */}
        <div className="p-3 bg-black/5 dark:bg-black/15 rounded-lg border border-black/10 dark:border-white/5 text-[10px] text-on-surface-variant space-y-1.5 leading-normal">
          <p className="font-semibold text-primary">Supported Formulas:</p>
          <p className="font-mono bg-black/10 dark:bg-black/30 p-1 rounded text-center text-on-surface">=SUM(B2:D2)</p>
          <p className="font-mono bg-black/10 dark:bg-black/30 p-1 rounded text-center text-on-surface">=AVERAGE(B2:D2)</p>
          <p className="font-mono bg-black/10 dark:bg-black/30 p-1 rounded text-center text-on-surface">=B2+C2</p>
          <p className="opacity-70">Formulas evaluate in real-time when focus shifts.</p>
        </div>

        {/* Save/Export */}
        <div className="mt-auto pt-3 border-t border-black/10 dark:border-white/5 space-y-2">
          <h3 className="text-xs font-semibold opacity-70 uppercase tracking-wider mb-1">Save Sheet to Kiosk</h3>
          <input
            type="text"
            value={sheetName}
            onChange={(e) => setSheetName(e.target.value.replace(/[^a-zA-Z0-9_-]/g, ''))}
            placeholder="sheet_name"
            className="w-full text-xs bg-black/5 dark:bg-black/30 border border-black/10 dark:border-white/10 focus:border-primary/50 rounded p-2 text-on-surface font-mono outline-none"
            id="excel-sheet-name"
          />
          <button
            onClick={handleSave}
            className={`w-full p-2.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer ${
              saveSuccess
                ? 'bg-tertiary text-on-tertiary shadow-[0_0_12px_rgba(101,248,151,0.3)]'
                : 'bg-primary hover:bg-primary-container text-on-primary'
            }`}
            id="excel-save-btn"
          >
            {saveSuccess ? (
              <>
                <Check size={14} />
                Saved Table!
              </>
            ) : (
              <>
                <Save size={14} />
                Save Spreadsheet (.sheet)
              </>
            )}
          </button>
        </div>
      </div>

      {/* Sheet Space */}
      <div className="flex-1 bg-surface-container-low/60 rounded-xl border border-black/10 dark:border-white/5 p-3 flex flex-col gap-3 overflow-hidden">
        {/* Formula Bar */}
        <div className="flex items-center bg-surface-container-high/60 border border-black/10 dark:border-white/10 rounded-lg p-2 gap-2 text-xs">
          <span className="font-bold text-primary font-mono select-none px-2 py-0.5 bg-primary/10 border border-primary/20 rounded">
            {activeCell || 'Fx'}
          </span>
          <span className="text-on-surface-variant font-mono opacity-60 font-semibold">=</span>
          <input
            type="text"
            value={formulaValue}
            onChange={(e) => handleCellChange(e.target.value)}
            placeholder="Select a cell to enter a formula or a value (e.g., 42, or =SUM(B2:D2))"
            disabled={!activeCell}
            className="flex-1 bg-transparent border-0 outline-none text-on-surface font-mono text-xs p-0 focus:ring-0"
            id="excel-formula-bar"
          />
        </div>

        {/* Scrollable Spreadsheet Table */}
        <div className="flex-1 overflow-auto custom-scrollbar border border-black/10 dark:border-white/10 rounded-lg">
          <table className="w-full border-collapse text-left font-mono text-xs">
            <thead>
              <tr className="bg-surface-container-highest/60 select-none">
                <th className="p-2 border border-black/5 dark:border-white/5 w-10 text-center text-on-surface-variant font-bold bg-black/10 dark:bg-black/20"></th>
                {cols.map(col => (
                  <th key={col} className="p-2 border border-black/5 dark:border-white/5 text-center text-on-surface font-bold">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map(row => (
                <tr key={row} className="hover:bg-black/[0.02] dark:hover:bg-white/[0.01]">
                  <td className="p-2 border border-black/5 dark:border-white/5 bg-black/10 dark:bg-black/20 font-bold text-center text-on-surface-variant select-none">
                    {row}
                  </td>
                  {cols.map(col => {
                    const cellId = col + row;
                    const val = grid[cellId] || '';
                    const isFormula = val.startsWith('=');
                    const displayValue = isFormula ? evaluateFormula(val, grid) : val;
                    const isSelected = activeCell === cellId;

                    return (
                      <td
                        key={col}
                        onClick={() => handleCellSelect(cellId)}
                        className={`p-2 border border-black/5 dark:border-white/5 cursor-cell transition-colors relative truncate max-w-[120px] ${
                          isSelected
                            ? 'bg-primary/25 border-primary/60 text-primary font-semibold'
                            : isFormula
                            ? 'bg-secondary/10 text-secondary hover:bg-secondary/15'
                            : 'hover:bg-black/5 dark:hover:bg-white/5 text-on-surface-variant hover:text-on-surface'
                        }`}
                        title={`${cellId}: ${val}`}
                      >
                        {displayValue}
                        {isFormula && !isSelected && (
                          <span className="absolute top-0 right-0 w-1 h-1 bg-secondary rounded-bl-sm" />
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Informative Footer */}
        <div className="flex items-center justify-between text-[11px] text-on-surface-variant opacity-60 font-mono px-1">
          <span>Click any cell to edit. Formulas sum/average matching matrix records instantly.</span>
          <span className="flex items-center gap-1">
            <HelpCircle size={10} className="text-secondary" />
            Grid dimensions A1 to G10.
          </span>
        </div>
      </div>
    </div>
  );
}
