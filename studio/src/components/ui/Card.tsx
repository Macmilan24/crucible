import { ReactNode } from "react";

export function Card({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={`rounded-xl border border-crucible-border bg-crucible-panel ${className}`}>
      {children}
    </div>
  );
}
