import { ReactNode } from "react";

type Tone = "accent" | "good" | "warn" | "muted" | "violet";

const tones: Record<Tone, string> = {
  accent: "bg-crucible-accent/15 text-crucible-accent ring-crucible-accent/30",
  good: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30",
  warn: "bg-amber-500/15 text-amber-300 ring-amber-500/30",
  muted: "bg-zinc-500/10 text-zinc-400 ring-zinc-500/20",
  violet: "bg-crucible-accent2/15 text-crucible-accent2 ring-crucible-accent2/30",
};

export function Badge({ tone = "muted", children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${tones[tone]}`}
    >
      {children}
    </span>
  );
}
