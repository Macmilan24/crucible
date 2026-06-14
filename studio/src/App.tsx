import { HashRouter, Navigate, Route, Routes } from "react-router-dom";
import { StudioProvider } from "./state/StudioContext";
import { Layout } from "./components/layout/Layout";
import { Chat } from "./pages/Chat";
import { Models } from "./pages/Models";
import { Server } from "./pages/Server";
import { Hardware } from "./pages/Hardware";
import { Settings } from "./pages/Settings";

export default function App() {
  return (
    <StudioProvider>
      <HashRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/models" element={<Models />} />
            <Route path="/server" element={<Server />} />
            <Route path="/hardware" element={<Hardware />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/chat" replace />} />
          </Route>
        </Routes>
      </HashRouter>
    </StudioProvider>
  );
}
