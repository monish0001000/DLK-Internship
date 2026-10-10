import React, { useState } from 'react';
import { Delete, RotateCcw, Equal, Plus, Minus, X, Percent } from 'lucide-react';

export default function Calculator() {
  const [display, setDisplay] = useState('0');
  const [expression, setExpression] = useState('');
  const [history, setHistory] = useState<string[]>([]);

  const handleNumber = (num: string) => {
    if (display === '0') {
      setDisplay(num);
    } else {
      setDisplay(display + num);
    }
  };

  const handleOperator = (op: string) => {
    setExpression(display + ' ' + op + ' ');
    setDisplay('0');
  };

  const handleClear = () => {
    setDisplay('0');
    setExpression('');
  };

  const handlePercent = () => {
    try {
      const val = parseFloat(display) / 100;
      setDisplay(val.toString());
    } catch {
      setDisplay('Error');
    }
  };

  const handleBackspace = () => {
    if (display.length > 1) {
      setDisplay(display.slice(0, -1));
    } else {
      setDisplay('0');
    }
  };

  const handleCalculate = () => {
    try {
      const fullExpression = expression + display;
      if (!fullExpression || fullExpression.includes('=')) return;

      // Safe evaluation of simple math
      // Replace operators with standard math symbols and sanitize
      const sanitized = fullExpression.replace(/x/g, '*');
      
      // Basic math regex parsing to ensure safety
      if (/^[0-9.+\-*/\s()]+$/.test(sanitized)) {
        // eslint-disable-next-line no-eval
        const result = eval(sanitized);
        const resultStr = Number(Number(result).toFixed(6)).toString(); // avoid long decimal issues
        setHistory(prev => [fullExpression + ' = ' + resultStr, ...prev].slice(0, 5));
        setDisplay(resultStr);
        setExpression('');
      } else {
        setDisplay('Error');
      }
    } catch {
      setDisplay('Error');
    }
  };

  return (
    <div className="flex flex-col md:flex-row h-full gap-4 text-on-surface">
      {/* Main Calculator */}
      <div className="flex-1 flex flex-col justify-between p-4 bg-surface-container/40 rounded-xl border border-black/10 dark:border-white/5">
        <div>
          {/* Expression display */}
          <div className="h-6 text-right font-mono text-xs text-on-surface-variant opacity-60 tracking-wider">
            {expression}
          </div>
          {/* Display */}
          <div className="text-right font-mono text-3xl font-semibold text-primary tracking-wider truncate py-2 border-b border-black/10 dark:border-white/5">
            {display}
          </div>
        </div>

        {/* Buttons Grid */}
        <div className="grid grid-cols-4 gap-2 mt-4">
          <button
            onClick={handleClear}
            className="p-4 rounded-lg bg-error-container/20 hover:bg-error-container/30 text-error font-semibold transition-colors flex items-center justify-center cursor-pointer"
            id="calc-clear"
          >
            AC
          </button>
          <button
            onClick={handleBackspace}
            className="p-4 rounded-lg bg-surface-container-highest/50 hover:bg-surface-container-highest text-on-surface-variant transition-colors flex items-center justify-center cursor-pointer"
            id="calc-backspace"
          >
            <Delete size={18} />
          </button>
          <button
            onClick={handlePercent}
            className="p-4 rounded-lg bg-surface-container-highest/50 hover:bg-surface-container-highest text-on-surface-variant transition-colors flex items-center justify-center cursor-pointer"
            id="calc-percent"
          >
            <Percent size={18} />
          </button>
          <button
            onClick={() => handleOperator('/')}
            className="p-4 rounded-lg bg-secondary-container/20 hover:bg-secondary-container/30 text-secondary font-semibold transition-colors flex items-center justify-center cursor-pointer"
            id="calc-div"
          >
            /
          </button>

          {['7', '8', '9'].map(num => (
            <button
              key={num}
              onClick={() => handleNumber(num)}
              className="p-4 rounded-lg bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 font-mono text-lg font-medium transition-colors cursor-pointer text-on-surface"
              id={`calc-${num}`}
            >
              {num}
            </button>
          ))}
          <button
            onClick={() => handleOperator('x')}
            className="p-4 rounded-lg bg-secondary-container/20 hover:bg-secondary-container/30 text-secondary font-semibold transition-colors flex items-center justify-center cursor-pointer"
            id="calc-mul"
          >
            <X size={16} />
          </button>

          {['4', '5', '6'].map(num => (
            <button
              key={num}
              onClick={() => handleNumber(num)}
              className="p-4 rounded-lg bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 font-mono text-lg font-medium transition-colors cursor-pointer text-on-surface"
              id={`calc-${num}`}
            >
              {num}
            </button>
          ))}
          <button
            onClick={() => handleOperator('-')}
            className="p-4 rounded-lg bg-secondary-container/20 hover:bg-secondary-container/30 text-secondary font-semibold transition-colors flex items-center justify-center cursor-pointer"
            id="calc-sub"
          >
            <Minus size={18} />
          </button>

          {['1', '2', '3'].map(num => (
            <button
              key={num}
              onClick={() => handleNumber(num)}
              className="p-4 rounded-lg bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 font-mono text-lg font-medium transition-colors cursor-pointer text-on-surface"
              id={`calc-${num}`}
            >
              {num}
            </button>
          ))}
          <button
            onClick={() => handleOperator('+')}
            className="p-4 rounded-lg bg-secondary-container/20 hover:bg-secondary-container/30 text-secondary font-semibold transition-colors flex items-center justify-center cursor-pointer"
            id="calc-add"
          >
            <Plus size={18} />
          </button>

          <button
            onClick={() => handleNumber('0')}
            className="p-4 col-span-2 rounded-lg bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 font-mono text-lg font-medium transition-colors text-center cursor-pointer text-on-surface"
            id="calc-0"
          >
            0
          </button>
          <button
            onClick={() => handleNumber('.')}
            className="p-4 rounded-lg bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 font-mono text-lg font-medium transition-colors cursor-pointer text-on-surface"
            id="calc-dot"
          >
            .
          </button>
          <button
            onClick={handleCalculate}
            className="p-4 rounded-lg bg-primary hover:bg-primary-container text-on-primary font-semibold transition-colors flex items-center justify-center cursor-pointer"
            id="calc-eq"
          >
            <Equal size={18} />
          </button>
        </div>
      </div>

      {/* History panel */}
      <div className="w-full md:w-48 p-4 bg-surface-container-high/30 rounded-xl border border-black/10 dark:border-white/5 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between text-xs font-semibold opacity-70 tracking-wider uppercase mb-3">
            <span>History</span>
            <RotateCcw
              size={12}
              className="cursor-pointer hover:text-primary transition-colors"
              onClick={() => setHistory([])}
            />
          </div>
          <div className="space-y-2 max-h-56 overflow-y-auto custom-scrollbar">
            {history.length === 0 ? (
              <p className="text-xs text-on-surface-variant opacity-50 italic py-2">
                No calculations yet
              </p>
            ) : (
              history.map((item, idx) => (
                <div
                  key={idx}
                  className="p-2 bg-black/5 dark:bg-black/20 rounded border border-black/5 dark:border-white/5 text-right font-mono text-xs text-on-surface-variant hover:text-on-surface hover:bg-black/10 dark:hover:bg-black/30 transition-all cursor-pointer"
                  onClick={() => {
                    const resultPart = item.split('=').pop()?.trim();
                    if (resultPart) setDisplay(resultPart);
                  }}
                >
                  {item}
                </div>
              ))
            )}
          </div>
        </div>
        <p className="text-[10px] text-on-surface-variant opacity-40 leading-normal mt-2">
          Click history item to load its result back into memory.
        </p>
      </div>
    </div>
  );
}
