import { motion } from "framer-motion";
import { ArrowLeft, Download, FileText, ShieldCheck } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { MarkdownView } from "../components/reports/MarkdownView";
import { FindingsTable } from "../components/findings/FindingsTable";
import { Badge, Button, Card, ErrorState, LoadingState, PageHeading } from "../components/ui/Primitives";
import { useAssessment } from "../hooks/useApi";
import { findingsFromReport, formatDate } from "../lib/utils";

export default function ReportDetail() {
  const { assessmentId } = useParams();
  const query = useAssessment(assessmentId);
  const item = query.data;

  function downloadReport() {
    const text = [
      `# ${item.name || "AWS security assessment"}`,
      `Assessment: ${item.id}`,
      `Created: ${formatDate(item.created_at)}`,
      "",
      "## Cloud Agent — Audit report",
      "```json",
      JSON.stringify(item.audit_report, null, 2),
      "```",
      "",
      "## Compliance Agent",
      item.compliance_review || "",
      "",
      "## Senior Agent",
      item.senior_review || "",
    ].join("\n");
    const blob = new Blob([text], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `Indra-AI-assessment-${item.id}.md`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <motion.div className="page-stack" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <Link to="/findings" className="back-link"><ArrowLeft size={14} /> Back to findings</Link>
      {query.isLoading ? <LoadingState label="Loading assessment report…" /> : query.error ? <ErrorState error={query.error} onRetry={() => query.refetch()} /> : item && (
        <>
          <PageHeading
            eyebrow={`ASSESSMENT · ${item.id}`}
            title={item.name || "AWS Security Assessment"}
            description={`Completed ${formatDate(item.created_at)} · ${item.audit_report?.audited_services?.join(", ") || "Services not listed"}`}
            action={<Button variant="outline" onClick={downloadReport}><Download size={15} /> Export Markdown</Button>}
          />
          <div className="report-detail-stats">
            <Card><span>Total findings</span><strong>{item.audit_report?.total_issues ?? 0}</strong></Card>
            <Card><span>Critical</span><strong className="text-critical">{item.audit_report?.critical_count ?? 0}</strong></Card>
            <Card><span>High</span><strong className="text-high">{item.audit_report?.high_count ?? 0}</strong></Card>
            <Card><span>Audited services</span><strong>{item.audit_report?.audited_services?.length || 0}</strong></Card>
          </div>
          <Card className="report-markdown-card">
            <div className="report-markdown-title"><span><FileText size={16} /></span><strong>Senior agent assessment</strong><Badge tone="green"><ShieldCheck size={12} /> REVIEWED</Badge></div>
            <MarkdownView text={item.senior_review || "No Senior review was saved for this assessment."} />
          </Card>
          <Card className="findings-card">
            <div className="section-heading"><div><div className="section-title">Cloud agent evidence</div><div className="section-subtitle">Structured finding details saved with this assessment</div></div></div>
            <FindingsTable findings={findingsFromReport(item.audit_report)} />
          </Card>
          <Card>
            <div className="section-heading"><div><div className="section-title">Compliance agent summary</div><div className="section-subtitle">Persisted summary for this report</div></div></div>
            <MarkdownView text={item.compliance_review || "No Compliance review was saved."} />
            <div className="report-source-note">Historical assessment records do not include RAG source citations; citations are included in the live chat response only.</div>
          </Card>
        </>
      )}
    </motion.div>
  );
}
