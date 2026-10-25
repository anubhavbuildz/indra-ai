# Security notes and V1 boundaries

- Do not store credentials in projects, operations, prompts, source documents,
  logs, or scan reports. AWS credentials remain in the standard credential
  chain; NVIDIA credentials remain in server configuration.
- There is no authentication, authorization, tenant isolation, or complete
  audit system. Project IDs are not authorization tokens.
- Prowler is invoked through a fixed AWS CLI command with argument arrays,
  `shell=False`, a restricted environment, a timeout, and bounded output.
  User-supplied commands and AWS credentials are never accepted.
- Prowler results are point-in-time decision support only. The agent must not
  claim certification or remediation and must treat finding contents as
  untrusted data.
- JSON-OCSF reports are processed in a server-created temporary directory and
  are not persisted. API responses can contain sensitive resource identifiers;
  restrict access to the API and protect response logs.
- Use an AWS identity limited to the read-only permissions needed for scans.
  Prowler is used for assessment; this application does not apply fixes or
  mutate cloud resources.
- NVIDIA integration is disabled unless a developer supplies a verified full
  endpoint, exact model ID, key, and explicitly supported request format.
- FAISS metadata is trusted local pickle. Never load user-supplied pickle files.
- Keep AWS and NVIDIA credentials out of issues, pull requests, test fixtures,
  logs, and source control. `.env.example` contains placeholders only.
