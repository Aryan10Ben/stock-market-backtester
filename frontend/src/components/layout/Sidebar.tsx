import { useState } from "react";
import { ChevronDown, Search, Crosshair, Play, Wallet, Activity } from "lucide-react";
import { Button } from "../ui/Button";

interface SectionProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

function Section({ title, icon, children, defaultOpen = false }: SectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  return (
    <div className="border-b border-border last:border-0">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between py-4 px-6 text-sm font-semibold hover:bg-card/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="text-muted">{icon}</div>
          <span>{title}</span>
        </div>
        <ChevronDown className={`h-4 w-4 text-muted transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      <div className={`overflow-hidden transition-all duration-300 ${isOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}>
        <div className="px-6 pb-5 space-y-5">
          {children}
        </div>
      </div>
    </div>
  );
}

export function Sidebar({ onRun }: { onRun: (config: any) => void }) {
  const [ticker, setTicker] = useState("");
  const [startDate, setStartDate] = useState("2023-01-01");
  const [endDate, setEndDate] = useState("2023-12-31");
  const [strategy, setStrategy] = useState("ma_crossover");
  // MA Crossover params
  const [fastWindow, setFastWindow] = useState(20);
  const [slowWindow, setSlowWindow] = useState(50);
  // RSI params
  const [rsiPeriod, setRsiPeriod] = useState(14);
  const [rsiOverbought, setRsiOverbought] = useState(70);
  const [rsiOversold, setRsiOversold] = useState(30);
  // MACD params
  const [macdFast, setMacdFast] = useState(12);
  const [macdSlow, setMacdSlow] = useState(26);
  const [macdSignal, setMacdSignal] = useState(9);
  // Bollinger params
  const [bbPeriod, setBbPeriod] = useState(20);
  const [bbStd, setBbStd] = useState(2.0);

  const [initialCapital, setInitialCapital] = useState(100000);
  const [commission, setCommission] = useState(0.001);
  const [slippage, setSlippage] = useState(5.0);
  const [isLoading, setIsLoading] = useState(false);

  const isValid = ticker.length > 0 && 
    (strategy !== "ma_crossover" || (fastWindow > 0 && slowWindow > 0 && fastWindow < slowWindow)) &&
    (strategy !== "rsi" || (rsiPeriod > 0 && rsiOverbought > rsiOversold)) &&
    (strategy !== "macd" || (macdFast > 0 && macdSlow > 0 && macdSignal > 0 && macdFast < macdSlow)) &&
    (strategy !== "bollinger" || (bbPeriod > 0 && bbStd > 0));

  const handleRun = () => {
    if (!isValid) return;
    setIsLoading(true);
    
    // Construct base config
    const config: any = {
      ticker: ticker.toUpperCase(), 
      start_date: startDate, 
      end_date: endDate, 
      strategy,
      initial_cash: initialCapital,
      commission_rate: commission,
      slippage_bps: slippage
    };

    // Add strategy specific config
    if (strategy === "ma_crossover") {
      config.fast_window = fastWindow;
      config.slow_window = slowWindow;
    } else if (strategy === "rsi") {
      config.rsi_period = rsiPeriod;
      config.rsi_overbought = rsiOverbought;
      config.rsi_oversold = rsiOversold;
    } else if (strategy === "macd") {
      config.macd_fast = macdFast;
      config.macd_slow = macdSlow;
      config.macd_signal = macdSignal;
    } else if (strategy === "bollinger") {
      config.bb_period = bbPeriod;
      config.bb_std = bbStd;
    }

    onRun(config);
    setTimeout(() => setIsLoading(false), 500);
  };

  return (
    <aside className="w-[340px] border-r border-border bg-background flex flex-col h-[calc(100vh-4rem)] sticky top-16 no-scrollbar overflow-y-auto z-40 shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
      <div className="flex-1">
        
        {/* Section 1: Stock Selection */}
        <Section title="1. Select Stock" icon={<Search className="h-4 w-4" />} defaultOpen>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
            <input 
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="e.g. AAPL"
              className="w-full h-10 pl-9 pr-3 rounded-md bg-card border border-border text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary uppercase transition-all" 
            />
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-wider font-semibold text-muted mb-2">Popular</p>
            <div className="flex flex-wrap gap-2">
              {['AAPL', 'MSFT', 'NVDA', 'SPY', 'TSLA'].map(t => (
                <button 
                  key={t}
                  onClick={() => setTicker(t)}
                  className={`text-xs px-2.5 py-1.5 rounded-md font-medium transition-colors ${ticker === t ? 'bg-primary text-primary-foreground' : 'bg-card border border-border hover:border-primary text-foreground'}`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-border mt-2">
            <div>
              <label className="text-[10px] text-muted mb-1 block uppercase tracking-wider font-semibold">From</label>
              <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-full h-8 rounded bg-card border border-border px-2 text-xs focus:outline-none focus:border-primary" />
            </div>
            <div>
              <label className="text-[10px] text-muted mb-1 block uppercase tracking-wider font-semibold">To</label>
              <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-full h-8 rounded bg-card border border-border px-2 text-xs focus:outline-none focus:border-primary" />
            </div>
          </div>
        </Section>

        {/* Section 2 & 3: Strategy */}
        <Section title="2. Strategy" icon={<Activity className="h-4 w-4" />} defaultOpen>
          <div>
            <select 
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full h-10 rounded-md bg-card border border-border px-3 text-sm focus:outline-none focus:border-primary appearance-none cursor-pointer"
            >
              <option value="ma_crossover">Moving Average Crossover</option>
              <option value="rsi">RSI Mean Reversion</option>
              <option value="macd">MACD Trend</option>
              <option value="bollinger">Bollinger Bands Breakout</option>
              <option value="buy_hold">Buy & Hold (Benchmark)</option>
            </select>
          </div>
          
          {/* Dynamic Params */}
          {strategy === "ma_crossover" && (
            <div className="p-3 bg-card/50 rounded-lg border border-border/50 space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <label className="text-xs font-medium">Fast Moving Average</label>
                  <span className="text-xs text-muted font-mono">{fastWindow}</span>
                </div>
                <input 
                  type="range" min="5" max="50" value={fastWindow} 
                  onChange={(e) => setFastWindow(parseInt(e.target.value))}
                  className="w-full accent-primary h-1 bg-border rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <label className="text-xs font-medium">Slow Moving Average</label>
                  <span className="text-xs text-muted font-mono">{slowWindow}</span>
                </div>
                <input 
                  type="range" min="20" max="200" value={slowWindow} 
                  onChange={(e) => setSlowWindow(parseInt(e.target.value))}
                  className="w-full accent-primary h-1 bg-border rounded-lg appearance-none cursor-pointer"
                />
                {fastWindow >= slowWindow && (
                  <p className="text-[10px] text-negative mt-1">Fast MA must be less than Slow MA.</p>
                )}
              </div>
            </div>
          )}

          {strategy === "rsi" && (
            <div className="p-3 bg-card/50 rounded-lg border border-border/50 space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <label className="text-xs font-medium">RSI Period</label>
                  <span className="text-xs text-muted font-mono">{rsiPeriod}</span>
                </div>
                <input 
                  type="range" min="2" max="30" value={rsiPeriod} 
                  onChange={(e) => setRsiPeriod(parseInt(e.target.value))}
                  className="w-full accent-primary h-1 bg-border rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <label className="text-xs font-medium">Overbought Level</label>
                  <span className="text-xs text-muted font-mono">{rsiOverbought}</span>
                </div>
                <input 
                  type="range" min="50" max="95" value={rsiOverbought} 
                  onChange={(e) => setRsiOverbought(parseInt(e.target.value))}
                  className="w-full accent-primary h-1 bg-border rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <label className="text-xs font-medium">Oversold Level</label>
                  <span className="text-xs text-muted font-mono">{rsiOversold}</span>
                </div>
                <input 
                  type="range" min="5" max="50" value={rsiOversold} 
                  onChange={(e) => setRsiOversold(parseInt(e.target.value))}
                  className="w-full accent-primary h-1 bg-border rounded-lg appearance-none cursor-pointer"
                />
                {rsiOversold >= rsiOverbought && (
                  <p className="text-[10px] text-negative mt-1">Oversold must be less than Overbought.</p>
                )}
              </div>
            </div>
          )}

          {strategy === "macd" && (
            <div className="p-3 bg-card/50 rounded-lg border border-border/50 space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <label className="text-xs font-medium">Fast Period</label>
                  <span className="text-xs text-muted font-mono">{macdFast}</span>
                </div>
                <input 
                  type="range" min="5" max="30" value={macdFast} 
                  onChange={(e) => setMacdFast(parseInt(e.target.value))}
                  className="w-full accent-primary h-1 bg-border rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <label className="text-xs font-medium">Slow Period</label>
                  <span className="text-xs text-muted font-mono">{macdSlow}</span>
                </div>
                <input 
                  type="range" min="15" max="60" value={macdSlow} 
                  onChange={(e) => setMacdSlow(parseInt(e.target.value))}
                  className="w-full accent-primary h-1 bg-border rounded-lg appearance-none cursor-pointer"
                />
                {macdFast >= macdSlow && (
                  <p className="text-[10px] text-negative mt-1">Fast must be less than Slow period.</p>
                )}
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <label className="text-xs font-medium">Signal Period</label>
                  <span className="text-xs text-muted font-mono">{macdSignal}</span>
                </div>
                <input 
                  type="range" min="3" max="20" value={macdSignal} 
                  onChange={(e) => setMacdSignal(parseInt(e.target.value))}
                  className="w-full accent-primary h-1 bg-border rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>
          )}

          {strategy === "bollinger" && (
            <div className="p-3 bg-card/50 rounded-lg border border-border/50 space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <label className="text-xs font-medium">Period</label>
                  <span className="text-xs text-muted font-mono">{bbPeriod}</span>
                </div>
                <input 
                  type="range" min="5" max="100" value={bbPeriod} 
                  onChange={(e) => setBbPeriod(parseInt(e.target.value))}
                  className="w-full accent-primary h-1 bg-border rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <label className="text-xs font-medium">Standard Deviations</label>
                  <span className="text-xs text-muted font-mono">{bbStd.toFixed(1)}</span>
                </div>
                <input 
                  type="range" min="1.0" max="4.0" step="0.1" value={bbStd} 
                  onChange={(e) => setBbStd(parseFloat(e.target.value))}
                  className="w-full accent-primary h-1 bg-border rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>
          )}
        </Section>

        {/* Section 4: Portfolio */}
        <Section title="3. Portfolio" icon={<Wallet className="h-4 w-4" />}>
          <div>
            <div className="flex justify-between mb-1">
              <label className="text-xs font-medium">Initial Capital</label>
              <span className="text-xs text-muted font-mono">${(initialCapital/1000).toFixed(0)}k</span>
            </div>
            <input 
              type="range" min="10000" max="1000000" step="10000" value={initialCapital} 
              onChange={(e) => setInitialCapital(parseInt(e.target.value))}
              className="w-full accent-primary h-1 bg-border rounded-lg appearance-none cursor-pointer"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4 mt-4">
            <div>
              <label className="text-[10px] text-muted mb-1 block uppercase tracking-wider font-semibold">Comm. (%)</label>
              <input 
                type="number" step="0.001" value={commission} onChange={(e) => setCommission(parseFloat(e.target.value))}
                className="w-full h-8 rounded bg-card border border-border px-2 text-xs focus:outline-none focus:border-primary" 
              />
            </div>
            <div>
              <label className="text-[10px] text-muted mb-1 block uppercase tracking-wider font-semibold">Slip (bps)</label>
              <input 
                type="number" step="0.1" value={slippage} onChange={(e) => setSlippage(parseFloat(e.target.value))}
                className="w-full h-8 rounded bg-card border border-border px-2 text-xs focus:outline-none focus:border-primary" 
              />
            </div>
          </div>
        </Section>
      </div>

      <div className="p-6 border-t border-border bg-background sticky bottom-0 z-10 shadow-[0_-10px_40px_rgba(0,0,0,0.5)]">
        <Button 
          onClick={handleRun} 
          disabled={!isValid || isLoading} 
          className="w-full h-12 text-base font-bold flex items-center justify-center gap-2 shadow-lg shadow-primary/20 transition-all"
        >
          {isLoading ? (
            <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <>
              <Play className="h-4 w-4 fill-current" />
              Run Backtest
            </>
          )}
        </Button>
      </div>
    </aside>
  );
}
