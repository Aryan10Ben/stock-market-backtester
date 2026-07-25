import { Trade } from "../lib/types";

export default function TradesTable({ trades }: { trades: Trade[] }) {
  if (!trades || trades.length === 0) {
    return (
      <div className="w-full bg-card rounded-xl border border-gray-800 p-8 text-center text-gray-500">
        No trades executed during this backtest.
      </div>
    );
  }

  return (
    <div className="w-full bg-card rounded-xl border border-gray-800 overflow-hidden">
      <div className="p-4 border-b border-gray-800">
        <h3 className="text-lg font-medium text-gray-100">Trade History</h3>
      </div>
      <div className="overflow-x-auto max-h-[400px]">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-gray-400 uppercase bg-gray-900 sticky top-0">
            <tr>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Side</th>
              <th className="px-4 py-3 text-right">Price</th>
              <th className="px-4 py-3 text-right">Total Cost</th>
              <th className="px-4 py-3 text-right">Balance</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {trades.map((t, i) => (
              <tr key={i} className="hover:bg-gray-800/50 transition-colors">
                <td className="px-4 py-3 font-mono text-gray-300">{t.date.split("T")[0]}</td>
                <td
                  className="px-4 py-3 font-bold"
                  style={{ color: t.action === "BUY" ? "#10b981" : "#ef4444" }}
                >
                  {t.action}
                </td>
                <td className="px-4 py-3 font-mono text-right text-gray-300">
                  ${t.price.toFixed(2)}
                </td>
                <td className="px-4 py-3 font-mono text-right text-gray-300">
                  ${t.cost.toFixed(2)}
                </td>
                <td className="px-4 py-3 font-mono text-right text-gray-300">
                  ${t.balanceAfter.toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
