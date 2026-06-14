import type { ReactNode } from "react";

/**
 * The "Fixed Document Model" from the design system: a scrollable area whose
 * content is centered in an 800px column on a `canvas` page, framed by hairlines.
 * Used by every page except Chat (which has its own full-height composition).
 */
export function Page({ children }: { children: ReactNode }) {
  return (
    <div className="h-full overflow-y-auto bg-surface-bright">
      <div className="mx-auto min-h-full max-w-container border-x border-hairline bg-canvas px-md py-xl md:px-margin-page">
        {children}
      </div>
    </div>
  );
}

/** Standard page heading: large display title with an optional subtitle + actions. */
export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-xl flex flex-col gap-md sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 className="font-display-lg text-display-lg text-ink">{title}</h1>
        {subtitle && (
          <p className="mt-1 max-w-xl font-body-md text-body-md text-mute-text">{subtitle}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-sm">{actions}</div>}
    </div>
  );
}
