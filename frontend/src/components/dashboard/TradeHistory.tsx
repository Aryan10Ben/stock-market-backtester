import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";

export function TradeHistory({ trades }: { trades: any[] }) {
  if (!trades) return null;

  return (
    <Card className="col-span-1 lg:col-span-2">
      <CardHeader>
        <CardTitle>Trade History</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-auto h-[450px] no-scrollbar">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted uppercase bg-card border-b border-border sticky top-0 z-10">
              <tr>
                <th className="px-4 py-3 font-semibold">Date</th>
                <th className="px-4 py-3 font-semibold">Action</th>
                <th className="px-4 py-3 font-semibold text-right">Price</th>
                <th className="px-4 py-3 font-semibold text-right">Qty</th>
                <th className="px-4 py-3 font-semibold text-right">Total Cost</th>
                <th className="px-4 py-3 font-semibold text-right">Balance After</th>
              </tr>
            </thead>
            <tbody>
              {trades.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-muted">
                    No trades executed in this period.
                  </td>
                </tr>
              )}
              {trades.map((trade, idx) => (
                <tr key={idx} className="border-b border-border hover:bg-card/50 transition-colors">
                  <td className="px-4 py-3 whitespace-nowrap">{trade.date}</td>
                  <td className="px-4 py-3 font-bold">
                    <span className={trade.side === "BUY" ? "text-primary" : "text-negative"}>
                      {trade.side}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-mono">${trade.price.toFixed(2)}</td>
                  <td className="px-4 py-3 text-right font-mono">{trade.quantity}</td>
                  <td className="px-4 py-3 text-right font-mono">${Math.abs(trade.total_cost).toFixed(2)}</td>
                  <td className="px-4 py-3 text-right font-mono">${trade.portfolio_value_after.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
