import { useEffect, useMemo, useRef, useState, type KeyboardEvent } from "react";
import { Link } from "react-router-dom";
import { useStudio } from "../state/StudioContext";
import { chatCompletion, type ChatMessage } from "../lib/api";
import { fmtInt } from "../lib/format";
import { Glyph } from "../components/ui/Glyph";
import { Icon } from "../components/ui/Icon";
import { Button } from "../components/ui/Button";
import { CopyButton, Spinner } from "../components/ui/controls";

const SYSTEM_PROMPT =
  "You are Crucible, a helpful AI assistant running locally on the user's machine. Be concise and precise.";

const SUGGESTIONS = [
  "Explain what a KV cache is in one paragraph.",
  "Write a Python function to debounce calls.",
  "Summarize the tradeoffs of 4-bit quantization.",
];

interface Msg {
  role: "user" | "assistant";
  content: string;
  ts: number;
}

interface Totals {
  prompt: number;
  completion: number;
  total: number;
  requests: number;
  lastMs: number;
}

const ZERO: Totals = { prompt: 0, completion: 0, total: 0, requests: 0, lastMs: 0 };

export function Chat() {
  const { status, serverRunning, models, recommendedId, run, setError, logRequest } = useStudio();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [totals, setTotals] = useState<Totals>(ZERO);
  const scrollRef = useRef<HTMLDivElement>(null);

  const port = status?.port ?? 8000;
  const modelLabel = status?.model_label ?? "no model";

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading || !serverRunning) return;

    const userMsg: Msg = { role: "user", content: trimmed, ts: Date.now() };
    const history: ChatMessage[] = [
      { role: "system", content: SYSTEM_PROMPT },
      ...messages.map((m) => ({ role: m.role, content: m.content })),
      { role: "user", content: trimmed },
    ];
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const reply = await chatCompletion(port, null, history);
      setMessages((prev) => [...prev, { role: "assistant", content: reply.content, ts: Date.now() }]);
      setTotals((t) => ({
        prompt: t.prompt + reply.prompt_tokens,
        completion: t.completion + reply.completion_tokens,
        total: t.total + reply.total_tokens,
        requests: t.requests + 1,
        lastMs: reply.latency_ms,
      }));
      logRequest({ method: "POST", path: "/v1/chat/completions", status: 200, ms: reply.latency_ms });
    } catch (e) {
      setError(String(e));
      logRequest({ method: "POST", path: "/v1/chat/completions", status: 500, ms: 0 });
    } finally {
      setLoading(false);
    }
  };

  const startRecommended = () => {
    const downloaded = models.filter((m) => m.downloaded);
    const pick = downloaded.find((m) => m.id === recommendedId) ?? downloaded[0];
    if (pick) run(pick.id);
  };
  const hasDownloaded = models.some((m) => m.downloaded);

  return (
    <div className="flex h-full">
      {/* Document column */}
      <section className="flex min-w-0 flex-1 flex-col bg-surface-bright">
        <div ref={scrollRef} className="flex-1 overflow-y-auto">
          <div className="relative mx-auto flex min-h-full max-w-container flex-col border-x border-hairline bg-canvas px-md py-xl md:px-margin-page">
            {messages.length > 0 && (
              <div className="absolute right-md top-md">
                <button
                  onClick={() => {
                    setMessages([]);
                    setTotals(ZERO);
                  }}
                  className="rounded p-xs text-mute-text transition-colors hover:text-ink"
                  title="Clear conversation"
                >
                  <Icon name="delete_sweep" size={18} />
                </button>
              </div>
            )}

            {messages.length === 0 ? (
              <EmptyState
                serverRunning={serverRunning}
                hasDownloaded={hasDownloaded}
                onStart={startRecommended}
                onPick={(s) => send(s)}
              />
            ) : (
              <div className="flex flex-col gap-lg pb-xl">
                {messages.map((m, i) => (
                  <Message key={i} msg={m} />
                ))}
                {loading && <Thinking />}
              </div>
            )}
          </div>
        </div>

        {/* Composer */}
        <div className="border-t border-hairline bg-canvas">
          <div className="mx-auto w-full max-w-container px-md py-md md:px-margin-page">
            <Composer
              value={input}
              onChange={setInput}
              onSend={() => send(input)}
              disabled={!serverRunning}
              loading={loading}
              modelLabel={modelLabel}
            />
            <p className="mt-xs text-center font-label-mono text-[10px] text-mute-text">
              Crucible runs locally. No data leaves this machine.
            </p>
          </div>
        </div>
      </section>

      {/* Telemetry rail */}
      <aside className="hidden w-80 shrink-0 flex-col border-l border-hairline bg-canvas lg:flex">
        <div className="border-b border-hairline px-md py-lg">
          <h3 className="mb-lg font-label-mono text-label-mono uppercase tracking-wider text-mute-text">
            Session Telemetry
          </h3>
          <div className="mb-lg flex flex-col gap-sm">
            <span className="font-label-mono text-label-mono text-body-text">Tokens this session</span>
            <div className="font-code-block text-[36px] font-semibold leading-none tracking-tight text-ink">
              {fmtInt(totals.total)}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-sm">
            <Stat label="Prompt" value={fmtInt(totals.prompt)} />
            <Stat label="Completion" value={fmtInt(totals.completion)} />
            <Stat label="Requests" value={fmtInt(totals.requests)} />
            <Stat label="Last latency" value={totals.lastMs ? `${totals.lastMs}ms` : "—"} />
          </div>
        </div>
        <div className="px-md py-lg">
          <h3 className="mb-md font-label-mono text-label-mono uppercase tracking-wider text-mute-text">
            State
          </h3>
          <div className="flex items-center gap-sm">
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                loading ? "animate-pulse bg-ember-start" : serverRunning ? "bg-ok" : "bg-surface-dim"
              }`}
            />
            <span className="font-label-mono text-label-mono text-ink">
              {loading ? "Generating…" : serverRunning ? "Ready" : "Server stopped"}
            </span>
          </div>
        </div>
        <div className="mt-auto border-t border-hairline bg-canvas-inset px-md py-md text-center">
          <span className="font-label-mono text-[10px] text-mute-text">
            {serverRunning ? `${modelLabel} · local` : "Start a server to chat"}
          </span>
        </div>
      </aside>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-hairline bg-canvas-inset p-sm">
      <span className="block font-label-mono text-[10px] uppercase text-mute-text">{label}</span>
      <span className="font-code-block text-code-block font-semibold text-ink">{value}</span>
    </div>
  );
}

function EmptyState({
  serverRunning,
  hasDownloaded,
  onStart,
  onPick,
}: {
  serverRunning: boolean;
  hasDownloaded: boolean;
  onStart: () => void;
  onPick: (s: string) => void;
}) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center py-[80px] text-center">
      <Glyph size={56} className="mb-lg" />
      <h2 className="mb-sm font-display-md text-display-md text-ink">Talk to your local model</h2>
      {serverRunning ? (
        <>
          <p className="mb-xl font-body-sm text-body-sm text-mute-text">
            Your server is running. Ask it anything.
          </p>
          <div className="flex max-w-[520px] flex-wrap justify-center gap-sm">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => onPick(s)}
                className="rounded-full border border-hairline bg-canvas-inset px-md py-sm text-left font-body-sm text-body-sm text-body-text transition-colors hover:border-ink"
              >
                {s}
              </button>
            ))}
          </div>
        </>
      ) : (
        <>
          <p className="mb-xl max-w-sm font-body-sm text-body-sm text-mute-text">
            No server is running yet. Start one to begin chatting — it serves entirely on your
            machine.
          </p>
          {hasDownloaded ? (
            <Button variant="ember" icon="play_arrow" onClick={onStart}>
              Start recommended model
            </Button>
          ) : (
            <Link to="/models">
              <Button variant="primary" icon="download">
                Download a model
              </Button>
            </Link>
          )}
        </>
      )}
    </div>
  );
}

function Message({ msg }: { msg: Msg }) {
  const time = new Date(msg.ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  if (msg.role === "user") {
    return (
      <div className="flex w-full flex-col items-end pl-[15%]">
        <div className="mb-xs flex items-baseline gap-sm">
          <span className="font-label-mono text-label-mono text-mute-text">{time}</span>
          <span className="font-label-mono text-label-mono font-semibold text-ink">You</span>
        </div>
        <div className="whitespace-pre-wrap text-right font-body-md text-body-md leading-relaxed text-ink">
          {msg.content}
        </div>
      </div>
    );
  }
  return (
    <div className="flex w-full flex-col pr-[8%]">
      <div className="mb-xs flex items-center gap-sm">
        <Glyph size={16} />
        <span className="font-label-mono text-label-mono font-semibold text-ink">Crucible</span>
        <span className="font-label-mono text-label-mono text-mute-text">{time}</span>
      </div>
      <RichText text={msg.content} />
    </div>
  );
}

function Thinking() {
  return (
    <div className="flex w-full flex-col pr-[8%]">
      <div className="mb-xs flex items-center gap-sm">
        <Glyph size={16} />
        <span className="font-label-mono text-label-mono font-semibold text-ink">Crucible</span>
      </div>
      <div className="flex items-center gap-xs text-mute-text">
        <Spinner size={16} />
        <span className="font-body-sm text-body-sm">Generating…</span>
      </div>
    </div>
  );
}

/** Renders assistant text, turning ``` fenced ``` segments into copyable code blocks. */
function RichText({ text }: { text: string }) {
  const segments = useMemo(() => text.split("```"), [text]);
  return (
    <div className="flex flex-col gap-md font-body-md text-body-md leading-relaxed text-body-text">
      {segments.map((seg, i) => {
        if (i % 2 === 1) {
          const firstNl = seg.indexOf("\n");
          const code = firstNl >= 0 ? seg.slice(firstNl + 1) : seg;
          return <CodeBlock key={i} code={code.replace(/\n$/, "")} />;
        }
        return seg.trim() ? (
          <p key={i} className="whitespace-pre-wrap">
            {seg.trim()}
          </p>
        ) : null;
      })}
    </div>
  );
}

