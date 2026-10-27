import { motion } from "framer-motion";
import { ArrowUpRight, FileText, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { Badge, Card, EmptyState, ErrorState, LoadingState, PageHeading } from "../components/ui/Primitives";
import { useAssessments } from "../hooks/useApi";
import { formatDate } from "../lib/utils";

function getRisk(item) {
  const report = item.audit_report || {};
  if (report.critical_count) return ["Critical", "critical"];
  if (report.high_count) return ["High", "high"];
  if (report.medium_count) return ["Medium", "medium"];
  return ["Low", "low"];
}

export default function Reports() {
  const query = useAssessments({ limit: 100, offset: 0 });
  const items = query.data?.items || [];

  return (
    <motion.div className="page-stack" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <PageHeading eyebrow="PERSISTED ASSESSMENTS" title="Security reports" description="Review completed backend assessments and their Senior agent verification." />
      <Card className="reports-card">
        <div className="section-heading">
          <div><div className="section-title">Assessment archive</div><div className="section-subtitle">Real records from the backend assessment store</div></div>
          <span className="report-count">{items.length} REPORTS</span>
        </div>
        {query.isLoading ? <LoadingState label="Loading reports…" /> : query.error ? <ErrorState error={query.error} onRetry={() => query.refetch()} /> : items.length ? (
          <div className="reports-list">
            {items.map((item) => {
              const [risk, tone] = getRisk(item);
              return (
                <Link className="report-row" key={item.id} to={`/reports/${item.id}`}>
                  <span className="report-file"><FileText size={17} /></span>
                  <span className="report-row-copy">
                    <strong>{item.name || item.question || "AWS Security Assessment"}</strong>
                    <small>{formatDate(item.created_at)} <i /> {item.audit_report?.audited_services?.length || 0} services <i /> {item.audit_report?.total_issues ?? 0} findings</small>
                  </span>
                  <Badge tone={tone}>{risk} risk</Badge>
                  <span className="report-status"><ShieldCheck size={13} /> {item.status || "completed"}</span>
                  <ArrowUpRight size={15} className="audit-arrow" />
                </Link>
              );
            })}
          </div>
        ) : (
          <EmptyState icon={FileText} title="No reports yet" description="Completed audits will be saved here with the separate Cloud, Compliance, and Senior outputs." />
        )}
      </Card>
    </motion.div>
  );
}
