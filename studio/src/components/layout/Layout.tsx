import { Outlet } from "react-router-dom";
import { useStudio } from "../../state/StudioContext";
import { GlyphDefs } from "../ui/Glyph";
import { Icon } from "../ui/Icon";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

export function Layout() {
  const { error, setError } = useStudio();

  return (
    <div className="flex h-screen overflow-hidden bg-background text-body-text">
      <GlyphDefs />
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar />
        {error && (
          <div className="flex items-start justify-between gap-sm border-b border-error/30 bg-error-container/60 px-lg py-sm">
            <div className="flex items-center gap-xs text-on-error-container">
              <Icon name="error" size={18} />
              <span className="font-body-sm text-body-sm">{error}</span>
            </div>
            <button
              onClick={() => setError(null)}
              className="shrink-0 font-label-mono text-label-mono text-on-error-container/80 hover:text-on-error-container"
            >
              Dismiss
            </button>
          </div>
        )}
        <main className="min-h-0 flex-1 overflow-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
