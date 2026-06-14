import { NavLink } from "react-router-dom";
import { NAV_ITEMS } from "../../nav";
import { useStudio } from "../../state/StudioContext";
import { openExternal } from "../../lib/api";
import { Glyph } from "../ui/Glyph";
import { Icon } from "../ui/Icon";
import { StatusDot } from "../ui/controls";

const REPO_URL = "https://github.com/Macmilan24/Crucible";
const DOCS_URL = "https://macmilan24.github.io/Crucible/";

export function Sidebar() {
  const { status } = useStudio();
  const running = !!status?.running;

  return (
    <nav className="hidden w-64 shrink-0 flex-col border-r border-hairline bg-canvas md:flex">
      {/* Brand */}
      <div className="flex items-center gap-sm border-b border-hairline px-lg py-lg">
        <Glyph size={28} />
        <div className="leading-none">
          <h1 className="font-display-md text-display-md font-bold tracking-tight text-ink">
            Crucible
          </h1>
          <p className="mt-1 font-label-mono text-label-mono text-mute-text">Local Runtime</p>
        </div>
      </div>

      {/* Primary nav */}
      <div className="flex-1 overflow-y-auto px-sm py-md">
        <ul className="flex flex-col gap-1">
          {NAV_ITEMS.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  [
                    "flex items-center gap-sm rounded-md border-l-2 py-sm pl-md pr-sm transition-colors",
                    isActive
                      ? "border-ember-start bg-surface-container-low font-semibold text-ink"
                      : "border-transparent text-mute-text hover:bg-surface-container-low hover:text-ink",
                  ].join(" ")
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon name={item.icon} size={20} fill={isActive} />
                    <span className="font-body-sm text-body-sm">{item.label}</span>
                  </>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>

      {/* Footer: live server status + external links */}
      <div className="border-t border-hairline px-md py-md">
        <NavLink
          to="/server"
          className="mb-sm flex items-center gap-xs rounded-md px-sm py-xs hover:bg-surface-container-low"
        >
          <StatusDot on={running} pulse={running} />
          <span className="font-label-mono text-label-mono text-body-text">
            {running ? `Running · :${status?.port ?? 8000}` : "Server stopped"}
          </span>
        </NavLink>
        <div className="flex flex-col gap-1">
          <button
            onClick={() => openExternal(DOCS_URL).catch(() => {})}
            className="flex items-center gap-sm rounded-md px-sm py-xs text-mute-text transition-colors hover:bg-surface-container-low hover:text-ink"
          >
            <Icon name="description" size={18} />
            <span className="font-label-mono text-label-mono uppercase">Docs</span>
          </button>
          <button
            onClick={() => openExternal(REPO_URL).catch(() => {})}
            className="flex items-center gap-sm rounded-md px-sm py-xs text-mute-text transition-colors hover:bg-surface-container-low hover:text-ink"
          >
            <Icon name="code" size={18} />
            <span className="font-label-mono text-label-mono uppercase">GitHub</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
