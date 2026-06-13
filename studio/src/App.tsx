import { useCallback, useEffect, useRef, useState } from "react";
import {
  crucibleAvailable,
  deleteModel,
  downloadModel,
  DownloadProgress,
  getModels,
  getSystemInfo,
  ModelEntry,
  modelsDir,
  onDownloadProgress,
  recommendModel,
  ServerStatus,
  serverStatus,
  startServer,
  stopServer,
  SystemInfo,
} from "./lib/api";
import { ModelCatalog } from "./components/ModelCatalog";
import { ServerControl } from "./components/ServerControl";
import { SystemPanel } from "./components/SystemPanel";
import { Badge } from "./components/ui/Badge";

const Flame = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
    <path d="M12 2c1 3 4 4.5 4 8a4 4 0 0 1-8 0c0-1 .2-1.8.5-2.5C6 9 5 11 5 13.5A7 7 0 0 0 19 14c0-4.5-4-6.5-7-12z" />
  </svg>
);

export default function App() {
  const [sys, setSys] = useState<SystemInfo | null>(null);
  const [models, setModels] = useState<ModelEntry[]>([]);
  const [recommended, setRecommended] = useState<string | null>(null);
  const [crucibleOk, setCrucibleOk] = useState(true);
  const [status, setStatus] = useState<ServerStatus | null>(null);
  const [dir, setDir] = useState("");
  const [progress, setProgress] = useState<Record<string, DownloadProgress>>({});
  const [busy, setBusy] = useState<Record<string, boolean>>({});
  const [runningId, setRunningId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refreshModels = useCallback(() => {
    getModels().then(setModels).catch((e) => setError(String(e)));
  }, []);

  const refreshStatus = useCallback(() => {
    serverStatus().then(setStatus).catch(() => {});
  }, []);

  // Initial load.
  useEffect(() => {
    getSystemInfo().then(setSys).catch((e) => setError(String(e)));
    recommendModel().then(setRecommended).catch(() => {});
    crucibleAvailable().then(setCrucibleOk).catch(() => {});
    modelsDir().then(setDir).catch(() => {});
    refreshModels();
    refreshStatus();
  }, [refreshModels, refreshStatus]);

  // Download progress stream.
  const unlisten = useRef<(() => void) | null>(null);
  useEffect(() => {
    onDownloadProgress((p) => {
      setProgress((prev) => ({ ...prev, [p.id]: p }));
      if (p.done) {
        setBusy((prev) => ({ ...prev, [p.id]: false }));
        if (p.error) setError(`Download failed: ${p.error}`);
        else refreshModels();
      }
    }).then((fn) => {
      unlisten.current = fn;
    });
    return () => {
      unlisten.current?.();
    };
  }, [refreshModels]);

  // Keep the server pill honest if the process exits on its own.
  useEffect(() => {
    const t = setInterval(refreshStatus, 4000);
    return () => clearInterval(t);
  }, [refreshStatus]);

  const handleDownload = (id: string) => {
    setError(null);
    setBusy((prev) => ({ ...prev, [id]: true }));
    setProgress((prev) => ({ ...prev, [id]: { id, downloaded: 0, total: 0, pct: 0, done: false, error: null } }));
    downloadModel(id).catch((e) => {
      setError(String(e));
      setBusy((prev) => ({ ...prev, [id]: false }));
    });
  };

  const handleDelete = (id: string) => {
    deleteModel(id).then(refreshModels).catch((e) => setError(String(e)));
  };

  const handleRun = (id: string) => {
    setError(null);
    startServer(id)
      .then(() => {
        setRunningId(id);
        refreshStatus();
      })
      .catch((e) => setError(String(e)));
  };

  const handleStop = () => {
    stopServer()
      .then(() => {
        setRunningId(null);
        refreshStatus();
      })
      .catch((e) => setError(String(e)));
  };

  const serverRunning = !!status?.running;

  return (
    <div className="mx-auto flex min-h-full max-w-6xl flex-col px-6 py-6">
      <header className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-crucible-accent/15 text-crucible-accent">
            <Flame />
          </div>
          <div>
            <h1 className="text-lg font-semibold leading-tight text-zinc-100">Crucible Studio</h1>
            <p className="text-xs text-zinc-500">Run frontier-grade local agents on your machine.</p>
          </div>
        </div>
        {serverRunning ? (
          <Badge tone="good">● Server on :{status?.port ?? 8000}</Badge>
        ) : (
          <Badge tone="muted">○ Server stopped</Badge>
        )}
      </header>

      {error && (
        <div className="mb-4 flex items-start justify-between gap-3 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          <span>{error}</span>
          <button className="shrink-0 text-red-300 hover:text-red-100" onClick={() => setError(null)}>
            Dismiss
          </button>
        </div>
      )}

      <main className="grid flex-1 grid-cols-1 gap-5 lg:grid-cols-[320px_1fr]">
        <div className="space-y-5">
          <SystemPanel info={sys} />
          <ServerControl
            status={status}
            runningId={runningId}
            models={models}
            crucibleOk={crucibleOk}
            onStop={handleStop}
          />
        </div>

        <ModelCatalog
          models={models}
          recommendedId={recommended}
          progress={progress}
          busy={busy}
          runningId={runningId}
          serverRunning={serverRunning}
          onDownload={handleDownload}
          onDelete={handleDelete}
          onRun={handleRun}
        />
      </main>

      <footer className="mt-6 flex items-center justify-between border-t border-crucible-border/60 pt-4 text-xs text-zinc-600">
        <span>
          Models stored in <code className="font-mono text-zinc-500">{dir || "…"}</code>
        </span>
        <span>Crucible Studio v0.1.0 · Apache-2.0</span>
      </footer>
    </div>
  );
}
