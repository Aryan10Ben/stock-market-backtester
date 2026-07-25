"use client";

import Plot from "./PlotlyWrapper";
import { BacktestResponse } from "../lib/types";

const COLORS = {
  drawdown: "#ef4444",
  text_secondary: "#a0a5b1",
};

export default function DrawdownChart({ data }: { data: BacktestResponse }) {
  if (!data.equityCurve || data.equityCurve.length === 0) return null;

  const dates = data.equityCurve.map((p) => p.date);
  const values = data.equityCurve.map((p) => p.totalValue);

  // Calculate drawdown series
  const { drawdowns } = values.reduce(
    (acc, val) => {
      const peak = Math.max(acc.peak, val);
      const dd = peak === 0 ? 0 : (val - peak) / peak;
      acc.drawdowns.push(dd);
      acc.peak = peak;
      return acc;
    },
    { drawdowns: [] as number[], peak: 0 }
  );

  const traces = [
    {
      x: dates,
      y: drawdowns,
      type: "scatter",
      mode: "lines",
      name: "Drawdown",
      line: { color: COLORS.drawdown, width: 1 },
      fill: "tozeroy",
      fillcolor: "rgba(239, 68, 68, 0.2)",
    },
  ];

  return (
    <div className="w-full bg-card rounded-xl border border-gray-800 p-4">
      <h3 className="text-lg font-medium text-gray-100 mb-4">Drawdown Profile</h3>
      <Plot
        data={traces}
        layout={{
          height: 300,
          margin: { l: 40, r: 40, t: 10, b: 40 },
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          font: { family: "Inter, sans-serif", color: COLORS.text_secondary },
          xaxis: { showgrid: false, zeroline: false },
          yaxis: {
            showgrid: true,
            gridcolor: "rgba(255,255,255,0.05)",
            zeroline: false,
            tickformat: ".1%",
          },
          hovermode: "x unified",
        }}
        useResizeHandler={true}
        className="w-full"
      />
    </div>
  );
}
