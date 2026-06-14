import { useState, type ReactNode } from "react";
import { useStudio } from "../state/StudioContext";
import { openExternal } from "../lib/api";
import { type Theme } from "../lib/settings";
import { Page } from "../components/layout/Page";
import { Button } from "../components/ui/Button";
import { Icon } from "../components/ui/Icon";
import { CopyButton, Toggle } from "../components/ui/controls";

const APP_VERSION = "0.1.0";
const REPO_URL = "https://github.com/Macmilan24/Crucible";
const DOCS_URL = "https://macmilan24.github.io/Crucible/";

type Section = "general" | "models" | "server" | "about";
const SECTIONS: { id: Section; label: string }[] = [
  { id: "general", label: "General" },
  { id: "models", label: "Models" },
  { id: "server", label: "Server" },
  { id: "about", label: "About" },
];

export function Settings() {
  const { dir, settings, updateSettings } = useStudio();
  const [section, setSection] = useState<Section>("general");

  return (
    <Page>
      <div className="grid grid-cols-12 gap-gutter">
        {/* Sub-nav */}
        <aside className="col-span-12 md:col-span-3">
          <nav className="sticky top-0 flex flex-row gap-md md:flex-col md:gap-md">
            {SECTIONS.map((s) => (
              <button
                key={s.id}
                onClick={() => setSection(s.id)}
                className={[
                  "border-l-2 pl-sm text-left font-label-mono text-label-mono uppercase tracking-[1px] transition-colors",
                  section === s.id
                    ? "border-ink font-semibold text-ink"
                    : "border-transparent text-mute-text hover:text-ink",
                ].join(" ")}
              >
                {s.label}
              </button>
            ))}
          </nav>
        </aside>

        {/* Panel */}
        <div className="col-span-12 space-y-xl pb-margin-page md:col-span-9">
          {section === "general" && (
            <>
              <SectionHead title="General" subtitle="Appearance and launch behavior." />
              <Row label="Theme" help="Light is the default. Dark is available too.">
                <Segmented
                  value={settings.theme}
                  onChange={(t) => updateSettings({ theme: t })}
                  options={[
                    { value: "light", label: "Light" },
                    { value: "dark", label: "Dark" },
                  ]}
                />
              </Row>
              <Row
                label="Start server when Studio launches"
                help="Automatically serve your recommended downloaded model on launch."
                last
              >
                <Toggle
                  checked={settings.autoStart}
                  onChange={(v) => updateSettings({ autoStart: v })}
                  label="Start server on launch"
                />
              </Row>
            </>
          )}

          {section === "models" && (
            <>
              <SectionHead title="Models" subtitle="Where downloaded weights are stored." />
              <Row label="Models Directory" help="GGUF files Studio downloads are kept here." last>
                <div className="flex items-center gap-sm">
                  <div className="flex h-10 w-64 items-center rounded-md border border-hairline bg-canvas-inset px-sm">
                    <span className="truncate font-code-block text-code-block text-ink" title={dir}>
                      {dir || "…"}
                    </span>
                  </div>
                  <CopyButton value={dir} />
                  <Button
                    variant="outline"
                    icon="folder_open"
                    onClick={() => dir && openExternal(dir).catch(() => {})}
                  >
                    Reveal
                  </Button>
                </div>
              </Row>
            </>
          )}

          {section === "server" && (
            <>
              <SectionHead title="Server" subtitle="Defaults for the local inference API." />
              <Row label="Default Port" help="The port the OpenAI-compatible server listens on.">
                <input
                  type="number"
                  value={settings.port}
                  onChange={(e) => updateSettings({ port: Number(e.target.value) || settings.port })}
                  className="h-10 w-24 rounded-md border border-hairline bg-canvas px-sm text-center font-code-block text-code-block text-ink outline-none focus:border-ink"
                />
              </Row>
              <Row label="Host" help="Studio serves on loopback only — nothing leaves the machine." last>
                <div className="flex h-10 items-center rounded-md border border-hairline bg-canvas-inset px-sm">
                  <span className="font-code-block text-code-block text-mute-text">127.0.0.1</span>
                </div>
              </Row>
            </>
          )}

          {section === "about" && (
            <>
              <SectionHead title="About" subtitle="Build and project links." />
              <div className="rounded-md border border-hairline bg-canvas p-lg">
                <div className="flex items-start gap-md">
                  <div className="shrink-0 rounded-md border border-hairline bg-surface-container-low p-sm">
                    <Icon name="deployed_code" size={22} fill className="text-ink" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-body-md text-body-md font-semibold text-ink">
                      Crucible Studio
                    </h4>
                    <div className="mt-2 flex flex-wrap items-center gap-md">
                      <Meta label="Version">
                        <span className="rounded border border-hairline bg-surface-container-low px-2 py-0.5 font-code-block text-code-block text-ink">
                          {APP_VERSION}
                        </span>
                      </Meta>
                      <Meta label="License">
                        <span className="font-code-block text-code-block text-ink">Apache-2.0</span>
                      </Meta>
                    </div>
                    <div className="mt-md flex flex-wrap gap-lg border-t border-hairline pt-md">
                      <LinkRow icon="menu_book" onClick={() => openExternal(DOCS_URL)}>
                        Documentation
                      </LinkRow>
                      <LinkRow icon="code" onClick={() => openExternal(REPO_URL)}>
                        GitHub
                      </LinkRow>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </Page>
  );
}

function SectionHead({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="border-b border-hairline pb-md">
      <h3 className="font-body-lg text-body-lg font-medium text-ink">{title}</h3>
      <p className="mt-1 font-body-sm text-body-sm text-mute-text">{subtitle}</p>
    </div>
  );
}

function Row({
  label,
  help,
  children,
  last = false,
}: {
  label: string;
  help: string;
  children: ReactNode;
  last?: boolean;
}) {
  return (
    <div
      className={`flex flex-col gap-md sm:flex-row sm:items-center sm:justify-between ${
        last ? "" : "border-b border-hairline pb-lg"
      }`}
    >
      <div className="flex-1">
        <label className="block font-body-md text-body-md font-medium text-ink">{label}</label>
        <p className="mt-1 font-body-sm text-body-sm text-mute-text">{help}</p>
      </div>
      <div className="shrink-0">{children}</div>
    </div>
  );
}

function Segmented({
  value,
  onChange,
  options,
}: {
  value: Theme;
  onChange: (v: Theme) => void;
  options: { value: Theme; label: string }[];
}) {
  return (
    <div className="flex rounded-md border border-hairline bg-canvas-inset p-1">
      {options.map((o) => (
        <button
          key={o.value}
          onClick={() => onChange(o.value)}
          className={[
            "rounded px-md py-xs font-body-sm text-body-sm font-medium transition-colors",
            value === o.value
              ? "border border-hairline bg-canvas text-ink shadow-[0_1px_2px_rgba(0,0,0,0.05)]"
              : "border border-transparent text-mute-text hover:text-ink",
          ].join(" ")}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

function Meta({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex items-center gap-xs text-mute-text">
      <span className="font-label-mono text-label-mono uppercase">{label}:</span>
      {children}
    </div>
  );
}

function LinkRow({
  icon,
  onClick,
  children,
}: {
  icon: string;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-xs font-body-sm text-body-sm text-ink transition-colors hover:text-secondary"
    >
      <Icon name={icon} size={16} />
      {children}
    </button>
  );
}
