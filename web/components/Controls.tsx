import { useState } from "react";
import { BacktestRequest } from "../lib/types";
import { Play } from "lucide-react";

interface ControlsProps {
  onRun: (req: BacktestRequest) => void;
  isLoading: boolean;
}

export default function Controls({ onRun, isLoading }: ControlsProps) {
  const [tickerMode, setTickerMode] = useState<"sample" | "custom">("sample");
  const [ticker, setTicker] = useState("AAPL");
  const [startDate, setStartDate] = useState("2023-01-01");
  const [endDate, setEndDate] = useState("2023-12-31");
  const [fastWindow, setFastWindow] = useState(20);
  const [slowWindow, setSlowWindow] = useState(50);
  const [initialCash, setInitialCash] = useState(100000);
  const [commissionPct, setCommissionPct] = useState(0.1);
  const [slippageBps, setSlippageBps] = useState(5.0);

  const isValid = ticker.trim() !== "" && fastWindow < slowWindow && startDate < endDate;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) return;

    onRun({
      ticker: ticker.trim().toUpperCase(),
      startDate,
      endDate,
      strategy: { fastWindow, slowWindow },
      initialCash,
      commissionPct,
      slippageBps,
    });
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="w-64 shrink-0 border-r border-gray-800 bg-gray-900/50 p-6 flex flex-col gap-6 h-full overflow-y-auto custom-scrollbar"
    >
      <div>
        <h2 className="text-lg font-semibold text-gray-100 flex items-center gap-2 mb-4">
          ⚙️ Configuration
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Data Source</label>
            <div className="flex bg-gray-800 rounded-lg p-1 mb-3">
              <button
                type="button"
                className={`flex-1 text-xs py-1.5 rounded-md ${tickerMode === "sample" ? "bg-gray-700 text-white" : "text-gray-400 hover:text-gray-200"}`}
                onClick={() => setTickerMode("sample")}
              >
                Sample
              </button>
              <button
                type="button"
                className={`flex-1 text-xs py-1.5 rounded-md ${tickerMode === "custom" ? "bg-gray-700 text-white" : "text-gray-400 hover:text-gray-200"}`}
                onClick={() => setTickerMode("custom")}
              >
                Custom
              </button>
            </div>

            {tickerMode === "sample" ? (
              <select
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                className="w-full bg-black border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
              >
                <option value="AAPL">AAPL</option>
                <option value="MSFT">MSFT</option>
                <option value="NVDA">NVDA</option>
                <option value="TSLA">TSLA</option>
                <option value="SPY">SPY</option>
              </select>
            ) : (
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                placeholder="e.g. META"
                className="w-full bg-black border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none uppercase"
              />
            )}
          </div>

          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-400">Date Range</label>
            <div>
              <div className="text-xs text-gray-500 mb-1">Start</div>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full bg-black border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
              />
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">End</div>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full bg-black border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
              />
            </div>
          </div>

          <div className="space-y-3 pt-4 border-t border-gray-800">
            <label className="block text-sm font-medium text-gray-400">MA Crossover</label>
            <div className="flex gap-3">
              <div className="flex-1">
                <div className="text-xs text-gray-500 mb-1">Fast</div>
                <input
                  type="number"
                  value={fastWindow}
                  onChange={(e) => setFastWindow(Number(e.target.value))}
                  className="w-full bg-black border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
                />
              </div>
              <div className="flex-1">
                <div className="text-xs text-gray-500 mb-1">Slow</div>
                <input
                  type="number"
                  value={slowWindow}
                  onChange={(e) => setSlowWindow(Number(e.target.value))}
                  className="w-full bg-black border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
                />
              </div>
            </div>
          </div>

          <div className="space-y-3 pt-4 border-t border-gray-800">
            <label className="block text-sm font-medium text-gray-400">Capital & Fees</label>
            <div>
              <div className="text-xs text-gray-500 mb-1">Initial Cash ($)</div>
              <input
                type="number"
                value={initialCash}
                onChange={(e) => setInitialCash(Number(e.target.value))}
                step="5000"
                className="w-full bg-black border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
              />
            </div>
            <div className="flex gap-3">
              <div className="flex-1">
                <div className="text-xs text-gray-500 mb-1">Comm (%)</div>
                <input
                  type="number"
                  value={commissionPct}
                  onChange={(e) => setCommissionPct(Number(e.target.value))}
                  step="0.05"
                  className="w-full bg-black border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
                />
              </div>
              <div className="flex-1">
                <div className="text-xs text-gray-500 mb-1">Slip (bps)</div>
                <input
                  type="number"
                  value={slippageBps}
                  onChange={(e) => setSlippageBps(Number(e.target.value))}
                  step="1"
                  className="w-full bg-black border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:border-blue-500 outline-none"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-auto pt-6">
        <button
          type="submit"
          disabled={!isValid || isLoading}
          className={`w-full flex items-center justify-center gap-2 py-3 rounded-lg font-medium transition-colors ${
            !isValid || isLoading
              ? "bg-gray-800 text-gray-500 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-500 text-white"
          }`}
        >
          {isLoading ? (
            <div className="h-5 w-5 rounded-full border-2 border-white/20 border-t-white animate-spin" />
          ) : (
            <>
              <Play className="h-4 w-4" />
              Run Backtest
            </>
          )}
        </button>
      </div>
    </form>
  );
}
