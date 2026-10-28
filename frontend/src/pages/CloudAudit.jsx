import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { createPortal } from "react-dom";
import { ArrowRight, Check, Cloud, Globe2, Info, LoaderCircle, LockKeyhole, Play, ShieldCheck } from "lucide-react";
import { AgentWorkflow } from "../components/agents/AgentWorkflow";
import { Button, Card, ErrorState, PageHeading } from "../components/ui/Primitives";
import { useChatMutation, useAwsIdentity } from "../hooks/useApi";
import { getErrorMessage } from "../lib/utils";

const services = [
  ["s3", "Amazon S3", "Bucket access, encryption, versioning"],
  ["iam", "AWS IAM", "Root account access keys"],
  ["ec2", "EC2 & EBS", "Network exposure, volumes, snapshots"],
  ["vpc", "Amazon VPC", "Default VPCs and flow logs"],
  ["rds", "Amazon RDS", "Exposure, encryption, backups"],
  ["cloudtrail", "CloudTrail", "Coverage, logging, log protection"],
  ["guardduty", "GuardDuty", "Detector presence and status"],
];

export default function CloudAudit() {
  const [selected, setSelected] = useState(services.map(([id]) => id));
  const [acceptedRegion, setAcceptedRegion] = useState("");
  const [regionNote, setRegionNote] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const queryClient = useQueryClient();
  const mutation = useChatMutation();
  const progressMessage = useRef(null);
  const identity = useAwsIdentity();
  const configuredRegion = identity.data?.region || "";
  const result = mutation.data;

  useEffect(() => {
    const appRoot = document.getElementById("root");
    if (!appRoot || !mutation.isPending) return undefined;

    const wasInert = appRoot.inert;
    const previouslyFocused = document.activeElement;
    appRoot.inert = true;
    progressMessage.current?.focus();

    return () => {
      appRoot.inert = wasInert;
      if (previouslyFocused instanceof HTMLElement && previouslyFocused.isConnected) {
        previouslyFocused.focus();
      }
    };
  }, [mutation.isPending]);

  function toggleService(id) {
    setSelected((current) =>
      current.includes(id) ? current.filter((value) => value !== id) : [...current, id],
    );
  }

  async function submit(event) {
    event.preventDefault();
    setErrorMessage("");
    if (!selected.length) {
      setErrorMessage("Select at least one AWS service for the audit request.");
      return;
    }
    if (!configuredRegion || acceptedRegion !== configuredRegion) {
      setErrorMessage("Confirm the backend-configured AWS region before running the audit.");
      return;
    }
    const selectedNames = services.filter(([id]) => selected.includes(id)).map(([, name]) => name);
    const prompt = [
      `Perform a read-only security audit focused on these AWS services: ${selectedNames.join(", ")}.`,
      "Report relevant findings, severity, affected resources, evidence, and remediation guidance.",
      regionNote.trim() ? `Additional scope requested: ${regionNote.trim()}` : "",
    ]
      .filter(Boolean)
      .join("\n");
    try {
      const response = await mutation.mutateAsync({ message: prompt, history: [] });
      queryClient.setQueryData(["latest-audit"], response);
      queryClient.invalidateQueries({ queryKey: ["assessments"] });
      queryClient.invalidateQueries({ queryKey: ["aws-identity"] });
    } catch (error) {
      if (error.status === 401) {
        window.dispatchEvent(new Event("indraa:session-expired"));
      }
      setErrorMessage(getErrorMessage(error));
    }
  }

  return (
    <motion.div className="page-stack" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <PageHeading
        eyebrow="READ-ONLY AWS ASSESSMENT"
        title="Cloud audit"
        description="Configure the audit request and review the real results returned by the backend."
        action={<div className="api-pill"><span className="status-dot" /> SECURE API CONNECTION</div>}
      />
      <div className="audit-layout">
        <Card className="audit-config-card">
          <div className="section-heading">
            <div>
              <div className="section-title">Audit configuration</div>
              <div className="section-subtitle">The model selects from backend-approved read-only checks.</div>
            </div>
            <span className="config-icon"><Cloud size={18} /></span>
          </div>
          <form onSubmit={submit}>
            <div className="config-block">
              <div className="config-label-row">
                <span className="config-label">AWS SERVICES</span>
                <span className="config-meta">{selected.length} of {services.length} selected</span>
              </div>
              <div className="service-grid">
                {services.map(([id, name, description]) => {
                  const checked = selected.includes(id);
                  return (
                    <button
                      className={`service-select ${checked ? "service-selected" : ""}`}
                      key={id}
                      type="button"
                      onClick={() => toggleService(id)}
                      aria-pressed={checked}
                    >
                      <span className="service-check">{checked && <Check size={13} />}</span>
                      <span className="service-select-copy"><strong>{name}</strong><small>{description}</small></span>
                    </button>
                  );
                })}
              </div>
              <div className="service-help"><Info size={14} /> This selection guides the request; the Cloud agent chooses relevant checks from the server allowlist.</div>
            </div>

            <div className="config-block">
              <div className="config-label-row">
                <span className="config-label">AWS REGION</span>
                <span className="config-meta">SET BY BACKEND</span>
              </div>
              <div className="region-readonly">
                <Globe2 size={16} />
                <span>{configuredRegion || (identity.isLoading ? "Loading configured region…" : "Region unavailable")}</span>
                <LockKeyhole size={13} className="region-lock" />
              </div>
              {configuredRegion ? (
                <button
                  className={`region-accept-button ${acceptedRegion === configuredRegion ? "region-accepted" : ""}`}
                  type="button"
                  aria-pressed={acceptedRegion === configuredRegion}
                  onClick={() => setAcceptedRegion(acceptedRegion === configuredRegion ? "" : configuredRegion)}
                >
                  {acceptedRegion === configuredRegion ? <Check size={15} /> : <Globe2 size={15} />}
                  {acceptedRegion === configuredRegion
                    ? `Region ${configuredRegion} accepted`
                    : `Accept ${configuredRegion} for this audit`}
                </button>
              ) : (
                <div className="region-unavailable" role={identity.isError ? "alert" : undefined}>
                  {identity.isError
                    ? `Could not load the configured AWS region: ${getErrorMessage(identity.error)}`
                    : "Waiting for the backend-configured AWS region."}
                  {identity.isError && (
                    <button type="button" onClick={() => identity.refetch()} disabled={identity.isFetching}>
                      {identity.isFetching ? "Retrying…" : "Retry"}
                    </button>
                  )}
                </div>
              )}
              <div className="service-help">The backend uses its configured AWS_REGION; the API does not accept a per-request region override.</div>
            </div>
            <label className="config-block region-notes-label">
              <span className="config-label">ADDITIONAL CONTEXT <small>OPTIONAL</small></span>
              <textarea
                rows="3"
                value={regionNote}
                onChange={(event) => setRegionNote(event.target.value)}
                maxLength={1500}
                placeholder="Describe what you want the audit to prioritize…"
              />
            </label>
            {errorMessage && <div className="form-error" role="alert">{errorMessage}</div>}
            <div className="audit-submit-row">
              <span><ShieldCheck size={14} /> Read-only · No AWS changes</span>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? <><LoaderCircle className="spin" size={15} /> Running audit</> : <><Play size={14} fill="currentColor" /> Run audit</>}
              </Button>
            </div>
            {mutation.isPending && (
              <div className="audit-progress" role="status" aria-live="polite">
                <span>Audit in progress — running the selected checks and reviewing results.</span>
                <div
                  className="audit-progress-track"
                  role="progressbar"
                  aria-label="Audit progress"
                  aria-valuetext="Audit in progress"
                >
                  <span />
                </div>
              </div>
            )}
          </form>
        </Card>
      </div>

      <AgentWorkflow result={result} running={mutation.isPending} />
      {mutation.isError && <ErrorState error={{ message: getErrorMessage(mutation.error) }} />}
      {result && (
        <div className="audit-complete-banner">
          <span><Check size={14} /></span>
          Audit complete · Assessment <code>{result.assessment_id}</code>
          <a href={`/reports/${result.assessment_id}`}><ArrowRight size={14} /> View assessment</a>
        </div>
      )}
      {mutation.isPending && createPortal(
        <div className="audit-running-overlay">
          <div
            ref={progressMessage}
            className="audit-running-dialog"
            role="status"
            aria-live="polite"
            aria-busy="true"
            tabIndex={-1}
          >
            <LoaderCircle className="spin" size={24} />
            <h2>Audit is running</h2>
            <p>Running the selected checks and preparing the review. Please wait for the response.</p>
            <div className="audit-progress-track" aria-hidden="true"><span /></div>
          </div>
        </div>,
        document.body,
      )}
    </motion.div>
  );
}
