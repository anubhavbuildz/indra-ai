import { ExternalLink, FileText } from "lucide-react";

export function SourceList({ sources = [] }) {
  if (!sources.length) {
    return (
      <div className="source-empty">
        <FileText size={17} />
        <span>No source citations were returned for this response.</span>
      </div>
    );
  }
  return (
    <div className="source-list">
      {sources.map((source, index) => (
        <div className="source-item" key={`${source.title}-${index}`}>
          <span className="source-icon"><FileText size={15} /></span>
          <div>
            <strong>{source.title || source.source || "Guidance source"}</strong>
            <small>{source.source || "Retrieved local guidance"}</small>
          </div>
          {source.uri && (
            <a href={source.uri} target="_blank" rel="noreferrer" aria-label="Open guidance source">
              <ExternalLink size={14} />
            </a>
          )}
        </div>
      ))}
    </div>
  );
}
