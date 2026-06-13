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
