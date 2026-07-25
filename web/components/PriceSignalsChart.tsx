"use client";

import Plot from "./PlotlyWrapper";
import { BacktestResponse } from "../lib/types";

const COLORS = {
  background: "#0e1117",
  card: "#1a1c24",
  text_primary: "#f8f9fa",
  text_secondary: "#a0a5b1",
  success: "#10b981",
  danger: "#ef4444",
  warning: "#f59e0b",
  primary: "#3b82f6",
  buy: "#10b981",
  sell: "#ef4444",
};

export default function PriceSignalsChart({ data }: { data: BacktestResponse }) {
  if (!data.priceData || data.priceData.length === 0) return null;

  const df = data.priceData;
  const dates = df.map((d) => d.Date);

  const traces = [
    {
      x: dates,
      open: df.map((d) => d.Open),
      high: df.map((d) => d.High),
      low: df.map((d) => d.Low),
      close: df.map((d) => d.Close),
      type: "candlestick",
      name: "Price",
      increasing: { line: { color: COLORS.success } },
      decreasing: { line: { color: COLORS.danger } },
    },
  ];

  // Indicator overlays
  const baseCols = new Set(["Date", "Open", "High", "Low", "Close", "Volume", "index"]);
  const indicatorColors = [COLORS.warning, COLORS.primary, "#8b5cf6", "#ec4899", "#06b6d4"];
  const allKeys = Object.keys(df[0] || {});
  const indicatorCols = allKeys.filter((k) => !baseCols.has(k));

  indicatorCols.forEach((col, i) => {
    traces.push({
      x: dates,
      y: df.map((d) => d[col]),
      type: "scatter",
      mode: "lines",
      name: col,
      line: { color: indicatorColors[i % indicatorColors.length], width: 1.5 },
    });
  });

  // Buy/Sell Signals
  const buys = data.signals.filter((s) => s.action === "BUY");
  const sells = data.signals.filter((s) => s.action === "SELL");

  if (buys.length > 0) {
    traces.push({
      x: buys.map((b) => b.date),
      y: buys.map((b) => b.price),
      type: "scatter",
      mode: "markers",
      marker: { symbol: "triangle-up", size: 12, color: COLORS.buy },
      name: "BUY",
    });
  }

  if (sells.length > 0) {
    traces.push({
      x: sells.map((s) => s.date),
      y: sells.map((s) => s.price),
      type: "scatter",
      mode: "markers",
      marker: { symbol: "triangle-down", size: 12, color: COLORS.sell },
      name: "SELL",
    });
  }

  return (
    <div className="w-full bg-card rounded-xl border border-gray-800 p-4">
      <h3 className="text-lg font-medium text-gray-100 mb-4">Price Action & Signals</h3>
      <Plot
        data={traces}
        layout={{
          height: 500,
          margin: { l: 40, r: 40, t: 10, b: 40 },
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          font: { family: "Inter, sans-serif", color: COLORS.text_secondary },
          xaxis: { showgrid: false, zeroline: false, rangeslider: { visible: false } },
          yaxis: { showgrid: true, gridcolor: "rgba(255,255,255,0.05)", zeroline: false },
          hovermode: "x unified",
        }}
        useResizeHandler={true}
        className="w-full"
      />
    </div>
  );
}
