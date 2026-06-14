import { useState } from "react";
import { Link } from "react-router-dom";
import { useStudio } from "../state/StudioContext";
import { fmtDuration } from "../lib/format";
import { Page, PageHeader } from "../components/layout/Page";
import { Button } from "../components/ui/Button";
import { Icon } from "../components/ui/Icon";
import { CopyButton, StatusDot } from "../components/ui/controls";

const BADGES = ["Tool calls grammar-guaranteed", "Token-frugal", "100% local"];

export function Server() {
  const { models, status, settings, updateSettings, recommendedId, run, stop, requestLog, crucibleOk } =
    useStudio();
  const running = !!status?.running;
  const downloaded = models.filter((m) => m.downloaded);

  const host = "127.0.0.1";
  const port = running ? status!.port : settings.port;
  const endpoint = running ? status!.base_url : `http://${host}:${port}/v1`;

  const defaultPick =
    downloaded.find((m) => m.id === recommendedId)?.id ?? downloaded[0]?.id ?? "";
  const [pick, setPick] = useState(defaultPick);
  const selected = pick || defaultPick;

  return (
    <Page>
      <PageHeader title="Server" subtitle="Serve your model on an OpenAI-compatible endpoint." />

      <div className="flex flex-col gap-xl">
        {/* Status hero */}
        <div className="rounded-lg border border-hairline bg-canvas p-xl">
          <div className="flex flex-col justify-between gap-md sm:flex-row sm:items-start">
            <div className="flex flex-col gap-sm">
              <div className="flex items-center gap-sm">
                <StatusDot on={running} pulse={running} />
                <h2 className="font-display-lg text-display-lg tracking-tight text-ink">
                  {running ? "Running" : "Stopped"}
                </h2>
              </div>
              {running ? (
                <div className="flex flex-wrap items-center gap-md font-code-block text-code-block text-mute-text">
                  <span className="rounded border border-hairline bg-canvas-inset px-sm py-base text-ink">
                    {status?.model_label}
                  </span>
                  <span>Uptime: {fmtDuration(status?.uptime_secs ?? 0)}</span>
                </div>
              ) : (
                <p className="font-body-sm text-body-sm text-mute-text">
                  No model is being served right now.
                </p>
              )}
            </div>

            {running ? (
              <Button variant="danger" icon="stop_circle" onClick={stop}>
                Stop
              </Button>
            ) : downloaded.length > 0 ? (
              <div className="flex items-center gap-sm">
                <div className="relative">
                  <select
                    value={selected}
                    onChange={(e) => setPick(e.target.value)}
                    className="h-10 appearance-none rounded-md border border-hairline bg-canvas pl-sm pr-8 font-body-sm text-body-sm text-ink outline-none focus:border-ink"
                  >
                    {downloaded.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.name}
                      </option>
                    ))}
                  </select>
                  <span className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2">
                    <Icon name="expand_more" size={18} className="text-mute-text" />
                  </span>
                </div>
                <Button
                  variant="ember"
                  icon="play_arrow"
                  disabled={!crucibleOk || !selected}
                  onClick={() => run(selected)}
                >
                  Start
                </Button>
              </div>
            ) : (
              <Link to="/models">
                <Button variant="primary" icon="download">
                  Get a model
                </Button>
              </Link>
            )}
          </div>

          {!crucibleOk && !running && (
            <p className="mt-md font-body-sm text-body-sm text-error">
              Crucible runtime not found. Released builds bundle it; for a dev run, install the
              crucible CLI.
            </p>
          )}

          <div className="mt-lg flex flex-wrap gap-sm">
            {BADGES.map((b) => (
              <span
                key={b}
                className="rounded-full border border-hairline-strong px-sm py-base font-label-mono text-label-mono text-body-text"
              >
                {b}
              </span>
            ))}
          </div>
        </div>

        {/* Endpoint */}
        <div className="flex flex-col gap-md rounded-lg border border-hairline bg-canvas p-lg">
          <h3 className="font-body-md text-body-md font-semibold text-ink">API Endpoint</h3>
          <div className="group flex items-center justify-between rounded-md border border-hairline bg-canvas-inset p-sm transition-colors hover:border-outline-variant">
            <span className="font-code-block text-code-block text-ink">{endpoint}</span>
            <CopyButton value={endpoint} />
          </div>
          <div className="mt-sm grid grid-cols-2 gap-md">
            <div className="flex flex-col gap-xs">
              <label className="font-label-mono text-[10px] uppercase tracking-widest text-mute-text">
                Host
              </label>
              <input
                readOnly
                value={host}
                className="h-10 w-full cursor-default rounded-md border border-hairline bg-canvas-inset px-sm font-code-block text-code-block text-mute-text outline-none"
              />
            </div>
            <div className="flex flex-col gap-xs">
              <label className="font-label-mono text-[10px] uppercase tracking-widest text-mute-text">
                Port
              </label>
              <input
                type="number"
                value={settings.port}
                onChange={(e) => updateSettings({ port: Number(e.target.value) || settings.port })}
                className="h-10 w-full rounded-md border border-hairline bg-canvas px-sm font-code-block text-code-block text-ink outline-none transition-colors focus:border-ink"
              />
            </div>
          </div>
          {running && status!.port !== settings.port && (
            <p className="font-label-mono text-label-mono text-mute-text">
              Serving on :{status!.port}. The new port applies the next time you start the server.
            </p>
          )}
        </div>

        {/* Connect tools */}
        <div className="flex flex-col gap-md">
          <h3 className="font-body-md text-body-md font-semibold text-ink">Connect Tools</h3>
          <div className="grid grid-cols-1 gap-md sm:grid-cols-3">
            {TOOLS.map((t) => (
              <div
                key={t.name}
                className="flex flex-col gap-md rounded-lg border border-hairline bg-canvas p-md transition-colors hover:border-outline-variant"
              >
                <div className="flex flex-col gap-xs">
                  <h4 className="font-body-md text-body-md font-medium text-ink">{t.name}</h4>
                  <p className="font-body-sm text-body-sm leading-tight text-mute-text">{t.blurb}</p>
                </div>
                <CopyConfigButton value={t.config(endpoint)} />
              </div>
            ))}
          </div>
        </div>

        {/* Request log */}
        <div className="flex flex-col gap-md">
          <h3 className="font-body-md text-body-md font-semibold text-ink">Request Log</h3>
          <div className="overflow-hidden rounded-lg border border-hairline bg-canvas">
            {requestLog.length === 0 ? (
              <p className="px-md py-sm font-code-block text-code-block text-mute-text">
                No requests yet — send a message in Chat and it shows up here.
              </p>
            ) : (
              <ul>
                {requestLog.slice(0, 8).map((r) => (
                  <li
                    key={r.id}
                    className="flex items-center gap-sm border-b border-hairline px-md py-sm font-code-block text-code-block text-body-text last:border-b-0"
                  >
                    <span
                      className={`h-2 w-2 shrink-0 rounded-full ${
                        r.status >= 200 && r.status < 300 ? "bg-ok" : "bg-error"
                      }`}
                    />
                    <span className="text-ink">{r.method}</span>
                    <span className="truncate">{r.path}</span>
                    <span className="ml-auto shrink-0">{r.status}</span>
                    <span className="shrink-0 text-mute-text">{r.ms}ms</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </Page>
  );
}

function CopyConfigButton({ value }: { value: string }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    } catch {
      /* clipboard unavailable */
    }
  };
  return (
    <button
      onClick={copy}
      className="mt-auto w-full rounded-md border border-hairline py-sm font-label-mono text-label-mono text-ink transition-colors hover:bg-canvas-inset"
    >
      {copied ? "Copied ✓" : "Copy Config"}
    </button>
  );
}

const TOOLS = [
  {
    name: "OpenCode",
    blurb: "Add Crucible as a custom provider in opencode.",
    config: (endpoint: string) =>
      JSON.stringify(
        {
          provider: {
            crucible: {
              npm: "@ai-sdk/openai-compatible",
              name: "Crucible (local)",
              options: { baseURL: endpoint },
              models: { "crucible-local": { name: "Crucible Local" } },
            },
          },
        },
        null,
        2,
      ),
  },
  {
    name: "Continue",
    blurb: "Use Crucible as an OpenAI-compatible model in Continue.dev.",
    config: (endpoint: string) =>
      JSON.stringify(
        {
          models: [
            {
              title: "Crucible",
              provider: "openai",
              model: "crucible-local",
              apiBase: endpoint,
              apiKey: "none",
            },
          ],
        },
        null,
        2,
      ),
  },
  {
    name: "Cursor / SDK",
    blurb: "Point any OpenAI client's base URL here; the API key can be anything.",
    config: (endpoint: string) =>
      [`OPENAI_BASE_URL=${endpoint}`, `OPENAI_API_KEY=local`, `# model: crucible-local`].join("\n"),
  },
];
