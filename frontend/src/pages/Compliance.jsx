import { useState } from "react";
import { motion } from "framer-motion";
import { BookOpenCheck, Database, ExternalLink, FileSearch, Search, ShieldCheck } from "lucide-react";
import { SourceList } from "../components/compliance/SourceList";
import { Button, Card, ErrorState, Input, LoadingState, PageHeading } from "../components/ui/Primitives";
import { useLatestAudit, useRagQueryMutation, useRagStatus } from "../hooks/useApi";
import { getErrorMessage } from "../lib/utils";

export default function Compliance() {
  const [question, setQuestion] = useState("What guidance applies to the AWS security findings in my account?");
  const [errorMessage, setErrorMessage] = useState("");
  const ragStatus = useRagStatus();
  const mutation = useRagQueryMutation();
  const latest = useLatestAudit();

  async function submit(event) {
    event.preventDefault();
    setErrorMessage("");
    try {
      await mutation.mutateAsync(question);
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    }
  }

  return (
    <motion.div className="page-stack" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <PageHeading
        eyebrow="LOCAL RETRIEVAL · EVIDENCE ATTRIBUTION"
        title="Compliance guidance"
        description="Query the configured FAISS store and inspect citations returned by the actual backend."
        action={
          <div className={`rag-health-chip ${ragStatus.data?.available ? "rag-health-ready" : ""}`}>
            <span className={ragStatus.data?.available ? "status-dot" : "status-dot status-dot-amber"} />
            {ragStatus.data?.available ? "INDEX FILES PRESENT" : ragStatus.isLoading ? "CHECKING INDEX" : "INDEX NOT CONFIRMED"}
          </div>
        }
      />
      <Card className="compliance-query-card">
        <div className="compliance-query-head">
          <span className="compliance-query-icon"><BookOpenCheck size={18} /></span>
          <div><strong>Ask the local guidance index</strong><small>Direct retrieval returns passages and sources. It does not invoke an LLM.</small></div>
        </div>
        <form className="compliance-query-form" onSubmit={submit}>
          <Input value={question} onChange={(event) => setQuestion(event.target.value)} maxLength={8000} required />
          <Button type="submit" disabled={mutation.isPending || !question.trim()}>
            {mutation.isPending ? <><span className="mini-spinner" /> Searching</> : <><Search size={15} /> Retrieve guidance</>}
          </Button>
        </form>
        {ragStatus.data && (
          <div className="rag-files-status">
            <span><Database size={13} /> {ragStatus.data.embedding_model}</span>
            <span>{ragStatus.data.index_available ? "Index file present" : "Index file missing"}</span>
            <span>{ragStatus.data.metadata_available ? "Metadata present" : "Metadata missing"}</span>
            <small>Status checks file presence only; retrieval validates compatibility.</small>
          </div>
        )}
        {ragStatus.error && <div className="inline-warning">RAG status unavailable: {getErrorMessage(ragStatus.error)}</div>}
        {errorMessage && <ErrorState error={{ message: errorMessage }} />}
      </Card>

      {mutation.isPending && <Card className="retrieval-loading"><LoadingState label="Retrieving local guidance…" /></Card>}
      {mutation.data && (
        <Card className="retrieval-results">
          <div className="section-heading">
            <div><div className="section-title">Retrieved passages</div><div className="section-subtitle">{mutation.data.passages.length} source passages returned for this query</div></div>
            <span className="retrieval-tag"><Database size={13} /> FAISS</span>
          </div>
          {mutation.data.passages.length ? (
            <div className="passage-list">
              {mutation.data.passages.map((passage, index) => (
                <article className="passage-card" key={`${passage.title}-${index}`}>
                  <div className="passage-number">{String(index + 1).padStart(2, "0")}</div>
                  <div className="passage-body">
                    <div className="passage-title-row"><h3>{passage.title}</h3>{passage.uri && <a href={passage.uri} target="_blank" rel="noreferrer"><ExternalLink size={13} /> source</a>}</div>
                    <p>{passage.content}</p>
                    <small><FileSearch size={12} /> {passage.source}</small>
                  </div>
                </article>
              ))}
            </div>
          ) : <div className="source-empty">No passages were returned for this question.</div>}
          <div className="section-heading citation-heading"><div><div className="section-title">Source citations</div></div></div>
          <SourceList sources={mutation.data.sources || []} />
        </Card>
      )}

      <Card className="compliance-review-card">
        <div className="section-heading">
          <div><div className="section-title">Latest Compliance agent response</div><div className="section-subtitle">Returned by the most recent completed chat workflow</div></div>
          <span className="principle-icon principle-violet"><ShieldCheck size={17} /></span>
        </div>
        {latest.data?.compliance_agent_response ? (
          <>
            <div className="agent-prose compliance-prose">{latest.data.compliance_agent_response}</div>
            <SourceList sources={latest.data.sources || []} />
          </>
        ) : (
          <div className="source-empty">No in-session chat output is available. Run an audit to receive a Compliance response with its cited guidance.</div>
        )}
      </Card>
    </motion.div>
  );
}
