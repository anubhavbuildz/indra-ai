import { Menu } from "lucide-react";
import { useLocation } from "react-router-dom";

const pageNames = {
  "/": "Overview",
  "/audit": "Cloud audit",
  "/agents": "AI agents",
  "/findings": "Findings",
  "/settings": "Settings",
};

export function Topbar({ onMenu }) {
  const { pathname } = useLocation();
  const heading = pathname.startsWith("/reports/") || pathname.startsWith("/findings/")
    ? "Assessment details"
    : pageNames[pathname] || "Indraa";

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
    </header>
  );
}
