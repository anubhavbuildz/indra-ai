import { useState } from "react";
import { Outlet } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [compact, setCompact] = useState(false);
  const { username, signOut } = useAuth();

  return (
    <div className={`app-shell ${compact ? "app-shell-compact" : ""}`}>
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        compact={compact}
        onToggleCompact={() => setCompact((value) => !value)}
      />
      <div className="workspace">
        <Topbar onMenu={() => setSidebarOpen(true)} />
        <main className="main-content">
          <Outlet />
        </main>
        <footer className="app-footer">
          <span>INDRAA AI CLOUD SECURITY POSTURE</span>
          <span>{username ? `SIGNED IN · ${username}` : "SECURE WORKSPACE"}</span>
          <button onClick={signOut}>Sign out</button>
        </footer>
      </div>
    </div>
  );
}
