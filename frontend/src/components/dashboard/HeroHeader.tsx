import { ArrowUpRight, ArrowDownRight } from "lucide-react";

interface HeroHeaderProps {
  ticker: string;
}

export function HeroHeader({ ticker }: HeroHeaderProps) {
  // Mocking live data for demonstration
  const price = 152.34;
  const change = 2.14;
  const pctChange = 1.42;
  const isPositive = change >= 0;

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-border">
      <div>
        <div className="flex items-center gap-3 mb-1">
          <h1 className="text-4xl font-bold tracking-tight uppercase">{ticker}</h1>
          <span className="px-2 py-0.5 rounded text-xs font-semibold bg-card border border-border text-muted">
            NASDAQ
          </span>
          <span className="flex items-center gap-1.5 text-xs text-primary bg-primary/10 px-2 py-0.5 rounded-full font-medium">
            <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse"></span>
            LIVE
          </span>
        </div>
        <div className="flex items-baseline gap-3">
          <span className="text-2xl font-bold text-foreground">${price.toFixed(2)}</span>
          <span className={`flex items-center text-sm font-semibold ${isPositive ? 'text-primary' : 'text-negative'}`}>
            {isPositive ? <ArrowUpRight className="h-4 w-4 mr-0.5" /> : <ArrowDownRight className="h-4 w-4 mr-0.5" />}
            {isPositive ? '+' : ''}{change.toFixed(2)} ({pctChange.toFixed(2)}%)
          </span>
          <span className="text-xs text-muted ml-2">Today</span>
        </div>
      </div>
    </div>
  );
}
