// One definition of the app's pages, shared by the Sidebar and the TopBar so
// brand, order, icons, and titles can never drift between them.

export interface NavItem {
  path: string;
  label: string;
  icon: string;
}

export const NAV_ITEMS: NavItem[] = [
  { path: "/chat", label: "Chat", icon: "chat_bubble" },
  { path: "/models", label: "Models", icon: "deployed_code" },
  { path: "/server", label: "Server", icon: "dns" },
  { path: "/hardware", label: "Hardware", icon: "memory" },
  { path: "/settings", label: "Settings", icon: "settings" },
];

export function titleForPath(pathname: string): string {
  const hit = NAV_ITEMS.find((n) => pathname.startsWith(n.path));
  return hit ? hit.label : "Crucible";
}
