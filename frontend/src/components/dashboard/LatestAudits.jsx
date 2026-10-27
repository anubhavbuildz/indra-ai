import { ArrowUpRight, Clock3, FileSearch } from "lucide-react";
import { Link } from "react-router-dom";
import { formatDate, relativeTime } from "../../lib/utils";
import { Badge, Card, EmptyState } from "../ui/Primitives";

function reportSeverity(report) {
  if (!report) return "Unknown";
  if (report.critical_count) return "Critical";
  if (report.high_count) return "High";
  if (report.medium_count) return "Medium";
  return "Low";
}

export function LatestAudits({ items = [] }) {
  return (
    <Card className="latest-card">
      <div className="section-heading">
        <div>
          <div className="section-title">Recent assessments</div>
          <div className="section-subtitle">Completed runs from your workspace</div>
        </div>
        <Link className="text-link" to="/reports">
          View all <ArrowUpRight size={14} />
        </Link>
      </div>
      {items.length ? (
        <div className="audit-list">
          {items.slice(0, 5).map((item) => {
            const level = reportSeverity(item.audit_report);
            return (
              <Link to={`/reports/${item.id}`} className="audit-row" key={item.id}>
                <span className="audit-file-icon">
                  <FileSearch size={16} />
                </span>
                <span className="audit-row-main">
                  <strong>{item.name || item.question || "AWS security assessment"}</strong>
                  <small>
                    <Clock3 size={12} /> {relativeTime(item.created_at)} <i />{" "}
                    {item.audit_report?.audited_services?.length || 0} services
                  </small>
                </span>
                <Badge tone={level.toLowerCase()}>{level}</Badge>
                <span className="audit-row-date">{formatDate(item.created_at)}</span>
                <ArrowUpRight className="audit-arrow" size={15} />
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
