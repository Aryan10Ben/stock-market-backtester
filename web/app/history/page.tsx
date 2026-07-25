"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, History as HistoryIcon, Activity } from "lucide-react";
import { getHistory } from "../../lib/api-client";
import { RunHistory } from "../../lib/types";

export default function HistoryPage() {
  const [runs, setRuns] = useState<RunHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchRuns() {
      try {
        const data = await getHistory();
        setRuns(data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : String(err);
        setError(errorMessage || "Failed to fetch history");
      } finally {
        setLoading(false);
      }
    }
    fetchRuns();
  }, []);

  return (
    <div className="min-h-screen bg-[#0e1117] text-gray-100 font-sans p-6 lg:p-10">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="flex items-center justify-between border-b border-gray-800 pb-6">
          <div className="flex items-center gap-3">
            <div className="bg-gray-800 p-2 rounded-lg">
              <HistoryIcon className="h-6 w-6 text-gray-300" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Run History</h1>
              <p className="text-sm text-gray-500">Recent backtest executions</p>
            </div>
          </div>

          <Link
            href="/"
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Link>
        </div>

        {error && (
          <div className="bg-red-900/20 border border-red-800 text-red-200 p-6 rounded-xl">
            <h3 className="text-lg font-medium flex items-center gap-2 mb-2">
              ⚠️ Could not load history
            </h3>
            <p>{error}</p>
          </div>
        )}

        {loading ? (
          <div className="flex flex-col items-center justify-center py-32 space-y-4">
            <div className="h-10 w-10 border-4 border-gray-600/30 border-t-gray-500 rounded-full animate-spin" />
            <p className="text-gray-400 font-medium animate-pulse">Loading history...</p>
          </div>
        ) : runs.length === 0 && !error ? (
          <div className="flex flex-col items-center justify-center py-20 text-center border border-dashed border-gray-800 rounded-2xl bg-gray-900/20">
            <Activity className="h-12 w-12 text-gray-600 mb-4" />
            <h2 className="text-xl font-medium text-gray-300">No Runs Found</h2>
            <p className="text-gray-500 max-w-sm mt-2">
              You haven&apos;t executed any backtests yet, or the database connection is not
              configured.
            </p>
          </div>
        ) : (
          <div className="bg-card border border-gray-800 rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-gray-400 uppercase bg-gray-900">
                  <tr>
                    <th className="px-6 py-4">Date Run</th>
                    <th className="px-6 py-4">Ticker</th>
                    <th className="px-6 py-4">Period</th>
                    <th className="px-6 py-4 text-right">Return</th>
                    <th className="px-6 py-4 text-right">Sharpe</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {runs.map((r, i) => (
                    <tr key={i} className="hover:bg-gray-800/50 transition-colors">
                      <td className="px-6 py-4 text-gray-400">
                        {new Date(r.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 font-bold tracking-wider">{r.ticker}</td>
                      <td className="px-6 py-4 text-gray-400">
                        {r.start_date.split("T")[0]} to {r.end_date.split("T")[0]}
                      </td>
                      <td
                        className={`px-6 py-4 text-right font-bold ${r.metrics?.totalReturn && r.metrics.totalReturn >= 0 ? "text-emerald-500" : "text-red-500"}`}
                      >
                        {r.metrics?.totalReturn !== undefined
                          ? `${(r.metrics.totalReturn * 100).toFixed(2)}%`
                          : "-"}
                      </td>
                      <td className="px-6 py-4 text-right font-mono text-gray-300">
                        {r.metrics?.sharpeRatio !== undefined
                          ? r.metrics.sharpeRatio.toFixed(2)
                          : "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
