import { Menu, Search, ShieldCheck } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";

const pageNames = {
  "/": "Overview",
  "/audit": "Cloud audit",
  "/agents": "AI agents",
  "/findings": "Findings",
  "/compliance": "Compliance",
  "/reports": "Reports",
  "/settings": "Settings",
};

export function Topbar({ onMenu }) {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const heading = pathname.startsWith("/reports/") ? "Report details" : pageNames[pathname] || "Indraa";

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="mobile-menu" onClick={onMenu} aria-label="Open navigation">
          <Menu size={19} />
        </button>
        <div className="breadcrumbs">
          <span>Workspace</span>
          <span className="breadcrumb-divider">/</span>
          <strong>{heading}</strong>
        </div>
      </div>
      <div className="topbar-actions">
        <button className="topbar-search" onClick={() => navigate("/findings")}>
          <Search size={15} />
          <span>Search workspace</span>
          <kbd>⌘ K</kbd>
        </button>
        <div className="topbar-divider" />
        <div className="connection-indicator">
          <span className="status-dot" />
          <span>SECURE SESSION</span>
        </div>
        <div className="session-shield" title="Authenticated workspace">
          <ShieldCheck size={17} />
        </div>
      </div>
    </header>
  );
}
