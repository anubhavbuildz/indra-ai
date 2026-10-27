import { motion } from "framer-motion";
import { ArrowRight, Bot, Cloud, Database, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { AgentWorkflow } from "../components/agents/AgentWorkflow";
import { Button, Card, EmptyState, PageHeading } from "../components/ui/Primitives";
import { useLatestAudit } from "../hooks/useApi";

export default function Agents() {
  const latest = useLatestAudit();
  return (
    <motion.div className="page-stack" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <PageHeading
        eyebrow="MULTI-AGENT REVIEW"
        title="AI agents"
        description="A sequential review path designed to keep observations, guidance, and verification distinct."
        action={<Link to="/audit"><Button variant="outline"><Bot size={15} /> New audit</Button></Link>}
      />
      <AgentWorkflow result={latest.data} />
      <div className="agent-principles-grid">
        <Card className="agent-principle">
          <span className="principle-icon principle-blue"><Cloud size={17} /></span>
          <div><strong>Cloud Agent</strong><p>Selects only backend-allowlisted AWS audit tools and returns a validated structured report.</p></div>
        </Card>
        <Card className="agent-principle">
          <span className="principle-icon principle-violet"><Database size={17} /></span>
          <div><strong>Compliance Agent</strong><p>Summarizes report evidence and the locally retrieved security guidance with source attribution.</p></div>
        </Card>
        <Card className="agent-principle">
          <span className="principle-icon principle-green"><ShieldCheck size={17} /></span>
          <div><strong>Senior Agent</strong><p>Reviews the report against the Compliance summary and flags unsupported claims and uncertainty.</p></div>
        </Card>
      </div>
      {!latest.data && (
        <Card className="agent-explainer-card">
          <EmptyState
            icon={Bot}
            title="No live agent output yet"
            description="Agent output is shown only after a real completed chat workflow. The backend does not stream per-agent status."
            action={<Link to="/audit"><Button>Run a cloud audit <ArrowRight size={15} /></Button></Link>}
          />
        </Card>
      )}
    </motion.div>
  );
}
