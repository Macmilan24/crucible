// Local, persisted preferences. Studio has no backend config store, so these
// live in localStorage — small, durable, and read before the first paint for
// theme (see index.html).

export type Theme = "light" | "dark";

export interface Settings {
  /** Port Studio starts the server on (the server reports the real one once up). */
  port: number;
  /** Light is the product default; dark is opt-in. */
  theme: Theme;
  /** Start the recommended downloaded model automatically when Studio launches. */
  autoStart: boolean;
}

const KEY = "crucible.settings";
const THEME_KEY = "crucible.theme"; // mirrored separately for the pre-paint bootstrap

export const DEFAULT_SETTINGS: Settings = {
  port: 8000,
  theme: "light",
  autoStart: false,
};

export function loadSettings(): Settings {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) {
      // Honor a theme set by the pre-paint bootstrap even before settings exist.
      const t = localStorage.getItem(THEME_KEY);
      return { ...DEFAULT_SETTINGS, theme: t === "dark" ? "dark" : "light" };
    }
    const parsed = JSON.parse(raw) as Partial<Settings>;
    return {
      port: typeof parsed.port === "number" && parsed.port > 0 ? parsed.port : DEFAULT_SETTINGS.port,
      theme: parsed.theme === "dark" ? "dark" : "light",
      autoStart: !!parsed.autoStart,
    };
  } catch {
    return { ...DEFAULT_SETTINGS };
  }
}

export function saveSettings(s: Settings): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(s));
    localStorage.setItem(THEME_KEY, s.theme);
  } catch {
    /* storage may be unavailable; preferences are best-effort */
  }
}

export function applyTheme(theme: Theme): void {
  const root = document.documentElement;
  if (theme === "dark") root.classList.add("dark");
  else root.classList.remove("dark");
}
