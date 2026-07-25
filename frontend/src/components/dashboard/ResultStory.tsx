import { motion } from "framer-motion";

export function ResultStory({ metrics, settings }: { metrics: any, settings: any }) {
  if (!metrics || !settings) return null;

  const isProfit = metrics.total_return > 0;
  const isOutperforming = metrics.excess_return > 0;
  
  const profitText = isProfit ? "generated a profit" : "incurred a loss";
  const profitColor = isProfit ? "text-primary" : "text-negative";
  
  const performText = isOutperforming ? "outperformed" : "underperformed";
  const performColor = isOutperforming ? "text-primary" : "text-negative";

  const drawdownClass = metrics.max_drawdown > 0.15 ? "text-negative" : "text-primary";
  const drawdownDesc = metrics.max_drawdown > 0.15 ? "indicating significant downside risk" : "indicating relatively low downside risk";

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 bg-card border border-border rounded-xl mt-8 mb-6 shadow-sm"
    >
      <h3 className="text-sm uppercase tracking-wider text-muted font-bold mb-4">Performance Summary</h3>
      <p className="text-lg leading-relaxed text-foreground">
        Your <strong className="text-foreground">Moving Average Crossover</strong> strategy on <strong className="text-foreground">{settings.ticker}</strong> {profitText} of <strong className={profitColor}>${(metrics.final_value - metrics.initial_cash).toLocaleString(undefined, { maximumFractionDigits: 0 })}</strong> over the selected period.
        <br/><br/>
        This strategy <strong className={performColor}>{performText}</strong> a simple Buy & Hold approach by <strong>{Math.abs(metrics.excess_return * 100).toFixed(2)}%</strong>. 
        The maximum drawdown reached <strong className={drawdownClass}>{(metrics.max_drawdown * 100).toFixed(2)}%</strong>, {drawdownDesc}. 
        Overall, the strategy executed <strong>{metrics.num_trades} trades</strong> with a win rate of <strong>{(metrics.win_rate * 100).toFixed(1)}%</strong>.
      </p>
    </motion.div>
  );
}
