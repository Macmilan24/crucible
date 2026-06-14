import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  crucibleAvailable,
  deleteModel,
  downloadModel,
  getModels,
  getSystemInfo,
  modelsDir,
  onDownloadProgress,
  recommendModel,
  serverStatus,
  startServer,
  stopServer,
  type DownloadProgress,
  type ModelEntry,
  type ServerStatus,
  type SystemInfo,
} from "../lib/api";
import {
  applyTheme,
  loadSettings,
  saveSettings,
  type Settings,
} from "../lib/settings";

export interface RequestLogEntry {
  id: number;
  method: string;
  path: string;
  status: number;
  ms: number;
  at: number;
}

interface StudioValue {
  sys: SystemInfo | null;
  models: ModelEntry[];
  recommendedId: string | null;
  crucibleOk: boolean;
  status: ServerStatus | null;
  dir: string;
  progress: Record<string, DownloadProgress>;
  busy: Record<string, boolean>;
  error: string | null;
  settings: Settings;
  requestLog: RequestLogEntry[];

  serverRunning: boolean;

  setError: (e: string | null) => void;
  updateSettings: (patch: Partial<Settings>) => void;
  logRequest: (e: Omit<RequestLogEntry, "id" | "at">) => void;

  download: (id: string) => void;
  remove: (id: string) => void;
  run: (id: string) => Promise<void>;
  stop: () => Promise<void>;
  refreshModels: () => void;
  refreshStatus: () => void;
}

const StudioContext = createContext<StudioValue | null>(null);

export function StudioProvider({ children }: { children: ReactNode }) {
  const [sys, setSys] = useState<SystemInfo | null>(null);
  const [models, setModels] = useState<ModelEntry[]>([]);
  const [recommendedId, setRecommendedId] = useState<string | null>(null);
  const [crucibleOk, setCrucibleOk] = useState(true);
  const [status, setStatus] = useState<ServerStatus | null>(null);
  const [dir, setDir] = useState("");
  const [progress, setProgress] = useState<Record<string, DownloadProgress>>({});
  const [busy, setBusy] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [settings, setSettings] = useState<Settings>(() => loadSettings());
  const [requestLog, setRequestLog] = useState<RequestLogEntry[]>([]);
  const reqId = useRef(0);

  const refreshModels = useCallback(() => {
    getModels().then(setModels).catch((e) => setError(String(e)));
  }, []);
  const refreshStatus = useCallback(() => {
    serverStatus().then(setStatus).catch(() => {});
  }, []);
  const refreshSystem = useCallback(() => {
    getSystemInfo().then(setSys).catch(() => {});
  }, []);

  // Initial load.
  useEffect(() => {
    refreshSystem();
    recommendModel().then(setRecommendedId).catch(() => {});
    crucibleAvailable().then(setCrucibleOk).catch(() => {});
    modelsDir().then(setDir).catch(() => {});
    refreshModels();
    refreshStatus();
    applyTheme(settings.theme);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
    return () => unlisten.current?.();
  }, [refreshModels]);

  // Keep server pill + memory bar honest while the app is open.
  useEffect(() => {
    const t = setInterval(() => {
      refreshStatus();
      refreshSystem();
    }, 4000);
    return () => clearInterval(t);
  }, [refreshStatus, refreshSystem]);

  // Auto-start the recommended downloaded model once, if the user opted in.
  const autoStarted = useRef(false);
  useEffect(() => {
    if (autoStarted.current) return;
    if (!settings.autoStart || !crucibleOk) return;
    if (!status || status.running) return;
    if (models.length === 0) return;
    const downloaded = models.filter((m) => m.downloaded);
    if (downloaded.length === 0) return;
    const pick =
      downloaded.find((m) => m.id === recommendedId) ??
      downloaded.find((m) => m.fits) ??
      downloaded[0];
    autoStarted.current = true;
    startServer(pick.id, settings.port)
      .then(() => refreshStatus())
      .catch((e) => setError(String(e)));
  }, [settings.autoStart, settings.port, crucibleOk, status, models, recommendedId, refreshStatus]);

  const updateSettings = useCallback((patch: Partial<Settings>) => {
    setSettings((prev) => {
      const next = { ...prev, ...patch };
      saveSettings(next);
      if (patch.theme && patch.theme !== prev.theme) applyTheme(patch.theme);
      return next;
    });
  }, []);

  const logRequest = useCallback((e: Omit<RequestLogEntry, "id" | "at">) => {
    setRequestLog((prev) => {
      const entry: RequestLogEntry = { ...e, id: ++reqId.current, at: Date.now() };
      return [entry, ...prev].slice(0, 50);
    });
  }, []);

  const download = useCallback((id: string) => {
    setError(null);
    setBusy((prev) => ({ ...prev, [id]: true }));
    setProgress((prev) => ({
      ...prev,
      [id]: { id, downloaded: 0, total: 0, pct: 0, done: false, error: null },
    }));
    downloadModel(id).catch((e) => {
      setError(String(e));
      setBusy((prev) => ({ ...prev, [id]: false }));
    });
  }, []);

  const remove = useCallback(
    (id: string) => {
      deleteModel(id).then(refreshModels).catch((e) => setError(String(e)));
    },
    [refreshModels],
  );

  const run = useCallback(
    async (id: string) => {
      setError(null);
      try {
        await startServer(id, settings.port);
        refreshStatus();
      } catch (e) {
        setError(String(e));
      }
    },
    [settings.port, refreshStatus],
  );

  const stop = useCallback(async () => {
    try {
      await stopServer();
      refreshStatus();
    } catch (e) {
      setError(String(e));
    }
  }, [refreshStatus]);

  const value = useMemo<StudioValue>(
    () => ({
      sys,
      models,
      recommendedId,
      crucibleOk,
      status,
      dir,
      progress,
      busy,
      error,
      settings,
      requestLog,
      serverRunning: !!status?.running,
      setError,
      updateSettings,
      logRequest,
      download,
      remove,
      run,
      stop,
      refreshModels,
      refreshStatus,
    }),
    [
      sys,
      models,
      recommendedId,
      crucibleOk,
      status,
      dir,
      progress,
      busy,
      error,
      settings,
      requestLog,
      updateSettings,
      logRequest,
      download,
      remove,
      run,
      stop,
      refreshModels,
      refreshStatus,
    ],
  );

  return <StudioContext.Provider value={value}>{children}</StudioContext.Provider>;
}

export function useStudio(): StudioValue {
  const ctx = useContext(StudioContext);
  if (!ctx) throw new Error("useStudio must be used within StudioProvider");
  return ctx;
}
