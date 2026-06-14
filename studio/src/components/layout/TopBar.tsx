import { useLocation, useNavigate } from "react-router-dom";
import { titleForPath } from "../../nav";
import { useStudio } from "../../state/StudioContext";
import { Icon } from "../ui/Icon";
import { StatusDot } from "../ui/controls";

export function TopBar() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { status, settings, updateSettings } = useStudio();
  const running = !!status?.running;
  const title = titleForPath(pathname);

  return (
    <header className="flex h-12 shrink-0 items-center justify-between border-b border-hairline bg-canvas px-lg">
      <h2 className="font-body-md text-body-md font-semibold text-ink">{title}</h2>

      <div className="flex items-center gap-sm">
        <button
          onClick={() => navigate("/server")}
          className="flex items-center gap-xs rounded-full border border-hairline bg-canvas-inset px-sm py-1 transition-colors hover:border-outline-variant"
          title="Server status"
        >
          <StatusDot on={running} pulse={running} />
          <span className="font-label-mono text-label-mono text-body-text">
            {running ? status?.model_label ?? "Running" : "Stopped"}
          </span>
        </button>

        <button
          onClick={() => updateSettings({ theme: settings.theme === "dark" ? "light" : "dark" })}
          className="flex h-8 w-8 items-center justify-center rounded-md text-mute-text transition-colors hover:bg-surface-container-low hover:text-ink"
          title={settings.theme === "dark" ? "Switch to light" : "Switch to dark"}
        >
          <Icon name={settings.theme === "dark" ? "light_mode" : "dark_mode"} size={18} />
        </button>
      </div>
    </header>
  );
}
