# Security notes and V1 boundaries

- Do not store credentials in projects, operations, prompts, source documents,
  logs, or Terraform code. Credentials remain in local environment/configuration
  and the standard AWS credential chain.
- There is no authentication, authorization, tenant isolation, or complete
  audit system. Project IDs are not authorization tokens.
- Compliance findings and retrieved guidance are decision support only; they
  are not certification, legal advice, or a guarantee of security.
- NVIDIA integration is disabled unless a developer supplies a verified full
  endpoint, exact model ID, key, and explicitly supported request format.
- FAISS metadata is trusted local pickle. Never load user-supplied pickle files.
- Terraform execution uses server-created directories, fixed commands,
  argument arrays, timeouts, output limits, and `shell=False`. This is not a
  substitute for production isolation or approval. Only plan is supported;
  apply and destroy are disabled.
- Terraform state, caches, and plan files may contain secrets. Do not commit
  them. Review generated HCL before any use.
- Keep AWS and NVIDIA credentials out of issues, pull requests, test fixtures,
  logs, and source control. `.env.example` contains placeholders only.