function CodeBlock({ code }: { code: string }) {
  return (
    <div className="group relative w-full overflow-hidden rounded-md border border-hairline bg-canvas-inset">
      <div className="absolute right-xs top-xs opacity-0 transition-opacity group-hover:opacity-100">
        <div className="rounded border border-hairline bg-canvas px-xs py-1">
          <CopyButton value={code} label="Copy" />
        </div>
      </div>
      <pre className="overflow-x-auto p-md font-code-block text-code-block text-ink">
        <code>{code}</code>
      </pre>
    </div>
  );
}

function Composer({
  value,
  onChange,
  onSend,
  disabled,
  loading,
  modelLabel,
}: {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  disabled: boolean;
  loading: boolean;
  modelLabel: string;
}) {
  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };
  return (
    <div className="flex flex-col rounded-xl border border-hairline bg-canvas transition-all focus-within:border-ink">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={onKeyDown}
        rows={2}
        disabled={disabled}
        placeholder={disabled ? "Start the server to chat…" : "Send a message…"}
        className="w-full resize-none border-none bg-transparent p-md font-body-md text-body-md text-ink outline-none placeholder:font-code-block placeholder:text-mute-text disabled:opacity-60"
      />
      <div className="flex items-center justify-between border-t border-hairline p-xs">
        <span className="flex items-center gap-1 rounded bg-surface-container px-sm py-xs text-ink">
          <Icon name="memory" size={16} />
          <span className="font-label-mono text-label-mono">{modelLabel}</span>
        </span>
        <button
          onClick={onSend}
          disabled={disabled || loading || !value.trim()}
          className="ember-gradient flex h-8 w-10 items-center justify-center rounded text-white transition-opacity hover:opacity-95 disabled:opacity-40"
          title="Send"
        >
          {loading ? <Spinner size={18} /> : <Icon name="send" size={18} />}
        </button>
      </div>
    </div>
  );
}
