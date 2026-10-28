import { ArrowUpRight, Clock3, FileSearch } from "lucide-react";
import { Link } from "react-router-dom";
import { formatDate, relativeTime } from "../../lib/utils";
import { Badge, Card, EmptyState } from "../ui/Primitives";

function reportSeverity(report) {
  if (report?.critical_count) return ["Critical", "critical"];
  if (report?.high_count) return ["High", "high"];
  if (report?.medium_count) return ["Medium", "medium"];
  return ["Low", "low"];
}

export function LatestAudits({ items = [] }) {
  return (
    <Card className="latest-card">
      <div className="section-heading">
        <div>
          <div className="section-title">Recent assessments</div>
          <div className="section-subtitle">Completed runs from your workspace</div>
        </div>
        <Link className="text-link" to="/findings">
          View all <ArrowUpRight size={14} />
        </Link>
      </div>
      {items.length ? (
        <div className="assessment-cards">
          {items.slice(0, 5).map((item) => {
            const [level, tone] = reportSeverity(item.audit_report);
            const summary = item.audit_report?.findings?.find((finding) => finding.title || finding.issue);
            const excerpt = summary?.title || summary?.issue || item.question || "Read-only AWS security assessment.";

            return (
              <Link to={`/reports/${item.id}`} className="assessment-card" key={item.id}>
                <div className="assessment-card-top">
                  <span className="assessment-card-icon"><FileSearch size={17} /></span>
                  <Badge tone={tone}>{level} risk</Badge>
                </div>
                <h3>{item.name || item.question || "AWS security assessment"}</h3>
                <p>{excerpt}</p>
                <div className="assessment-card-meta">
                  <span><Clock3 size={12} /> {relativeTime(item.created_at)}</span>
                  <span>{formatDate(item.created_at)}</span>
                </div>
                <div className="assessment-card-footer">
                  <span>{item.audit_report?.audited_services?.length || 0} services · {item.audit_report?.total_issues ?? 0} findings</span>
                  <span className="assessment-card-link">Read assessment <ArrowUpRight size={14} /></span>
                </div>
              </Link>
            );
          })}
        </div>
      ) : (
        <EmptyState
          icon={FileSearch}
          title="No completed assessments"
          description="Start an audit to see real assessment history here."
          action={<Link className="text-link" to="/audit">Start an audit <ArrowUpRight size={14} /></Link>}
        />
      )}
    </Card>
  );
}
