import { useMemo, useState } from "react";
import { ChevronDown, Search } from "lucide-react";
import { Input } from "../ui/Primitives";
import { titleCase } from "../../lib/utils";

const severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

function SeverityPill({ severity }) {
  const normalized = severities.includes(String(severity).toUpperCase())
    ? String(severity).toLowerCase()
    : "neutral";
  return <span className={`severity-pill severity-${normalized}`}>{severity || "Unrated"}</span>;
}

export function FindingsTable({ findings = [] }) {
  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState("All severities");
  const [expanded, setExpanded] = useState(null);

  const filtered = useMemo(
    () =>
      findings.filter((finding) => {
        const searchable = [
          finding.title,
          finding.issue,
          finding.resource,
          finding.service,
          finding.region,
          finding.check_id,
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        const matchesText = searchable.includes(search.toLowerCase());
        const matchesSeverity =
          severity === "All severities" ||
          String(finding.severity || "").toUpperCase() === severity.toUpperCase();
        return matchesText && matchesSeverity;
      }),
    [findings, search, severity],
  );

  return (
    <div className="findings-table-wrap">
      <div className="table-toolbar">
        <label className="table-search">
          <Search size={15} />
          <Input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search finding, resource, service…"
          />
        </label>
        <label className="select-wrap">
          <select value={severity} onChange={(event) => setSeverity(event.target.value)}>
            <option>All severities</option>
            {severities.map((item) => <option key={item}>{item}</option>)}
          </select>
          <ChevronDown size={14} />
        </label>
        <span className="table-result-count">{filtered.length} findings</span>
      </div>
      <div className="table-scroll">
        <table className="findings-table">
          <thead>
            <tr>
              <th>SEVERITY</th>
              <th>FINDING</th>
              <th>SERVICE</th>
              <th>RESOURCE</th>
              <th>REGION</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {filtered.map((finding, index) => {
              const isOpen = expanded === index;
              return (
                <tr className={isOpen ? "finding-expanded" : ""} key={`${finding.check_id}-${index}`}>
                  <td><SeverityPill severity={finding.severity} /></td>
                  <td className="finding-main-cell">
                    <strong>{finding.title || finding.issue || "Audit finding"}</strong>
                    <small>{finding.check_id || "Check ID unavailable"}</small>
                    {isOpen && (
                      <div className="finding-detail">
                        {finding.issue && <p>{finding.issue}</p>}
                        {finding.error && <p className="error-detail">Audit error: {finding.error}</p>}
                        {finding.evidence && (
                          <pre>{JSON.stringify(finding.evidence, null, 2)}</pre>
                        )}
                        {finding.remediation && (
                          <div><b>Suggested remediation</b><p>{finding.remediation}</p></div>
                        )}
                      </div>
                    )}
                  </td>
                  <td>{titleCase(finding.service || "—")}</td>
                  <td className="resource-cell">{finding.resource || "—"}</td>
                  <td>{finding.region || "—"}</td>
                  <td>
                    <button
                      className={`row-expand ${isOpen ? "row-expand-open" : ""}`}
                      onClick={() => setExpanded(isOpen ? null : index)}
                      aria-label={isOpen ? "Collapse finding details" : "Expand finding details"}
                    >
                      <ChevronDown size={15} />
                    </button>
                  </td>
                </tr>
              );
            })}
            {!filtered.length && (
              <tr><td className="table-empty" colSpan="6">No findings match these filters.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
