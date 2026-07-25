import { TrendingUp, TrendingDown, Activity, Clock, Percent, AlertTriangle, Target, Hash } from "lucide-react";
import { Card, CardContent } from "../ui/Card";
import { ResponsiveContainer, LineChart, Line } from "recharts";

interface MetricProps {
  title: string;
  value: string;
  icon: React.ReactNode;
  trend?: { value: number; label: string };
  sparklineData?: any[];
  positiveColor?: boolean;
}

function MetricCard({ title, value, icon, trend, sparklineData, positiveColor = true }: MetricProps) {
  const isPositive = trend ? trend.value >= 0 : true;
  const trendColor = isPositive === positiveColor ? "text-primary" : "text-negative";
  
  return (
    <Card className="overflow-hidden group">
      <CardContent className="p-5 flex flex-col relative h-full">
        <div className="flex justify-between items-start mb-4">
          <p className="text-sm font-medium text-muted uppercase tracking-wider">{title}</p>
          <div className="p-2 bg-background rounded-md text-neutral group-hover:text-foreground transition-colors">
            {icon}
          </div>
        </div>
        
        <div className="flex items-baseline gap-2 mb-2">
          <h2 className="text-2xl font-bold tracking-tight text-foreground">{value}</h2>
        </div>
        
        <div className="mt-auto flex justify-between items-end">
          {trend ? (
            <div className={`flex items-center text-xs font-semibold ${trendColor}`}>
              {trend.value >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
              {Math.abs(trend.value).toFixed(2)}% <span className="text-muted ml-1 font-normal">{trend.label}</span>
            </div>
          ) : (
            <div className="h-4"></div>
          )}
          
          {sparklineData && (
            <div className="h-8 w-16 opacity-50 group-hover:opacity-100 transition-opacity">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={sparklineData}>
                  <Line 
                    type="monotone" 
                    dataKey="val" 
                    stroke={isPositive === positiveColor ? "#10b981" : "#ef4444"} 
                    strokeWidth={2} 
                    dot={false} 
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function KPIGrid({ metrics, equityCurve }: { metrics: any; equityCurve: any[] }) {
  if (!metrics) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 py-6">
        {[1, 2, 3, 4].map(i => (
          <Card key={i} className="animate-pulse">
            <CardContent className="h-32 p-5 bg-card/50"></CardContent>
          </Card>
        ))}
      </div>
    );
  }

  // Generate a mock sparkline from equity curve for the visual effect
  const sparkline = equityCurve ? equityCurve.filter((_, i) => i % Math.ceil(equityCurve.length / 20) === 0).map(p => ({ val: p.total_value })) : [];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 py-6">
      <MetricCard 
        title="Total Return" 
        value={`${(metrics.total_return * 100).toFixed(2)}%`}
        icon={<Activity className="h-5 w-5" />}
        trend={{ value: metrics.excess_return * 100, label: "vs Benchmark" }}
        sparklineData={sparkline}
      />
      <MetricCard 
        title="Annualized Return (CAGR)" 
        value={`${(metrics.cagr * 100).toFixed(2)}%`}
        icon={<Percent className="h-5 w-5" />}
        trend={{ value: metrics.cagr * 100, label: "per year" }}
      />
      <MetricCard 
        title="Sharpe Ratio" 
        value={metrics.sharpe_ratio.toFixed(2)}
        icon={<Target className="h-5 w-5" />}
        trend={metrics.sharpe_ratio > 1 ? { value: 1.5, label: "Good" } : { value: -0.5, label: "Sub-optimal" }}
      />
      <MetricCard 
        title="Max Drawdown" 
        value={`${(metrics.max_drawdown * 100).toFixed(2)}%`}
        icon={<AlertTriangle className="h-5 w-5" />}
        positiveColor={false}
        trend={{ value: metrics.max_drawdown * 100, label: "Peak to Trough" }}
      />
      <MetricCard 
        title="Win Rate" 
        value={`${(metrics.win_rate * 100).toFixed(1)}%`}
        icon={<Hash className="h-5 w-5" />}
      />
      <MetricCard 
        title="Total Trades" 
        value={metrics.num_trades.toString()}
        icon={<Clock className="h-5 w-5" />}
      />
      <MetricCard 
        title="Winning Trades" 
        value={metrics.num_winning_trades.toString()}
        icon={<TrendingUp className="h-5 w-5" />}
      />
      <MetricCard 
        title="Losing Trades" 
        value={metrics.num_losing_trades.toString()}
        icon={<TrendingDown className="h-5 w-5" />}
        positiveColor={false}
      />
    </div>
  );
}
