import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Icon } from "./Icon";

type Variant = "primary" | "ember" | "outline" | "ghost" | "danger";
type Size = "sm" | "md";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  icon?: string;
  children?: ReactNode;
}

const base =
  "inline-flex items-center justify-center gap-xs rounded-md font-body-sm text-body-sm font-medium transition-all disabled:opacity-50 disabled:pointer-events-none focus:outline-none focus-visible:ring-2 focus-visible:ring-ink/20";

const variants: Record<Variant, string> = {
  primary: "bg-primary text-on-primary hover:opacity-90",
  ember:
    "ember-gradient text-white shadow-[inset_0_1px_1px_rgba(255,255,255,0.25)] hover:opacity-95",
  outline: "border border-hairline-strong bg-canvas text-ink hover:bg-canvas-inset",
  ghost: "text-mute-text hover:text-ink hover:bg-surface-container-low",
  danger: "border border-error text-error hover:bg-error-container",
};

const sizes: Record<Size, string> = {
  sm: "h-8 px-sm",
  md: "h-10 px-md",
};

export function Button({
  variant = "primary",
  size = "md",
  icon,
  children,
  className = "",
  ...rest
}: ButtonProps) {
  return (
    <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} {...rest}>
      {icon && <Icon name={icon} size={18} />}
      {children}
    </button>
  );
}
