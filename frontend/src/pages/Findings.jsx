import { useMemo } from "react";
import { motion } from "framer-motion";
import { AlertOctagon, AlertTriangle, CheckCircle2, ShieldAlert } from "lucide-react";
import { FindingsTable } from "../components/findings/FindingsTable";
import { Button, Card, EmptyState, ErrorState, LoadingState, PageHeading } from "../components/ui/Primitives";
import { useAssessments } from "../hooks/useApi";
import { findingsFromReport, severityCounts } from "../lib/utils";
import { Link } from "react-router-dom";

export default function Findings() {
  const assessments = useAssessments({ limit: 50, offset: 0 });
  const latest = assessments.data?.items?.[0];
  const findings = useMemo(() => findingsFromReport(latest?.audit_report), [latest]);
  const counts = severityCounts(findings);

  return (
    <motion.div className="page-stack" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <PageHeading
        eyebrow="EVIDENCE REGISTER"
        title="Security findings"
        description="Search and inspect findings from the latest persisted backend assessment."
        action={<Link to="/audit"><Button variant="outline"><ShieldAlert size={15} /> Run new audit</Button></Link>}
      />
      {assessments.isLoading ? <LoadingState label="Loading assessment findings…" /> : assessments.error ? (
        <ErrorState error={assessments.error} onRetry={() => assessments.refetch()} />
      ) : latest ? (
        <>
          <div className="finding-summary-grid">
            <Card><span className="summary-icon summary-red"><AlertOctagon size={16} /></span><small>CRITICAL</small><strong>{counts.CRITICAL}</strong></Card>
            <Card><span className="summary-icon summary-orange"><AlertTriangle size={16} /></span><small>HIGH</small><strong>{counts.HIGH}</strong></Card>
            <Card><span className="summary-icon summary-yellow"><AlertTriangle size={16} /></span><small>MEDIUM</small><strong>{counts.MEDIUM}</strong></Card>
            <Card><span className="summary-icon summary-green"><CheckCircle2 size={16} /></span><small>LOW / INFO</small><strong>{counts.LOW}</strong></Card>
          </div>
          <Card className="findings-card">
            <div className="section-heading">
              <div><div className="section-title">Latest assessment findings</div><div className="section-subtitle">Raw report from the backend · {latest.name || latest.id}</div></div>
              <span className="audit-date-chip">Assessment {latest.id?.slice(0, 8)}</span>
            </div>
            {findings.length ? <FindingsTable findings={findings} /> : (
              <EmptyState icon={CheckCircle2} title="No findings returned" description="The latest audit returned no findings. This does not certify the account or guarantee security." />
            )}
          </Card>
        </>
      ) : (
        <Card><EmptyState icon={ShieldAlert} title="No assessment findings yet" description="Run an audit to populate this view with actual AWS findings." action={<Link to="/audit"><Button>Start an audit</Button></Link>} /></Card>
      )}
    </motion.div>
  );
}
