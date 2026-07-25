import { AlertCircle, RefreshCw, Upload, FileText, WifiOff, Server, Terminal } from "lucide-react";
import { Card, CardContent } from "../ui/Card";
import { Button } from "../ui/Button";

interface ErrorStateProps {
  errorType: string;
  errorMessage: string;
  troubleshooting: string;
  onRetry: () => void;
}

export function ErrorState({ errorType, errorMessage, troubleshooting, onRetry }: ErrorStateProps) {
  const isBackendOffline = errorType === "backend_offline";

  // Map error types to human-friendly titles and icons
  const titleMap: Record<string, string> = {
    backend_offline: "Engine Offline",
    data_error: "Invalid Data",
    network_error: "Network Error",
    input_error: "Invalid Parameters",
    engine_error: "Simulation Error",
    system_error: "System Error",
    timeout: "Request Timed Out",
    unknown_error: "Unknown Error",
  };

  const title = titleMap[errorType] || "Backtest Failed";

  if (isBackendOffline) {
    return (
      <Card className="col-span-full border-amber-500/20 bg-amber-500/5">
        <CardContent className="p-8">
          <div className="flex flex-col items-center text-center max-w-xl mx-auto space-y-6">
            <div className="h-16 w-16 bg-amber-500/10 text-amber-500 rounded-full flex items-center justify-center">
              <WifiOff className="h-8 w-8" />
            </div>
            
            <div>
              <h2 className="text-2xl font-bold text-foreground mb-2">{title}</h2>
              <p className="text-muted text-base">{errorMessage}</p>
            </div>

            <div className="w-full bg-card border border-border rounded-lg p-5 text-left space-y-4">
              <h3 className="font-semibold text-sm uppercase tracking-wider text-muted flex items-center gap-2">
                <Terminal className="h-4 w-4" /> How to Fix
              </h3>
              <p className="text-sm">
                The backend analysis engine is not running. Open a terminal in your project directory and run:
              </p>
              <div className="bg-background rounded-md p-3 font-mono text-xs text-emerald-400 border border-border">
                PYTHONPATH=src uvicorn api.main:app --reload --port 8000
              </div>
              <p className="text-xs text-muted">
                The status indicator in the top bar will turn green once the engine is connected.
              </p>
            </div>

            <div className="flex gap-4 w-full pt-4">
              <Button onClick={onRetry} className="flex-1 gap-2" variant="default">
                <RefreshCw className="h-4 w-4" /> Retry Connection
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="col-span-full border-negative/20 bg-negative/5">
      <CardContent className="p-8">
        <div className="flex flex-col items-center text-center max-w-xl mx-auto space-y-6">
          <div className="h-16 w-16 bg-negative/10 text-negative rounded-full flex items-center justify-center">
            <AlertCircle className="h-8 w-8" />
          </div>
          
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-2">{title}</h2>
            <p className="text-muted text-base">{errorMessage}</p>
          </div>

          <div className="w-full bg-card border border-border rounded-lg p-5 text-left">
            <h3 className="font-semibold text-sm uppercase tracking-wider text-muted mb-3 flex items-center gap-2">
              <FileText className="h-4 w-4" /> Troubleshooting
            </h3>
            <p className="text-sm whitespace-pre-wrap">{troubleshooting}</p>
          </div>

          <div className="flex gap-4 w-full pt-4">
            <Button onClick={onRetry} className="flex-1 gap-2" variant="default">
              <RefreshCw className="h-4 w-4" /> Retry Backtest
            </Button>
            <Button className="flex-1 gap-2" variant="outline">
              <Upload className="h-4 w-4" /> Upload Custom CSV
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
