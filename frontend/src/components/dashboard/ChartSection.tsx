import { useState } from "react";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, ComposedChart, Line, Bar } from "recharts";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import { Maximize2, Download } from "lucide-react";
import { Button } from "../ui/Button";

export function ChartSection({ data, priceData }: { data: any[]; priceData: any[] }) {
  const [activeTab, setActiveTab] = useState<"equity" | "price">("equity");

  if (!data || data.length === 0) {
    return (
      <Card className="col-span-full h-[500px] flex items-center justify-center">
        <div className="flex flex-col items-center text-muted">
          <div className="h-10 w-10 border-2 border-muted border-t-primary rounded-full animate-spin mb-4" />
          <p>Loading chart data...</p>
        </div>
      </Card>
    );
  }

  // Format data for Recharts
  const equityData = data.map(d => ({
    date: d.date,
    Portfolio: d.total_value,
    Benchmark: d.benchmark_value,
  }));

  const priceChartData = priceData.map(d => ({
    date: d.time,
    Price: d.close,
    Volume: d.volume,
    Signal: d.signal,
    ...(d.indicators || {})
  }));

  const indicatorKeys = priceData.length > 0 && priceData[0].indicators ? Object.keys(priceData[0].indicators) : [];
  const colors = ['#10b981', '#ef4444', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899'];

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card border border-border p-3 rounded-lg shadow-lg text-sm z-50 relative">
          <p className="font-semibold mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
              <span className="text-muted">{entry.name}:</span>
              <span className="font-mono font-medium">${Number(entry.value).toFixed(2)}</span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="col-span-full">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="flex gap-4">
          <button 
            onClick={() => setActiveTab("equity")}
            className={`text-sm font-semibold pb-2 border-b-2 transition-colors ${activeTab === 'equity' ? 'border-primary text-foreground' : 'border-transparent text-muted hover:text-foreground'}`}
          >
            Portfolio Equity
          </button>
          <button 
            onClick={() => setActiveTab("price")}
            className={`text-sm font-semibold pb-2 border-b-2 transition-colors ${activeTab === 'price' ? 'border-primary text-foreground' : 'border-transparent text-muted hover:text-foreground'}`}
          >
            Price & Signals
          </button>
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><Download className="h-4 w-4" /></Button>
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><Maximize2 className="h-4 w-4" /></Button>
        </div>
      </CardHeader>
      <CardContent className="pt-4 h-[450px]">
        <ResponsiveContainer width="100%" height="100%">
          {activeTab === "equity" ? (
            <AreaChart data={equityData} margin={{ top: 10, right: 0, left: 20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorPortfolio" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="date" stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} minTickGap={30} />
              <YAxis domain={['auto', 'auto']} stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `$${(val/1000).toFixed(0)}k`} />
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#27272a" />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="Portfolio" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorPortfolio)" />
              <Area type="monotone" dataKey="Benchmark" stroke="#6b7280" strokeDasharray="5 5" fill="none" strokeWidth={2} />
            </AreaChart>
          ) : (
            <ComposedChart data={priceChartData} margin={{ top: 10, right: 0, left: 20, bottom: 0 }}>
              <XAxis dataKey="date" stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} minTickGap={30} />
              <YAxis yAxisId="left" domain={['auto', 'auto']} stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `$${val.toFixed(0)}`} />
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#27272a" />
              <Tooltip content={<CustomTooltip />} />
              <Line yAxisId="left" type="monotone" dataKey="Price" stroke="#f8f9fa" strokeWidth={2} dot={false} />
              {indicatorKeys.map((key, i) => (
                <Line key={key} yAxisId="left" type="monotone" dataKey={key} stroke={colors[i % colors.length]} strokeWidth={1} dot={false} />
              ))}
            </ComposedChart>
          )}
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
