import { useState } from "react";
import { motion } from "framer-motion";
import { Check, Cloud, Database, ExternalLink, Globe2, RefreshCw, Save, Shield, UserRound } from "lucide-react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import { api, getApiBaseUrl, saveApiBaseUrl } from "../services/api";
import { useAwsIdentity, useBackendHealth, useRagStatus } from "../hooks/useApi";
import { getErrorMessage } from "../lib/utils";
import { Badge, Button, Card, Input, PageHeading } from "../components/ui/Primitives";

export default function Settings() {
  const { username } = useAuth();
  const [url, setUrl] = useState(getApiBaseUrl());
  const [saved, setSaved] = useState(false);
  const [urlError, setUrlError] = useState("");
  const [busy, setBusy] = useState(false);
  const queryClient = useQueryClient();
  const health = useBackendHealth();
  const rag = useRagStatus();
  const identity = useAwsIdentity();
  const readiness = useQuery({ queryKey: ["backend-readiness"], queryFn: api.ready, retry: false });

  function saveSettings(event) {
    event.preventDefault();
    try {
      const parsed = new URL(url);
      if (!["http:", "https:"].includes(parsed.protocol)) throw new Error("Use an http or https URL.");
      saveApiBaseUrl(parsed.origin);
      setUrl(parsed.origin);
      setUrlError("");
      setSaved(true);
      queryClient.invalidateQueries();
      window.setTimeout(() => setSaved(false), 2200);
    } catch (error) {
      setUrlError(error.message || "Enter a valid backend URL.");
    }
  }

  async function refresh() {
    setBusy(true);
    try {
      await queryClient.invalidateQueries();
    } finally {
      setBusy(false);
    }
  }

  return (
    <motion.div className="page-stack" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <PageHeading eyebrow="WORKSPACE CONFIGURATION" title="Settings" description="Manage the frontend connection and inspect backend-reported integration status." />
      <div className="settings-layout">
        <div className="settings-main">
          <Card>
            <div className="section-heading">
              <div><div className="section-title">Backend connection</div><div className="section-subtitle">Set the backend origin used by this browser.</div></div>
              <span className="settings-card-icon"><Globe2 size={17} /></span>
            </div>
            <form className="settings-url-form" onSubmit={saveSettings}>
              <label><span>API base URL</span><Input value={url} onChange={(event) => setUrl(event.target.value)} placeholder="http://localhost:8000" /></label>
              <Button type="submit">{saved ? <><Check size={15} /> Saved</> : <><Save size={15} /> Save URL</>}</Button>
            </form>
            <div className="settings-helper">URL is stored in this browser only. Configure CORS_ORIGINS on the backend to allow your frontend origin.</div>
            {urlError && <div className="form-error">{urlError}</div>}
          </Card>

          <Card>
            <div className="section-heading">
              <div><div className="section-title">Integration status</div><div className="section-subtitle">Live results from public health and authenticated backend endpoints.</div></div>
              <Button variant="icon-outline" size="sm" onClick={refresh} disabled={busy}><RefreshCw size={14} className={busy ? "spin" : ""} /> Refresh</Button>
            </div>
            <div className="integration-list">
              <IntegrationRow icon={Cloud} label="Backend API" value={health.data?.status === "ok" ? "Connected" : health.isLoading ? "Checking" : "Unavailable"} detail={health.error?.message || (health.data ? `${health.data.service} · v${health.data.version}` : getErrorMessage(health.error))} ok={health.data?.status === "ok"} loading={health.isLoading} />
              <IntegrationRow icon={Database} label="Database configuration" value={readiness.data?.database_configured ? "Configured" : readiness.isLoading ? "Checking" : "Not configured"} detail={readiness.error?.message || "Readiness endpoint reports database URL configuration; no connectivity probe."} ok={readiness.data?.database_configured} loading={readiness.isLoading} />
              <IntegrationRow icon={Database} label="FAISS artifacts" value={rag.data?.available ? "Files present" : rag.isLoading ? "Checking" : "Unavailable"} detail={rag.data ? `Index: ${rag.data.index_available ? "present" : "missing"} · Metadata: ${rag.data.metadata_available ? "present" : "missing"}` : getErrorMessage(rag.error)} ok={rag.data?.available} loading={rag.isLoading} />
              <IntegrationRow
                icon={Cloud}
                label="AWS identity"
                value={identity.data?.status === "configured" ? "Verified" : identity.isLoading ? "Checking" : identity.data?.status || "Unavailable"}
                detail={
                  identity.data?.status === "configured"
                    ? `Account ${identity.data.account} · ${identity.data.region}`
                    : identity.data?.status === "not_configured"
                      ? "No AWS credentials are configured in the backend credential chain."
                      : getErrorMessage(identity.error)
                }
                ok={identity.data?.status === "configured"}
                loading={identity.isLoading}
              />
            </div>
          </Card>
          <Card className="settings-security-note">
            <Shield size={17} />
            <div><strong>Credentials stay on the backend</strong><p>AWS credentials, inference keys, login passwords, and the JWT signing key are never configured or stored in this frontend.</p></div>
          </Card>
        </div>
        <div className="settings-aside">
          <Card className="account-card">
            <div className="account-avatar"><UserRound size={20} /></div>
            <div className="account-label">AUTHENTICATED ACCOUNT</div>
            <strong>{username || "Configured user"}</strong>
            <Badge tone="green"><span className="status-dot" /> JWT session active</Badge>
            <small>Tokens are held in memory and cleared when the browser app is refreshed or you sign out.</small>
          </Card>
          <Card className="backend-features">
            <div className="section-title">Connected capabilities</div>
            <div><Check size={14} /> Chat workflow · separate agent outputs</div>
            <div><Check size={14} /> Assessment history and reports</div>
            <div><Check size={14} /> Local FAISS status and queries</div>
            <div><Check size={14} /> AWS caller identity</div>
            <a href={`${url}/docs`} target="_blank" rel="noreferrer">Open API docs <ExternalLink size={13} /></a>
          </Card>
        </div>
      </div>
    </motion.div>
  );
}

function IntegrationRow({ icon: Icon, label, value, detail, ok, loading }) {
  return (
    <div className="integration-row">
      <span className="integration-icon"><Icon size={16} /></span>
      <div className="integration-copy"><strong>{label}</strong><small>{detail}</small></div>
      <Badge tone={loading ? "neutral" : ok ? "green" : "red"}>{loading && <span className="mini-spinner" />}{value}</Badge>
    </div>
  );
}
