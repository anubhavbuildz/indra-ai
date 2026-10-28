import { lazy, Suspense, useEffect } from "react";
import { LoaderCircle } from "lucide-react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { useAuth } from "./context/AuthContext";

const Agents = lazy(() => import("./pages/Agents"));
const CloudAudit = lazy(() => import("./pages/CloudAudit"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Findings = lazy(() => import("./pages/Findings"));
const Login = lazy(() => import("./pages/Login"));
const ReportDetail = lazy(() => import("./pages/ReportDetail"));
const Settings = lazy(() => import("./pages/Settings"));

function RouteLoading() {
  return (
    <div className="route-loading">
      <LoaderCircle className="spin" size={18} />
      Opening workspace…
    </div>
  );
}

function SessionEvents() {
  const { signOut } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    function expireSession() {
      signOut();
      navigate("/login", { replace: true });
    }
    window.addEventListener("indraa:session-expired", expireSession);
    return () => window.removeEventListener("indraa:session-expired", expireSession);
  }, [navigate, signOut]);

  return null;
}

export default function App() {
  return (
    <>
      <SessionEvents />
      <Suspense fallback={<RouteLoading />}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="audit" element={<CloudAudit />} />
              <Route path="agents" element={<Agents />} />
              <Route path="findings" element={<Findings />} />
              <Route path="reports/:assessmentId" element={<ReportDetail />} />
              <Route path="settings" element={<Settings />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </>
  );
}
