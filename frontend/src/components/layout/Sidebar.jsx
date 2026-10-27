import { motion } from "framer-motion";
import {
  Activity,
  Bot,
  ChevronLeft,
  ClipboardCheck,
  Cloud,
  FileText,
  LayoutDashboard,
  Search,
  Settings,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "../../lib/utils";
import indraaMark from "../../assets/indraa-mark.svg";

const navigation = [
  { label: "Overview", path: "/", icon: LayoutDashboard },
  { label: "Cloud audit", path: "/audit", icon: Cloud },
  { label: "AI agents", path: "/agents", icon: Bot },
  { label: "Findings", path: "/findings", icon: Search },
  { label: "Compliance", path: "/compliance", icon: ClipboardCheck },
  { label: "Reports", path: "/reports", icon: FileText },
];

export function Sidebar({ open, onClose, compact, onToggleCompact }) {
  return (
    <>
      {open && <button className="mobile-scrim" onClick={onClose} aria-label="Close navigation" />}
      <aside className={cn("sidebar", compact && "sidebar-compact", open && "sidebar-open")}>
        <div className="brand-row">
          <div className="brand-mark">
            <img src={indraaMark} alt="" />
          </div>
          {!compact && (
            <div className="brand-wordmark">
              <span>INDRAA</span>
              <small>AI CLOUD SECURITY POSTURE</small>
            </div>
          )}
          <button className="sidebar-collapse" onClick={onToggleCompact} aria-label="Toggle sidebar">
            <ChevronLeft size={15} />
          </button>
        </div>

        {!compact && <div className="sidebar-section-label">WORKSPACE</div>}
        <nav className="sidebar-nav">
          {navigation.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              onClick={onClose}
              title={compact ? label : undefined}
              className={({ isActive }) => cn("nav-link", isActive && "nav-link-active")}
            >
              <Icon size={18} strokeWidth={1.8} />
              {!compact && <span>{label}</span>}
              {!compact && path === "/findings" && <span className="nav-indicator" />}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-spacer" />
        {!compact && (
          <motion.div
            className="sidebar-credit"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="credit-signal">
              <Activity size={14} />
              <span>AI SECURITY SYSTEM</span>
            </div>
            <p>Evidence-led cloud security, built for clarity.</p>
            <div className="credit-footer">
              <span>POWERED BY</span>
              <strong>NVIDIA</strong>
            </div>
          </motion.div>
        )}
        <NavLink
          to="/settings"
          onClick={onClose}
          title={compact ? "Settings" : undefined}
          className={({ isActive }) => cn("nav-link settings-link", isActive && "nav-link-active")}
        >
          <Settings size={18} strokeWidth={1.8} />
          {!compact && <span>Settings</span>}
        </NavLink>
        {!compact && <div className="sidebar-version">INDRAA CONSOLE <span>v1.0</span></div>}
      </aside>
    </>
  );
}
