// A single wrapper over Material Symbols Outlined so icon usage is consistent
// (size, optical fill) across every page.

interface IconProps {
  name: string;
  size?: number;
  fill?: boolean;
  className?: string;
  title?: string;
}

export function Icon({ name, size = 20, fill = false, className = "", title }: IconProps) {
  return (
    <span
      className={`material-symbols-outlined${fill ? " fill" : ""} ${className}`}
      style={{ fontSize: size }}
      aria-hidden={title ? undefined : true}
      title={title}
    >
      {name}
    </span>
  );
}
