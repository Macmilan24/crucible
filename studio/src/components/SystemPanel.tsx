import { SystemInfo } from "../lib/api";
import { fmtGb } from "../lib/format";
import { Card } from "./ui/Card";
import { Badge } from "./ui/Badge";

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 py-1.5">
      <span className="text-sm text-zinc-500">{label}</span>
      <span className="truncate text-right text-sm font-medium text-zinc-200">{value}</span>
    </div>
  );
}

export function SystemPanel({ info }: { info: SystemInfo | null }) {
  return (
    <Card className="p-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-400">
          Your machine
        </h2>
        {info?.apple_silicon && <Badge tone="violet">Apple Silicon</Badge>}
      </div>

      {info ? (
        <div className="divide-y divide-crucible-border/60">
          <Row label="CPU" value={info.cpu_brand} />
          <Row label="Cores" value={`${info.cpu_cores}`} />
          <Row
            label="Memory"
            value={`${fmtGb(info.total_ram_gb)} total · ${fmtGb(info.available_ram_gb)} free`}
          />
          <Row label="GPU" value={info.gpu} />
          <Row
            label="OS"
            value={`${info.os}${info.os_version ? ` ${info.os_version}` : ""} · ${info.arch}`}
          />
        </div>
      ) : (
        <div className="py-6 text-center text-sm text-zinc-500">Detecting hardware…</div>
      )}
    </Card>
  );
}
