import { useState } from "react";
import { Icon } from "./Icon";

/** A small status dot — emerald when live, muted otherwise, with an optional pulse. */
export function StatusDot({ on, pulse = false }: { on: boolean; pulse?: boolean }) {
  return (
    <span className="relative inline-flex h-2.5 w-2.5">
      {on && pulse && (
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-ok opacity-60" />
      )}
      <span
        className={`relative inline-flex h-2.5 w-2.5 rounded-full ${
          on ? "bg-ok" : "bg-surface-dim"
        }`}
      />
    </span>
  );
}

/** Copies text to the clipboard and briefly confirms. */
export function CopyButton({
  value,
  className = "",
  label,
}: {
  value: string;
  className?: string;
  label?: string;
}) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    } catch {
      /* clipboard may be unavailable */
    }
  };
  return (
    <button
      onClick={copy}
      className={`inline-flex items-center gap-xs text-mute-text transition-colors hover:text-ink ${className}`}
      title="Copy"
    >
      <Icon name={copied ? "check" : "content_copy"} size={16} />
      {label && <span className="font-label-mono text-[10px]">{copied ? "Copied" : label}</span>}
    </button>
  );
}

/** An ember toggle switch. */
export function Toggle({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  label?: string;
}) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      aria-label={label}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ember-start/50 ${
        checked ? "ember-gradient" : "bg-surface-dim"
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition ${
          checked ? "translate-x-6" : "translate-x-1"
        }`}
      />
    </button>
  );
}

/** A spinning loader glyph. */
export function Spinner({ size = 16, className = "" }: { size?: number; className?: string }) {
  return (
    <span className={`inline-block animate-spin ${className}`} style={{ lineHeight: 0 }}>
      <Icon name="progress_activity" size={size} />
    </span>
  );
}
