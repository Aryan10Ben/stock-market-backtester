"use client";

import { useState } from "react";
import Link from "next/link";
import { Activity, History } from "lucide-react";
import Controls from "../components/Controls";
import SummaryCards from "../components/SummaryCards";
import PriceSignalsChart from "../components/PriceSignalsChart";
import EquityCurveChart from "../components/EquityCurveChart";
import DrawdownChart from "../components/DrawdownChart";
import TradesTable from "../components/TradesTable";
import { runBacktest } from "../lib/api-client";
import { BacktestRequest, BacktestResponse } from "../lib/types";

export default function Dashboard() {
  const [data, setData] = useState<BacktestResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async (req: BacktestRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await runBacktest(req);
      setData(res);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(errorMessage || "Failed to run backtest");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0e1117] text-gray-100 overflow-hidden font-sans">
      <Controls onRun={handleRun} isLoading={loading} />

      <main className="flex-1 overflow-y-auto custom-scrollbar p-6 lg:p-10">
        <div className="max-w-7xl mx-auto space-y-8">
          <div className="flex items-center justify-between border-b border-gray-800 pb-6">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Activity className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight">Stock Market Backtester</h1>
                <p className="text-sm text-gray-500">Professional Quantitative Research</p>
              </div>
            </div>

            <Link
              href="/history"
              className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm font-medium transition-colors border border-gray-700"
            >
              <History className="h-4 w-4" />
              Run History
            </Link>
          </div>

          {!data && !loading && !error && (
            <div className="flex flex-col items-center justify-center py-20 text-center border border-dashed border-gray-800 rounded-2xl bg-gray-900/20">
              <Activity className="h-12 w-12 text-gray-600 mb-4" />
              <h2 className="text-xl font-medium text-gray-300">Ready to Test</h2>
              <p className="text-gray-500 max-w-sm mt-2">
                Configure your strategy parameters in the sidebar and click Run Backtest to see
                results.
              </p>
            </div>
          )}

          {error && (
            <div className="bg-red-900/20 border border-red-800 text-red-200 p-6 rounded-xl">
              <h3 className="text-lg font-medium flex items-center gap-2 mb-2">
                ⚠️ Backtest Failed
              </h3>
              <p>{error}</p>
            </div>
          )}

          {loading && (
            <div className="flex flex-col items-center justify-center py-32 space-y-4">
              <div className="h-10 w-10 border-4 border-blue-600/30 border-t-blue-600 rounded-full animate-spin" />
              <p className="text-gray-400 font-medium animate-pulse">Running simulation...</p>
            </div>
          )}

          {data && !loading && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-400">
                  Data Source:{" "}
                  <span className="text-gray-300 uppercase px-2 py-1 bg-gray-800 rounded">
                    {data.dataSourceUsed}
                  </span>
                </div>
              </div>

              <SummaryCards metrics={data.metrics} equityCurve={data.equityCurve} />

              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                <div className="xl:col-span-2 space-y-6">
                  <PriceSignalsChart data={data} />
                  <EquityCurveChart data={data} />
                </div>
                <div className="space-y-6">
                  <DrawdownChart data={data} />
                  <TradesTable trades={data.trades} />
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
