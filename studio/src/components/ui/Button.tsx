import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "ghost" | "danger" | "subtle";

const styles: Record<Variant, string> = {
  primary: "bg-crucible-accent text-black hover:brightness-110",
  ghost: "border border-crucible-border text-zinc-100 hover:bg-crucible-raised",
  danger: "border border-red-500/40 text-red-300 hover:bg-red-500/10",
  subtle: "text-zinc-400 hover:text-zinc-100",
};

export function Button({
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={`inline-flex cursor-pointer items-center justify-center gap-2 rounded-lg px-3.5 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-40 ${styles[variant]} ${className}`}
      {...props}
    />
  );
}
