import { useState } from "react";
import { ModelEntry, ServerStatus } from "../lib/api";
import { Badge } from "./ui/Badge";
import { Button } from "./ui/Button";
import { Card } from "./ui/Card";

interface Props {
  status: ServerStatus | null;
  runningId: string | null;
  models: ModelEntry[];
  crucibleOk: boolean;
  onStop: () => void;
}

export function ServerControl({ status, runningId, models, crucibleOk, onStop }: Props) {
  const [copied, setCopied] = useState(false);
  const running = !!status?.running;
  const runningModel = models.find((m) => m.id === runningId);
  const baseUrl = status?.base_url ?? "http://127.0.0.1:8000/v1";

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(baseUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard may be unavailable; ignore */
    }
  };

  return (
    <Card className="p-5">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-zinc-400">Server</h2>
        {running ? (
          <Badge tone="good">● Running</Badge>
        ) : (
          <Badge tone="muted">○ Stopped</Badge>
        )}
      </div>

      {!crucibleOk && (
        <div className="mb-3 rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-200">
          The <code className="font-mono">crucible</code> CLI wasn't found. Install Crucible, then
          reopen Studio — running a model launches <code className="font-mono">crucible serve</code>.
        </div>
      )}

      {running ? (
        <div className="space-y-3">
          <div>
            <div className="mb-1 text-xs text-zinc-500">Serving</div>
            <div className="font-medium text-zinc-100">{runningModel?.name ?? "model"}</div>
          </div>
          <div>
            <div className="mb-1 text-xs text-zinc-500">OpenAI-compatible endpoint</div>
            <div className="flex items-center gap-2">
              <code className="flex-1 truncate rounded-md bg-crucible-raised px-2.5 py-1.5 font-mono text-sm text-crucible-accent">
                {baseUrl}
              </code>
              <Button variant="ghost" onClick={copy}>
                {copied ? "Copied" : "Copy"}
              </Button>
            </div>
            <p className="mt-1.5 text-xs text-zinc-500">
              Point opencode, Continue, Cursor, or the <code className="font-mono">openai</code> SDK
              here.
            </p>
          </div>
          <Button variant="danger" className="w-full" onClick={onStop}>
            Stop server
          </Button>
        </div>
      ) : (
        <p className="py-2 text-sm text-zinc-500">
          Download a model, then press <span className="text-zinc-300">Run</span> to start the local
          server.
        </p>
      )}

      <div className="mt-4 flex flex-wrap gap-2 border-t border-crucible-border/60 pt-4">
        <Badge tone="good">✓ Tool calls guaranteed valid</Badge>
        <Badge tone="violet">Token-frugal</Badge>
        <Badge tone="muted">100% local</Badge>
      </div>
    </Card>
  );
}
