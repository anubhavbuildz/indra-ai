# Security notes and V1 boundaries

- Do not store credentials in assessments, operations, prompts, source documents,
  or logs. AWS credentials remain in the standard credential chain; NVIDIA
  credentials remain in server configuration.
- The login endpoint supports one environment-configured account and issues a
  30-minute HS256 JWT. Configure `AUTH_USERNAME`, `AUTH_PASSWORD`, and a unique
  `JWT_SECRET_KEY` of at least 32 bytes. Do not commit these secrets.
- JWTs are not currently required or validated by existing application routes.
  There is no authorization, tenant isolation, or complete audit system.
  Assessment IDs are not authorization tokens.
- Chat runs only the allowlisted read-only Boto3 checks for S3, IAM, EC2/EBS,
  VPC, RDS, CloudTrail, and GuardDuty. S3 and IAM are global checks; EC2/EBS,
  VPC, RDS, and GuardDuty use `AWS_REGION`; CloudTrail discovers enabled
  regions. The Cloud model cannot choose arbitrary AWS operations, arguments,
  or regions. It requires suitable AWS read permissions and
  configured inference. Results are point-in-time decision support, not a
  certification or guarantee of security.
- The optional AWS identity endpoint performs a read-only STS caller identity
  lookup using the standard credential chain. It does not inspect IAM policies
  or mutate cloud resources.
- NVIDIA inference defaults to the Nebius Token Factory endpoint and
  `nvidia/Nemotron-3_5-Lightning`. A valid `NVIDIA_API_KEY` is required for
  model calls; never commit or log the key.
- Keep AWS and NVIDIA credentials out of issues, pull requests, test fixtures,
  logs, and source control. `.env.example` contains placeholders only.
- Retrieval/RAG is not currently included; review the design and security
  boundaries before adding document ingestion or index loading.
