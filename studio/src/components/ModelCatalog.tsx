import { DownloadProgress, ModelEntry } from "../lib/api";
import { clampPct, fmtGb } from "../lib/format";
import { Badge } from "./ui/Badge";
import { Button } from "./ui/Button";
import { Card } from "./ui/Card";
import { Progress } from "./ui/Progress";

const IconDownload = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7 10 12 15 17 10" />
    <line x1="12" y1="15" x2="12" y2="3" />
  </svg>
);
const IconPlay = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
    <path d="M8 5v14l11-7z" />
  </svg>
);
const IconTrash = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6" />
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
  </svg>
);

interface Props {
  models: ModelEntry[];
  recommendedId: string | null;
  progress: Record<string, DownloadProgress>;
  busy: Record<string, boolean>;
  runningId: string | null;
  serverRunning: boolean;
  onDownload: (id: string) => void;
  onDelete: (id: string) => void;
  onRun: (id: string) => void;
}

function ModelRow({
  m,
  recommended,
  prog,
  busy,
  isRunning,
  serverRunning,
  onDownload,
  onDelete,
  onRun,
}: {
  m: ModelEntry;
  recommended: boolean;
  prog?: DownloadProgress;
  busy: boolean;
  isRunning: boolean;
  serverRunning: boolean;
  onDownload: () => void;
  onDelete: () => void;
  onRun: () => void;
}) {
  const downloading = busy && !m.downloaded;
  const pct = prog ? clampPct(prog.pct) : 0;

  return (
    <div
      className={`flex flex-col gap-3 rounded-lg border p-4 transition ${
        recommended ? "border-crucible-accent/40 bg-crucible-accent/[0.04]" : "border-crucible-border bg-crucible-raised/40"
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-semibold text-zinc-100">{m.name}</h3>
            <span className="font-mono text-xs text-zinc-500">
              {m.params} · {m.quant} · ~{fmtGb(m.approx_size_gb)}
            </span>
            {recommended && <Badge tone="accent">Recommended</Badge>}
            {isRunning && <Badge tone="good">● Serving</Badge>}
            {m.downloaded && !isRunning && <Badge tone="muted">Downloaded</Badge>}
            {!m.fits && <Badge tone="warn">Needs ~{fmtGb(m.min_ram_gb)} RAM</Badge>}
          </div>
          <p className="mt-1 text-sm text-zinc-400">{m.description}</p>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          {!m.downloaded && (
            <Button variant="primary" onClick={onDownload} disabled={downloading}>
              <IconDownload />
              {downloading ? "Downloading…" : "Download"}
            </Button>
          )}
          {m.downloaded && (
            <>
              <Button
                variant={isRunning ? "ghost" : "primary"}
                onClick={onRun}
                disabled={isRunning || (serverRunning && !isRunning)}
                title={serverRunning && !isRunning ? "Stop the running server first" : ""}
              >
                <IconPlay />
                {isRunning ? "Serving" : "Run"}
              </Button>
              <Button variant="danger" onClick={onDelete} disabled={isRunning} title="Delete model">
                <IconTrash />
              </Button>
            </>
          )}
        </div>
      </div>

      {downloading && (
        <div className="space-y-1.5">
          <Progress value={pct} />
          <div className="flex justify-between font-mono text-xs text-zinc-500">
            <span>{prog && prog.total > 0 ? `${fmtGb(prog.downloaded / 1024 ** 3)} / ${fmtGb(prog.total / 1024 ** 3)}` : "starting…"}</span>
            <span>{Math.round(pct)}%</span>
          </div>
        </div>
      )}
    </div>
  );
}

export function ModelCatalog(props: Props) {
  return (
    <Card className="p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-400">Models</h2>
        <span className="text-xs text-zinc-500">Q4_K_M GGUF · from Hugging Face</span>
      </div>
      <div className="space-y-3">
        {props.models.map((m) => (
          <ModelRow
            key={m.id}
            m={m}
            recommended={m.id === props.recommendedId}
            prog={props.progress[m.id]}
            busy={!!props.busy[m.id]}
            isRunning={m.id === props.runningId}
            serverRunning={props.serverRunning}
            onDownload={() => props.onDownload(m.id)}
            onDelete={() => props.onDelete(m.id)}
            onRun={() => props.onRun(m.id)}
          />
        ))}
      </div>
    </Card>
  );
}
