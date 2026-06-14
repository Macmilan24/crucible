export function fmtGb(gb: number): string {
  if (!isFinite(gb) || gb <= 0) return "—";
  return gb >= 10 ? `${Math.round(gb)} GB` : `${gb.toFixed(1)} GB`;
}

export function fmtBytesToGb(bytes: number): string {
  return fmtGb(bytes / 1024 / 1024 / 1024);
}

export function clampPct(pct: number): number {
  return Math.max(0, Math.min(100, pct));
}

/** Whole number with thousands separators, e.g. 14092 -> "14,092". */
export function fmtInt(n: number): string {
  return Math.round(n).toLocaleString("en-US");
}

/** Seconds as a clock-style uptime, e.g. 15153 -> "04:12:33". */
export function fmtDuration(totalSecs: number): string {
  const s = Math.max(0, Math.floor(totalSecs));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${pad(h)}:${pad(m)}:${pad(sec)}`;
}
