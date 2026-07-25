import { Search, Moon, Activity } from "lucide-react";
import { Button } from "../ui/Button";

interface TopNavProps {
  backendOnline?: boolean | null;
}

export function TopNav({ backendOnline }: TopNavProps) {
  const statusDot =
    backendOnline === null
      ? "bg-yellow-500 animate-pulse" // checking
      : backendOnline
        ? "bg-emerald-500"            // connected
        : "bg-red-500 animate-pulse"; // offline

  const statusLabel =
    backendOnline === null
      ? "Connecting…"
      : backendOnline
        ? "Engine Online"
        : "Engine Offline";

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-md">
      <div className="flex h-16 items-center px-6">
        <div className="flex items-center gap-2 font-bold text-xl tracking-tight mr-8">
          <Activity className="h-6 w-6 text-primary" />
          <span>Backtester</span>
        </div>
        
        <div className="flex-1 max-w-xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
            <input 
              type="text" 
              placeholder="Search ticker (e.g. AAPL, TSLA)..." 
              className="w-full h-10 pl-10 pr-4 bg-card border border-border rounded-lg text-sm focus:outline-none focus:border-primary transition-colors"
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 hidden sm:flex gap-1">
              <kbd className="px-1.5 py-0.5 text-[10px] font-medium bg-background border border-border rounded text-muted">⌘</kbd>
              <kbd className="px-1.5 py-0.5 text-[10px] font-medium bg-background border border-border rounded text-muted">K</kbd>
            </div>
          </div>
        </div>

        <div className="ml-auto flex items-center gap-4">
          {/* Connection status indicator */}
          <div className="flex items-center gap-2 text-xs text-muted">
            <div className={`h-2 w-2 rounded-full ${statusDot}`} />
            <span className="hidden sm:inline">{statusLabel}</span>
          </div>

          <Button variant="ghost" size="sm" className="h-9 w-9 p-0 rounded-full text-muted hover:text-foreground">
            <Moon className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </nav>
  );
}
