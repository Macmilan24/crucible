import { useMemo, useState, type ReactNode } from "react";
import { useStudio } from "../state/StudioContext";
import { type ModelEntry } from "../lib/api";
import { fmtBytesToGb, fmtGb, clampPct } from "../lib/format";
import { Page, PageHeader } from "../components/layout/Page";
import { Button } from "../components/ui/Button";
import { Icon } from "../components/ui/Icon";
import { Spinner } from "../components/ui/controls";

type Filter = "all" | "downloaded" | "compatible";

function specLine(m: ModelEntry): string {
  return `${m.params} · ${m.quant} · ~${fmtGb(m.approx_size_gb)}`;
}

export function Models() {
  const { models, recommendedId, progress, busy, status, download, remove, run, stop } = useStudio();
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("all");

  const runningId = status?.running ? status.model_id : null;

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return models.filter((m) => {
      if (q && !`${m.name} ${m.params} ${m.quant}`.toLowerCase().includes(q)) return false;
      if (filter === "downloaded") return m.downloaded;
      if (filter === "compatible") return m.fits;
      return true;
    });
  }, [models, query, filter]);

  const onMachine = filtered.filter((m) => m.downloaded);
  const available = filtered.filter((m) => !m.downloaded);
  const recommended = models.find((m) => m.id === recommendedId) ?? null;

  const chips: { id: Filter; label: string }[] = [
    { id: "all", label: "All" },
    { id: "downloaded", label: "Downloaded" },
    { id: "compatible", label: "Compatible" },
  ];

  return (
    <Page>
      <PageHeader title="Models" subtitle="Curated GGUF models. Download one that fits, then run it." />

      {/* Search + filters */}
      <div className="mb-xl flex flex-col gap-md md:flex-row md:items-center md:justify-between">
        <div className="relative w-full md:w-96">
          <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2">
            <Icon name="search" size={20} className="text-mute-text" />
          </span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search models..."
            className="h-10 w-full rounded-md border border-hairline bg-canvas-inset pl-10 pr-4 font-code-block text-code-block text-ink outline-none transition-colors placeholder:text-mute-text focus:border-ink"
          />
        </div>
        <div className="flex flex-wrap gap-xs">
          {chips.map((c) => (
            <button
              key={c.id}
              onClick={() => setFilter(c.id)}
              className={[
                "rounded-full border px-4 py-1.5 font-body-sm text-body-sm transition-colors",
                filter === c.id
                  ? "border-ink bg-ink text-on-primary"
                  : "border-hairline-strong bg-canvas text-ink hover:bg-canvas-inset",
              ].join(" ")}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {/* Recommended */}
      {recommended && filter === "all" && !query && (
        <RecommendedCard
          model={recommended}
          runningId={runningId}
          busy={!!busy[recommended.id]}
          progressPct={progress[recommended.id]?.done ? 100 : progress[recommended.id]?.pct}
          onDownload={() => download(recommended.id)}
          onRun={() => run(recommended.id)}
          onStop={stop}
        />
      )}

      {/* On your machine */}
      {onMachine.length > 0 && (
        <section className="mb-xl">
          <SectionTitle>On your machine</SectionTitle>
          <div className="flex flex-col gap-sm">
            {onMachine.map((m) => (
              <ModelRow
                key={m.id}
                model={m}
                runningId={runningId}
                busy={!!busy[m.id]}
                progress={progress[m.id]}
                onDownload={() => download(m.id)}
                onRun={() => run(m.id)}
                onStop={stop}
                onDelete={() => remove(m.id)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Available to download */}
      {available.length > 0 && (
        <section>
          <SectionTitle>Available to download</SectionTitle>
          <div className="flex flex-col gap-sm">
            {available.map((m) => (
              <ModelRow
                key={m.id}
                model={m}
                runningId={runningId}
                busy={!!busy[m.id]}
                progress={progress[m.id]}
                onDownload={() => download(m.id)}
                onRun={() => run(m.id)}
                onStop={stop}
                onDelete={() => remove(m.id)}
              />
            ))}
          </div>
        </section>
      )}

      {filtered.length === 0 && (
        <p className="py-xl text-center font-body-sm text-body-sm text-mute-text">
          No models match “{query}”.
        </p>
      )}
    </Page>
  );
}

function SectionTitle({ children }: { children: ReactNode }) {
  return (
    <h4 className="mb-md border-b border-hairline pb-2 font-label-mono text-label-mono uppercase tracking-widest text-mute-text">
      {children}
    </h4>
  );
}

function RecommendedCard({
  model,
  runningId,
  busy,
  progressPct,
  onDownload,
  onRun,
  onStop,
}: {
  model: ModelEntry;
  runningId: string | null | undefined;
  busy: boolean;
  progressPct?: number;
  onDownload: () => void;
  onRun: () => void;
  onStop: () => void;
}) {
  return (
    <div className="relative mb-xl overflow-hidden rounded-lg border border-hairline bg-gradient-to-r from-surface-container-high to-surface-container p-lg">
      <div className="pointer-events-none absolute -mr-16 -mt-16 right-0 top-0 h-32 w-32 rounded-full bg-gradient-to-br from-ember-start/10 to-ember-end/10 blur-2xl" />
      <div className="mb-sm flex items-center gap-xs">
        <Icon name="auto_awesome" size={18} className="text-ember-start" />
        <span className="font-label-mono text-label-mono font-semibold uppercase tracking-wider text-ember-start">
          Recommended for your machine
        </span>
      </div>
      <div className="flex flex-col justify-between gap-md md:flex-row md:items-end">
        <div>
          <h3 className="mb-1 font-display-md text-display-md font-bold text-ink">{model.name}</h3>
          <p className="mb-3 font-code-block text-code-block text-mute-text">{specLine(model)}</p>
          <p className="max-w-md font-body-sm text-body-sm text-body-text">{model.description}</p>
        </div>
        <div className="shrink-0">
          <ModelAction
            model={model}
            runningId={runningId}
            busy={busy}
            progressPct={progressPct}
            onDownload={onDownload}
            onRun={onRun}
            onStop={onStop}
            emphasis
          />
        </div>
      </div>
    </div>
  );
}

function ModelRow({
  model,
  runningId,
  busy,
  progress,
  onDownload,
  onRun,
  onStop,
  onDelete,
}: {
  model: ModelEntry;
  runningId: string | null | undefined;
  busy: boolean;
  progress?: { pct: number; downloaded: number; total: number; done: boolean };
  onDownload: () => void;
  onRun: () => void;
  onStop: () => void;
  onDelete: () => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const downloading = busy && !(progress?.done ?? false);
  const isRunning = runningId === model.id;

  return (
    <div
      className={[
        "relative overflow-hidden rounded-md border bg-canvas p-md transition-colors",
        isRunning ? "border-hairline-strong" : "border-hairline hover:border-hairline-strong",
      ].join(" ")}
    >
      {downloading && (
        <div
          className="ember-gradient absolute bottom-0 left-0 h-1"
          style={{ width: `${clampPct(progress?.pct ?? 0)}%` }}
        />
      )}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex flex-wrap items-center gap-3">
            <h5 className="font-body-lg text-body-lg font-semibold text-ink">{model.name}</h5>
            {isRunning ? (
              <Pill tone="ok">Running</Pill>
            ) : model.downloaded ? (
              <Pill tone="neutral">Downloaded</Pill>
            ) : !model.fits ? (
              <Pill tone="error">Needs {Math.round(model.min_ram_gb)} GB RAM</Pill>
            ) : null}
          </div>
          <p className="mb-2 font-code-block text-code-block text-mute-text">{specLine(model)}</p>
          <p className="line-clamp-1 font-body-sm text-body-sm text-body-text">
            {model.description}
          </p>
        </div>

        <div className="flex shrink-0 items-center justify-end gap-2 md:w-auto">
          {downloading ? (
            <div className="flex flex-col items-end">
              <span className="mb-1 font-code-block text-code-block font-semibold text-ink">
                {Math.round(progress?.pct ?? 0)}%
              </span>
              <span className="font-code-block text-[11px] text-mute-text">
                {progress && progress.total > 0
                  ? `${fmtBytesToGb(progress.downloaded)} / ${fmtBytesToGb(progress.total)}`
                  : "starting…"}
              </span>
            </div>
          ) : (
            <ModelAction
              model={model}
              runningId={runningId}
              busy={busy}
              onDownload={onDownload}
              onRun={onRun}
              onStop={onStop}
            />
          )}

          {model.downloaded && !downloading && (
            <div className="relative">
              <button
                onClick={() => setMenuOpen((v) => !v)}
                className="rounded-md p-1.5 text-mute-text transition-colors hover:bg-canvas-inset hover:text-ink"
                title="More"
              >
                <Icon name="more_vert" size={20} />
              </button>
              {menuOpen && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
                  <div className="absolute right-0 z-20 mt-1 w-40 overflow-hidden rounded-md border border-hairline bg-canvas shadow-[0_4px_16px_rgba(0,0,0,0.08)]">
                    <button
                      onClick={() => {
                        setMenuOpen(false);
                        if (confirm(`Delete ${model.name}? The GGUF file will be removed.`))
                          onDelete();
                      }}
                      disabled={isRunning}
                      className="flex w-full items-center gap-xs px-sm py-xs text-left font-body-sm text-body-sm text-error transition-colors hover:bg-error-container/40 disabled:opacity-40"
                    >
                      <Icon name="delete" size={16} />
                      Delete model
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/** The right-hand action for a model: Download / Run / Stop / Running-elsewhere. */
function ModelAction({
  model,
  runningId,
  busy,
  progressPct,
  onDownload,
  onRun,
  onStop,
  emphasis = false,
}: {
  model: ModelEntry;
  runningId: string | null | undefined;
  busy: boolean;
  progressPct?: number;
  onDownload: () => void;
  onRun: () => void;
  onStop: () => void;
  emphasis?: boolean;
}) {
  const isRunning = runningId === model.id;
  const otherRunning = !!runningId && runningId !== model.id;

  if (!model.downloaded) {
    const downloading = busy && progressPct !== 100;
    return (
      <Button
        variant={emphasis ? "primary" : "outline"}
        icon={downloading ? undefined : "download"}
        disabled={downloading}
        onClick={onDownload}
      >
        {downloading ? <Spinner size={16} /> : "Download"}
      </Button>
    );
  }

  if (isRunning) {
    return (
      <Button variant="danger" icon="stop_circle" onClick={onStop}>
        Stop
      </Button>
    );
  }

  return (
    <Button
      variant="ember"
      icon="play_arrow"
      onClick={onRun}
      disabled={otherRunning}
      title={otherRunning ? "Stop the running server first" : undefined}
    >
      Run
    </Button>
  );
}

function Pill({
  children,
  tone,
}: {
  children: ReactNode;
  tone: "ok" | "neutral" | "error";
}) {
  const tones: Record<string, string> = {
    ok: "bg-ok-soft text-ok border-ok/30",
    neutral: "bg-surface-dim text-ink border-outline-variant",
    error: "bg-error-container/50 text-error border-error/20",
  };
  return (
    <span
      className={`rounded border px-2 py-0.5 font-label-mono text-[10px] uppercase tracking-wide ${tones[tone]}`}
    >
      {children}
    </span>
  );
}
