import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowDown,
  Check,
  ChevronDown,
  Cloud,
  Database,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { MarkdownView } from "../reports/MarkdownView";
import { Badge, Card } from "../ui/Primitives";

const agents = [
  {
    key: "cloud_agent_response",
    name: "Cloud Agent",
    subtitle: "Infrastructure audit",
    icon: Cloud,
    color: "blue",
    description: "Selected and ran allowlisted AWS checks.",
  },
  {
    key: "compliance_agent_response",
    name: "Compliance Agent",
    subtitle: "Guidance synthesis",
    icon: Database,
    color: "violet",
    description: "Reviewed the report with retrieved local guidance.",
  },
  {
    key: "senior_agent_response",
    name: "Senior Agent",
    subtitle: "Evidence verification",
    icon: ShieldCheck,
    color: "green",
    description: "Reviewed the report and Compliance summary.",
  },
];

function outputText(key, value) {
  if (key === "cloud_agent_response") return JSON.stringify(value, null, 2);
  return value || "No output was returned.";
}

export function AgentWorkflow({ result, running = false, compact = false }) {
  const [expanded, setExpanded] = useState("cloud_agent_response");

  return (
    <div className={`agent-flow ${compact ? "agent-flow-compact" : ""}`}>
      <div className="agent-flow-heading">
        <div>
          <div className="eyebrow"><Sparkles size={13} /> LIVE AGENTIC SECURITY WORKFLOW</div>
          <h2>Three specialists. One evidence trail.</h2>
        </div>
        <Badge tone={running ? "running" : result ? "green" : "neutral"}>
          <span className={running ? "mini-spinner" : "status-dot"} />
          {running ? "Workflow running" : result ? "Response received" : "Awaiting audit"}
        </Badge>
      </div>
      {running && (
        <div className="workflow-notice">
          The backend processes agents sequentially and does not stream agent-level progress.
          Individual results will appear when the full response arrives.
        </div>
      )}
      <div className="agent-nodes">
        {agents.map((agent, index) => {
          const Icon = agent.icon;
          const value = result?.[agent.key];
          return (
            <div className="agent-node-wrap" key={agent.key}>
              <motion.div
                className={`agent-node agent-node-${agent.color} ${value ? "agent-node-done" : ""}`}
                animate={running ? { opacity: [0.72, 1, 0.72] } : { opacity: 1 }}
                transition={running ? { duration: 1.8, repeat: Infinity } : { duration: 0.35 }}
              >
                <div className="agent-node-icon"><Icon size={20} /></div>
                <div className="agent-node-name">{agent.name}</div>
                <div className="agent-node-subtitle">{agent.subtitle}</div>
                <div className="agent-node-state">
                  {value ? <><Check size={12} /> Response received</> : running ? "Awaiting response" : "Ready"}
                </div>
              </motion.div>
              {index < agents.length - 1 && (
                <div className="agent-connector">
                  <span />
                  <ArrowDown size={14} />
                </div>
              )}
            </div>
          );
        })}
      </div>
      {result ? (
        <div className="agent-output-list">
          {agents.map((agent) => {
            const open = expanded === agent.key;
            const value = result[agent.key];
            return (
              <Card className="agent-output" key={agent.key}>
                <button className="agent-output-trigger" onClick={() => setExpanded(open ? "" : agent.key)}>
                  <span className={`agent-output-dot dot-${agent.color}`} />
                  <span className="agent-output-title">{agent.name}</span>
                  <span className="agent-output-desc">{agent.description}</span>
                  <ChevronDown className={open ? "rotate-chevron" : ""} size={16} />
                </button>
                <AnimatePresence initial={false}>
                  {open && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="agent-output-content"
                    >
                      {agent.key === "cloud_agent_response" ? (
                        <pre>{outputText(agent.key, value)}</pre>
                      ) : (
                        <MarkdownView className="agent-prose" text={outputText(agent.key, value)} />
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </Card>
            );
          })}
        </div>
      ) : (
        <div className="agent-flow-empty">
          <span><Sparkles size={15} /></span>
          Submit a cloud audit to see each agent’s actual response.
        </div>
      )}
    </div>
  );
}
