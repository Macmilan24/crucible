import { type ReactNode } from "react";
import { useStudio } from "../state/StudioContext";
import { type SystemInfo } from "../lib/api";
import { fmtGb, clampPct } from "../lib/format";
import { Page, PageHeader } from "../components/layout/Page";
import { Icon } from "../components/ui/Icon";

const OS_LABEL: Record<string, string> = { macos: "macOS", windows: "Windows", linux: "Linux" };

// Representative RAM floors per size class (Q4_K_M, incl. KV + overhead). The
// three smaller points match the model catalog; 32B is an estimate.
const SCALE = [
  { label: "1.5B", minRam: 4 },
  { label: "7B", minRam: 10 },
  { label: "14B", minRam: 20 },
  { label: "32B+", minRam: 36 },
];

type Verdict = "ok" | "tight" | "over";
function verdictFor(totalRam: number, minRam: number): Verdict {
  if (totalRam >= minRam * 1.25) return "ok";
  if (totalRam >= minRam) return "tight";
  return "over";
}

export function Hardware() {
  const { sys, models, recommendedId } = useStudio();

  if (!sys) {
    return (
      <Page>
        <PageHeader title="Hardware" subtitle="Reading system diagnostics…" />
        <div className="h-40 animate-pulse rounded-md border border-hairline bg-canvas-inset" />
      </Page>
    );
  }

  const usedRam = Math.max(0, sys.total_ram_gb - sys.available_ram_gb);
  const usedPct = clampPct(sys.total_ram_gb > 0 ? (usedRam / sys.total_ram_gb) * 100 : 0);
  const osLabel = OS_LABEL[sys.os] ?? sys.os;

  const recommended = models.find((m) => m.id === recommendedId) ?? null;
  // The largest scale point this machine can run at all = "current target".
  const targetIndex = SCALE.reduce(
    (acc, p, i) => (sys.total_ram_gb >= p.minRam ? i : acc),
    -1,
  );

  return (
    <Page>
      <PageHeader
        title="Hardware"
        subtitle="System diagnostics and capacity assessment for local inference."
        actions={<AccelPill sys={sys} />}
      />

      {/* Specs */}
      <div className="mb-xl grid grid-cols-1 gap-4 md:grid-cols-2">
        <SpecCard icon="developer_board" title="Processor" tag="CPU">
          <p className="mb-1 font-code-block text-code-block text-ink">{sys.cpu_brand}</p>
          <p className="font-label-mono text-label-mono text-mute-text">{sys.cpu_cores} cores</p>
        </SpecCard>

        <SpecCard icon="memory_alt" title="Graphics" tag="GPU">
          <p className="font-code-block text-code-block text-ink">{sys.gpu}</p>
        </SpecCard>

        <div className="md:col-span-2">
          <SpecCard icon="dataset" title="Memory" tag="RAM">
            <div className="mb-2 flex items-end justify-between">
              <div className="font-code-block text-code-block text-ink">
                {fmtGb(sys.total_ram_gb)} Total
                <span className="mx-1 text-mute-text">/</span>
                <span className="text-body-text">{fmtGb(sys.available_ram_gb)} Free</span>
              </div>
              <span className="font-label-mono text-label-mono text-mute-text">
                {Math.round(usedPct)}% In Use
              </span>
            </div>
            <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-canvas-inset">
              <div
                className="h-full rounded-full bg-gradient-to-r from-ember-end to-ember-start transition-[width] duration-500"
                style={{ width: `${usedPct}%` }}
              />
            </div>
          </SpecCard>
        </div>

        <div className="flex flex-col justify-between gap-4 rounded-md border border-hairline bg-canvas-inset p-4 md:col-span-2 md:flex-row md:items-center">
          <div className="flex items-center gap-3 text-mute-text">
            <Icon name={sys.os === "macos" ? "laptop_mac" : "computer"} size={20} />
            <span className="font-code-block text-code-block">
              System: {osLabel} {sys.os_version}
            </span>
          </div>
          <span className="rounded bg-surface-dim px-2 py-1 font-label-mono text-label-mono text-mute-text">
            {sys.arch} architecture
          </span>
        </div>
      </div>

      {/* Capacity verdict */}
      <section>
        <h2 className="mb-6 border-b border-hairline pb-2 font-display-md text-display-md font-bold text-ink">
          Capacity Verdict
        </h2>
        <div className="rounded-md border border-hairline bg-canvas p-6">
          <div className="mb-8 flex items-start gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md border border-hairline bg-canvas-inset">
              <Icon name="check_circle" size={22} fill className="text-ink" />
            </div>
            <div>
              <p className="font-body-lg text-body-lg font-bold leading-tight text-ink">
                {recommended
                  ? `Comfortably runs up to ${recommended.params} models.`
                  : "Best suited to compact models."}
              </p>
              <p className="mt-1 font-body-sm text-body-sm text-mute-text">
                {sys.apple_silicon
                  ? "Unified memory and Metal acceleration handle quantized inference well."
                  : "Quantized GGUF inference runs on CPU/GPU as detected by llama.cpp at load."}
              </p>
            </div>
          </div>

          {/* Scale */}
          <div className="relative pb-2 pt-6">
            <div className="absolute left-0 right-0 top-8 flex h-1 overflow-hidden rounded-full bg-canvas-inset">
              <div className="h-full bg-ok" style={{ width: "40%" }} />
              <div className="h-full bg-warn" style={{ width: "30%" }} />
              <div className="h-full bg-error" style={{ width: "30%" }} />
            </div>
            <div className="relative flex justify-between px-1">
              {SCALE.map((p, i) => {
                const v = verdictFor(sys.total_ram_gb, p.minRam);
                const isTarget = i === targetIndex;
                const dot =
                  v === "ok" ? "bg-ok" : v === "tight" ? "bg-warn" : "bg-error";
                const note =
                  v === "ok" ? "Fits easily" : v === "tight" ? "Tight" : "Too big";
                const noteColor =
                  v === "ok"
                    ? "text-mute-text"
                    : v === "tight"
                      ? "text-warn"
                      : "text-error";
                return (
                  <div key={p.label} className="flex flex-col items-center">
                    <div className="relative mb-2">
                      {isTarget && (
                        <span
                          className={`absolute -left-0.5 -top-0.5 h-4 w-4 animate-ping rounded-full opacity-50 ${dot}`}
                        />
                      )}
                      <span
                        className={`relative z-10 block h-3 w-3 rounded-full ring-2 ring-canvas ${dot}`}
                      />
                    </div>
                    <span
                      className={`font-code-block text-code-block ${
                        isTarget ? "font-bold text-ink" : "text-mute-text"
                      }`}
                    >
                      {p.label}
                    </span>
                    <span className={`mt-1 font-label-mono text-[10px] ${noteColor}`}>
                      {isTarget ? "Current target" : note}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>
    </Page>
  );
}

function AccelPill({ sys }: { sys: SystemInfo }) {
  const label = sys.apple_silicon ? "Metal · unified memory" : sys.os === "macos" ? "Metal" : sys.arch;
  return (
    <div className="flex items-center gap-2 rounded-full border border-hairline bg-canvas-inset px-3 py-1.5">
      <span className="h-2 w-2 rounded-full bg-ok" />
      <span className="font-label-mono text-label-mono text-ink">{label}</span>
    </div>
  );
}

function SpecCard({
  icon,
  title,
  tag,
  children,
}: {
  icon: string;
  title: string;
  tag: string;
  children: ReactNode;
}) {
  return (
    <div className="rounded-md border border-hairline bg-canvas p-5 transition-colors hover:border-hairline-strong">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="flex items-center gap-2 font-body-sm text-body-sm font-bold text-ink">
          <Icon name={icon} size={18} className="text-mute-text" />
          {title}
        </h3>
        <span className="font-label-mono text-label-mono text-mute-text">{tag}</span>
      </div>
      {children}
    </div>
  );
}
