import { useState, useEffect } from 'react';
import { TopNav } from './components/layout/TopNav';
import { Sidebar } from './components/layout/Sidebar';
import { HeroHeader } from './components/dashboard/HeroHeader';
import { KPIGrid } from './components/dashboard/KPIGrid';
import { ChartSection } from './components/dashboard/ChartSection';
import { TradeHistory } from './components/dashboard/TradeHistory';
import { ErrorState } from './components/dashboard/ErrorState';
import { EmptyState } from './components/dashboard/EmptyState';
import { ResultStory } from './components/dashboard/ResultStory';
import { StrategyExplanation } from './components/dashboard/StrategyExplanation';
import { runBacktestApi, checkBackendHealth } from './lib/api';

export default function App() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<any>(null);
  const [lastConfig, setLastConfig] = useState<any>(null);
  const [hasRun, setHasRun] = useState(false);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  // Periodic backend health check — detect offline state before the user clicks
  useEffect(() => {
    let mounted = true;
    const check = async () => {
      const alive = await checkBackendHealth();
      if (mounted) setBackendOnline(alive);
    };
    check();
    const interval = setInterval(check, 15000); // every 15s
    return () => { mounted = false; clearInterval(interval); };
  }, []);

  const runBacktest = async (config: any) => {
    setLoading(true);
    setError(null);
    setLastConfig(config);
    setHasRun(true);

    const { data: result, error: apiError } = await runBacktestApi(config);

    if (apiError) {
      setError(apiError);
      setData(null);
      if (apiError.type === 'backend_offline') setBackendOnline(false);
    } else {
      setData(result);
      setBackendOnline(true);
    }

    setLoading(false);
  };

  const handleRunExample = () => {
    runBacktest({
      ticker: 'AAPL',
      start_date: '2023-01-01',
      end_date: '2023-12-31',
      strategy: 'ma_crossover',
      fast_window: 20,
      slow_window: 50,
      initial_cash: 100000,
      commission_rate: 0.001,
      slippage_bps: 5.0
    });
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <TopNav backendOnline={backendOnline} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar onRun={runBacktest} />
        <main className="flex-1 overflow-y-auto p-8 lg:p-10 no-scrollbar">
          <div className="max-w-[1400px] mx-auto">
            
            {!hasRun && !error && (
              <EmptyState onRunExample={handleRunExample} />
            )}

            {error && (
              <ErrorState 
                errorType={error.type}
                errorMessage={error.message}
                troubleshooting={error.troubleshooting}
                onRetry={() => runBacktest(lastConfig)}
              />
            )}
            
            {hasRun && !error && data && (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
                <HeroHeader ticker={lastConfig?.ticker || 'AAPL'} />
                
                <ResultStory metrics={data.metrics} settings={data.settings} />
                
                {/* KPI Grid Row */}
                <KPIGrid metrics={data.metrics} equityCurve={data.equity_curve} />
                
                {/* Chart and History Row */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
                  {/* Large Chart takes up 2/3 width */}
                  <div className="lg:col-span-2">
                    <ChartSection data={data.equity_curve} priceData={data.price_data} />
                  </div>
                  
                  {/* Trade History takes up 1/3 width */}
                  <div className="lg:col-span-1">
                    <TradeHistory trades={data.trades} />
                  </div>
                </div>

                {/* Strategy Explanation Row */}
                <StrategyExplanation strategy={lastConfig?.strategy} />
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
