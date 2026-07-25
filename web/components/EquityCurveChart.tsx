"use client";

import Plot from "./PlotlyWrapper";
import { BacktestResponse } from "../lib/types";

const COLORS = {
  equity: "#3b82f6",
  benchmark: "rgba(255,255,255,0.2)",
  text_secondary: "#a0a5b1",
};

export default function EquityCurveChart({ data }: { data: BacktestResponse }) {
  if (!data.equityCurve || data.equityCurve.length === 0) return null;

  const dates = data.equityCurve.map((p) => p.date);
  const portfolio = data.equityCurve.map((p) => p.totalValue);
  const benchmark = data.equityCurve.map((p) => p.benchmarkValue);

  const traces = [
    {
      x: dates,
      y: portfolio,
      type: "scatter",
      mode: "lines",
      name: "Portfolio",
      line: { color: COLORS.equity, width: 2 },
      fill: "tozeroy",
      fillcolor: "rgba(59, 130, 246, 0.1)",
    },
    {
      x: dates,
      y: benchmark,
      type: "scatter",
      mode: "lines",
      name: "Buy & Hold",
      line: { color: COLORS.benchmark, width: 2, dash: "dash" },
    },
  ];

  return (
    <div className="w-full bg-card rounded-xl border border-gray-800 p-4">
      <h3 className="text-lg font-medium text-gray-100 mb-4">Portfolio Equity</h3>
      <Plot
        data={traces}
        layout={{
          height: 400,
          margin: { l: 40, r: 40, t: 10, b: 40 },
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          font: { family: "Inter, sans-serif", color: COLORS.text_secondary },
          xaxis: { showgrid: false, zeroline: false },
          yaxis: {
            showgrid: true,
            gridcolor: "rgba(255,255,255,0.05)",
            zeroline: false,
            tickformat: "$,.0f",
          },
          hovermode: "x unified",
        }}
        useResizeHandler={true}
        className="w-full"
      />
    </div>
  );
}
