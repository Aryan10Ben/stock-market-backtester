import { Metrics, EquityPoint } from "../lib/types";
import { TrendingUp, Activity, Percent, ArrowDownRight, Scale } from "lucide-react";

export default function SummaryCards({
  metrics,
  equityCurve,
}: {
  metrics: Metrics;
  equityCurve: EquityPoint[];
}) {
  if (!metrics) return null;

  const openQty =
    equityCurve && equityCurve.length > 0
      ? (equityCurve[equityCurve.length - 1] as EquityPoint).portfolioQty || 0
      : 0;

  const cards = [
    {
      title: "Total Return",
      value: `${(metrics.totalReturn! * 100).toFixed(2)}%`,
      sub: `${(metrics.excessReturn! * 100).toFixed(2)}% vs B&H`,
      icon: TrendingUp,
      color: metrics.totalReturn! >= 0 ? "text-emerald-500" : "text-red-500",
    },
    {
      title: "CAGR",
      value: `${(metrics.cagr! * 100).toFixed(2)}%`,
      icon: Activity,
      color: "text-blue-500",
    },
    {
      title: "Sharpe Ratio",
      value: metrics.sharpeRatio!.toFixed(2),
      icon: Scale,
      color: "text-purple-500",
    },
    {
      title: "Max Drawdown",
      value: `${(metrics.maxDrawdown! * 100).toFixed(2)}%`,
      icon: ArrowDownRight,
      color: "text-red-500",
    },
    {
      title: "Win Rate",
      value: `${(metrics.winRate! * 100).toFixed(1)}%`,
      sub: `${metrics.numTrades} Trades`,
      icon: Percent,
      color: "text-amber-500",
    },
  ];

  return (
    <div className="space-y-4">
      {openQty > 0 && (
        <div className="bg-blue-900/20 border border-blue-800 text-blue-200 px-4 py-3 rounded-lg text-sm flex items-center gap-2">
          <TrendingUp className="h-4 w-4" />
          <strong>1 Open Position:</strong> Strategy holds {openQty} shares at the end of the
          backtest window.
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {cards.map((c, i) => (
          <div
            key={i}
            className="bg-card border border-gray-800 rounded-xl p-4 shadow-sm hover:border-gray-700 transition-colors"
          >
            <div className="text-xs uppercase tracking-wider text-gray-400 font-medium mb-2">
              {c.title}
            </div>
            <div className={`text-2xl font-bold ${c.color}`}>{c.value}</div>
            {c.sub && <div className="text-xs text-gray-500 mt-1">{c.sub}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}
