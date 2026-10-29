import { useMemo } from "react";
import { motion } from "framer-motion";
import {
  Activity,
  ArrowRight,
  CheckCircle2,
  Cloud,
  Database,
  Fingerprint,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";
import { Link } from "react-router-dom";
import { StatCard } from "../components/dashboard/StatCard";
import { SeverityChart } from "../components/dashboard/SeverityChart";
import { LatestAudits } from "../components/dashboard/LatestAudits";
import { Badge, Button, Card, ErrorState, LoadingState } from "../components/ui/Primitives";
import { useAssessments, useAwsIdentity, useBackendHealth, useRagStatus } from "../hooks/useApi";
import { findingsFromReport, formatDate, severityCounts } from "../lib/utils";

export default function Dashboard() {
  const assessments = useAssessments({ limit: 50, offset: 0 });
  const health = useBackendHealth();
  const rag = useRagStatus();
  const identity = useAwsIdentity();
  const items = assessments.data?.items || [];
  const latest = items[0];
  const report = latest?.audit_report;
  const findings = findingsFromReport(report);
  const observedCounts = severityCounts(findings);
  const counts = {
    CRITICAL: report?.critical_count ?? observedCounts.CRITICAL,
    HIGH: report?.high_count ?? observedCounts.HIGH,
    MEDIUM: report?.medium_count ?? observedCounts.MEDIUM,
    LOW: report?.low_count ?? observedCounts.LOW,
  };
  const serviceCount = report?.audited_services?.length || 0;
  const resourceCount = new Set(findings.map((item) => item.resource).filter(Boolean)).size;
  const coverage = useMemo(
    () => (serviceCount ? Math.round((serviceCount / 7) * 100) : 0),
    [serviceCount],
  );

  return (
    <motion.div className="page-stack" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <div className="dashboard-welcome">
        <div>
          <div className="eyebrow"><span className="status-dot" /> SECURITY OPERATIONS CENTER</div>
          <h1>Security overview</h1>
          <p>Your cloud security posture assessment, translated into evidence you can act on.</p>
        </div>
        <Link to="/audit">
          <Button><Activity size={16} /> Start an audit <ArrowRight size={15} /></Button>
        </Link>
      </div>

      <div className="overview-banner">
        <div className="overview-banner-orb"><ShieldCheck size={26} /></div>
        <div className="overview-banner-copy">
          <div className="banner-label">Indra-AI · CLOUD SECURITY POSTURE ASSESSMENT <span>LIVE</span></div>
          <strong>{latest ? "Your latest assessment is ready to review." : "Your cloud security workspace is ready."}</strong>
          <p>{latest ? `Last completed ${formatDate(latest.created_at)} · ${findings.length} findings returned.` : "Run a read-only AWS audit to surface real findings and evidence."}</p>
        </div>
        <div className="banner-availability">
          <div><span className={health.data ? "status-dot" : "status-dot status-dot-muted"} /> API {health.data ? "CONNECTED" : health.isLoading ? "CHECKING" : "UNAVAILABLE"}</div>
          <div><span className={rag.data?.available ? "status-dot" : "status-dot status-dot-amber"} /> RAG {rag.data?.available ? "INDEX READY" : rag.isLoading ? "CHECKING" : "CHECK STATUS"}</div>
        </div>
      </div>

      {assessments.isLoading ? (
        <LoadingState label="Loading your security overview…" />
      ) : assessments.error ? (
        <ErrorState error={assessments.error} onRetry={() => assessments.refetch()} />
      ) : (
        <>
          <div className="stats-grid">
            <StatCard label="Latest findings" value={report?.total_issues ?? "—"} note={latest ? "From latest completed run" : "Run an audit to begin"} icon={ShieldAlert} tone="red" />
            <StatCard label="Audited services" value={serviceCount || "—"} note={report?.audited_services?.map((item) => item.toUpperCase()).join(" · ") || "No audit data yet"} icon={Cloud} tone="blue" />
            <StatCard label="Resources in findings" value={latest ? resourceCount : "—"} note="Distinct resources reported by latest audit" icon={Fingerprint} tone="green" />
            <StatCard label="Assessment runs" value={items.length} note={identity.data?.account ? `AWS account ${identity.data.account}` : "Persisted audit history"} icon={Database} tone="violet" />
          </div>

          <div className="dashboard-grid">
            <SeverityChart counts={counts} />
            <Card className="coverage-card">
              <div className="section-heading">
                <div>
                  <div className="section-title">Audit & compliance coverage</div>
                  <div className="section-subtitle">Observed service scope from the latest completed run</div>
                </div>
                <Badge tone={coverage ? "blue" : "neutral"}>{coverage ? `${coverage}%` : "NO DATA"}</Badge>
              </div>
              <div className="coverage-ring-wrap">
                <div className="coverage-ring" style={{ "--coverage": `${coverage * 3.6}deg` }}>
                  <div><strong>{serviceCount}</strong><span>services</span></div>
                </div>
              </div>
              <div className="coverage-list">
                {["s3", "iam", "ec2", "vpc", "rds", "cloudtrail", "guardduty"].map((service) => {
                  const audited = report?.audited_services?.includes(service);
                  return (
                    <div key={service}>
                      {audited ? <CheckCircle2 size={14} className="icon-green" /> : <span className="coverage-not-run" />}
                      <span>{service.toUpperCase()}</span>
                      <small>{audited ? "Audited" : "Not in latest run"}</small>
                    </div>
                  );
                })}
              </div>
              <div className="coverage-disclaimer">
                Framework-control coverage is not scored by the backend. Compliance output and cited guidance are available in the review.
              </div>
            </Card>
          </div>
          <LatestAudits items={items} />
          <div className="dashboard-footnote">
            <ShieldCheck size={14} />
            All results are point-in-time observations from completed, read-only AWS checks.
          </div>
        </>
      )}
    </motion.div>
  );
}
