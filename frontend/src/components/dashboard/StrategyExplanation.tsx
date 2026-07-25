import { Info, ThumbsUp, AlertTriangle, BarChart3 } from "lucide-react";
import { motion } from "framer-motion";

export function StrategyExplanation({ strategy = "ma_crossover" }: { strategy?: string }) {
  if (strategy !== "ma_crossover") return null;

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12 pt-12 border-t border-border"
    >
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Info className="h-5 w-5 text-accent" />
          <h3 className="text-lg font-bold">How the Strategy Works</h3>
        </div>
        <p className="text-muted leading-relaxed mb-6 text-sm">
          A Moving Average Crossover strategy relies on two distinct lines: a Fast Moving Average (shorter lookback period) and a Slow Moving Average (longer lookback period). 
          A "Buy" signal is generated when the fast line crosses above the slow line, indicating upward momentum. A "Sell" signal is generated when the fast line crosses below the slow line.
        </p>
        
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="h-5 w-5 text-accent" />
          <h3 className="text-lg font-bold">Suitable Markets</h3>
        </div>
        <p className="text-muted leading-relaxed text-sm">
          This strategy performs best in strongly trending markets. It is designed to capture large, sustained directional moves in the asset's price.
        </p>
      </div>

      <div className="space-y-6">
        <div className="bg-primary/5 border border-primary/20 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-2">
            <ThumbsUp className="h-5 w-5 text-primary" />
            <h4 className="font-bold text-primary">Strengths</h4>
          </div>
          <ul className="list-disc list-inside text-sm text-muted space-y-1">
            <li>Excellent at capturing long-term macro trends.</li>
            <li>Objective and rules-based, removing emotional trading.</li>
            <li>Limits downside during prolonged bear markets.</li>
          </ul>
        </div>

        <div className="bg-negative/5 border border-negative/20 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-5 w-5 text-negative" />
            <h4 className="font-bold text-negative">Weaknesses</h4>
          </div>
          <ul className="list-disc list-inside text-sm text-muted space-y-1">
            <li>Susceptible to "whipsawing" in sideways/ranging markets.</li>
            <li>Lagging indicator; enters and exits trades slightly late.</li>
            <li>Can generate many small losses while waiting for a big trend.</li>
          </ul>
        </div>
      </div>
    </motion.div>
  );
}
