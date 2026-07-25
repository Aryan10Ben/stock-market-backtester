import { Play, TrendingUp, Search } from "lucide-react";
import { Button } from "../ui/Button";
import { motion } from "framer-motion";

export function EmptyState({ onRunExample }: { onRunExample: () => void }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="flex flex-col items-center justify-center min-h-[60vh] text-center max-w-2xl mx-auto px-4"
    >
      <div className="relative mb-8">
        <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full" />
        <div className="relative h-24 w-24 bg-card border border-border rounded-2xl flex items-center justify-center shadow-2xl">
          <TrendingUp className="h-10 w-10 text-primary" />
        </div>
      </div>
      
      <h1 className="text-4xl font-bold tracking-tight mb-4">
        Run your first backtest.
      </h1>
      <p className="text-muted text-lg mb-10 max-w-lg">
        Select a stock, choose a strategy, and simulate historical trading performance in seconds. No coding required.
      </p>

      <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
        <Button onClick={onRunExample} size="lg" className="w-full sm:w-auto gap-2 px-8 h-14 text-base rounded-xl font-semibold shadow-lg shadow-primary/20 hover:scale-105 transition-transform">
          <Play className="h-5 w-5 fill-current" /> Run AAPL Example
        </Button>
        <div className="text-muted text-sm hidden sm:block">or</div>
        <div className="flex items-center gap-2 text-sm text-muted bg-card border border-border px-4 py-3 rounded-xl w-full sm:w-auto">
          <Search className="h-4 w-4" /> Use the sidebar to start
        </div>
      </div>
    </motion.div>
  );
}
