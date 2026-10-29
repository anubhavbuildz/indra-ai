# AWS CLI and identity setup

Complete this setup before installing or running Indra-AI if you plan to use its
AWS audit workflow. Indra-AI's backend uses Boto3's standard AWS credential
chain. The AWS CLI is useful for creating and validating a local named
credential profile; it is not itself required by the running backend when
credentials are provided through another supported mechanism, such as a
workload identity.

## 1. Install and verify AWS CLI v2

Install AWS CLI v2 using the instructions for your operating system in the
[official AWS CLI installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Then verify that it is available:

```bash
aws --version
```

The output should identify AWS CLI version 2. If the command is not found,
finish installing the CLI and open a new terminal before continuing.

## 2. Use a non-root AWS identity

**Do not use the AWS account root user for Indra-AI or day-to-day AWS work.** Do
not create root access keys. Keep root credentials protected for account-level
administration and recovery only.

Prefer an individual identity managed through **AWS IAM Identity Center**.
If you administer the AWS organization, create or connect a user in IAM
Identity Center, create a permission set with only the required read
permissions, and assign that user or group to the target AWS account with
that permission set. Otherwise, ask your AWS administrator to provision this
identity and assignment. For deployments, prefer a narrowly scoped workload
role or the platform's workload identity rather than a developer's personal
credentials.

Indra-AI's AWS audit tools perform read-only checks across selected services,
including S3, IAM, EC2/EBS, VPC, RDS, CloudTrail, and GuardDuty. An identity
with only `sts:GetCallerIdentity` can verify its caller identity but cannot
run those audits. Grant only the specific read actions required for the
checks you intend to run; avoid broad administrator permissions. Review
permissions with your AWS administrator before using a profile.

## 3. Configure and verify a named profile

For an IAM Identity Center profile, use the interactive CLI setup:

```bash
aws configure sso --profile indra-readonly
aws sso login --profile indra-readonly
```

Follow the prompts using your organization's approved SSO start URL, region,
account, and permission set. Do not put credentials in the command line or
check them into source control.

Verify which identity the profile resolves to:

```bash
aws sts get-caller-identity --profile indra-readonly
```

Confirm the returned account and ARN are the expected non-root identity. If
the identity is not correct, stop and ask your administrator to fix the
profile or permission assignment before using Indra-AI.

## 4. Make the profile available to the backend

In the terminal used to start the backend, select the profile:

```bash
export AWS_PROFILE=indra-readonly
```

On PowerShell, use:

```powershell
$env:AWS_PROFILE = "indra-readonly"
```

Set `AWS_REGION` in the backend `.env` file to the region appropriate for
your audit. Keep AWS credentials out of `.env`, frontend environment
variables, request bodies, logs, and source control. The backend obtains
credentials through the AWS SDK credential chain.

The application's `GET /api/v1/aws/identity` endpoint performs a read-only
STS identity lookup. It confirms the identity available to the backend, but
does not validate all permissions needed by the audit tools.

## 5. AWS credentials with Docker Compose

> **Docker Deployment — Under Development**
>
> The Docker-based deployment version of Indraa is currently under active development and testing. Docker deployment is not yet considered production-ready. The standard installation and deployment method remains available and operational. Docker support will be finalized after testing and validation.

`compose.yml` runs the backend and a built React frontend. The frontend's
Nginx proxy forwards API requests to the backend over Docker's internal network.
Open `http://localhost:8080`; the backend port is not published to the host.

The backend mounts your host AWS directory **read-only** at
`/home/indra/.aws` and selects `AWS_PROFILE` (default `indra-readonly`). Boto3
reads the mounted configuration, credentials, and any existing SSO cache.
Credentials are not copied into an image or exposed to the frontend.
AWS documents the [shared configuration file locations](https://docs.aws.amazon.com/sdkref/latest/guide/file-location.html)
and [named profile format](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

First configure and authenticate your read-only profile on the host, as above.
For IAM Identity Center, run:

```bash
aws sso login --profile indra-readonly
```

From the repository root, configure application login/inference settings in the
ignored `.env` file. Copy `.env.example` only if `.env` does not already exist.
Never add AWS access keys to that file or to Vite variables. Then, on Linux or
macOS:

```bash
export AWS_PROFILE=indra-readonly
export LOCAL_UID="$(id -u)"
export LOCAL_GID="$(id -g)"
mkdir -p data/compose .cache/indra/huggingface

docker compose -f compose.yml config --quiet
docker compose -f compose.yml up --build -d --wait
```

The matching host UID/GID lets the backend read AWS files with restrictive
permissions and write its data/cache directories. Do not make credential files
world-readable to work around a permission error. On Windows, use WSL and these
commands, or set `AWS_CONFIG_DIR` to the absolute Windows AWS-directory path
available to Docker Desktop. The default source is `${HOME}/.aws`.

If credentials are in a dedicated directory instead:

```bash
export AWS_CONFIG_DIR=/absolute/path/to/indraa-aws
```

The mount exposes all files in the chosen directory to the backend. Prefer a
dedicated AWS directory when you need to isolate this app from other profiles.
Profiles using `credential_process` also require that helper executable inside
the image; mounting configuration alone does not install it. SSO refresh can
require writes, so refresh/login on the host and restart the backend after
renewing an expired session:

```bash
aws sso login --profile indra-readonly
docker compose -f compose.yml restart backend
```

A read-only filesystem mount prevents changes to the host files. **AWS IAM
permissions determine which AWS API operations the credentials allow.** Use
an approved profile with only the required read permissions.

Sign in through the frontend and use Settings → AWS identity to verify the
backend identity. This performs a real STS read; submitting an audit makes real
AWS read requests and configured inference calls. The real app Compose file
is separate from the synthetic, credential-free `compose.qa.yml` test setup.

Configuration and persistence:

- `.env` supplies backend application settings, including login credentials,
  the JWT signing key, and the inference key, at runtime. It is never built into
  either image. Avoid printing `docker compose config` without `--quiet`, as it
  can display resolved environment secrets.
- `data/compose/` stores the container's SQLite database separately from the
  development database; `.cache/indra/huggingface/` retains embedding downloads.
- `faiss_store/` is mounted read-only and must contain the matching index and
  trusted metadata. The first retrieval may download the configured CPU model.
- The frontend build uses `VITE_API_BASE_URL=/` for the same-origin proxy. If
  you previously saved a backend URL on this browser origin, clear it in Settings
  or run `localStorage.removeItem("indraa.apiBaseUrl")` in the browser console.
- `FRONTEND_PORT` changes host port 8080. `FRONTEND_BIND_ADDRESS` defaults to
  `127.0.0.1`; use a configured HTTPS reverse proxy for remote access.

Inspect and stop the local stack without deleting persistent files:

```bash
docker compose -f compose.yml ps
docker compose -f compose.yml logs --tail=100 backend frontend
docker compose -f compose.yml down
```

Docker runtime verification was unavailable on the implementation host. The
configuration can be validated there structurally, but image builds, container
health and credential permissions still need verification on a Docker host.

## Before installing Indra-AI

- [ ] `aws --version` reports AWS CLI v2.
- [ ] You have an approved non-root identity; do not use root credentials.
- [ ] The named profile (or deployment workload identity) resolves to the
      expected AWS account and identity.
- [ ] The identity has only the required read permissions for the checks you
      intend to run.
- [ ] AWS credentials are not being added to project files or frontend
      configuration.

The backend can start without AWS credentials, but AWS identity checks and
AWS audit workflows require valid credentials. See the [project README](./README.md)
for installation and startup steps, and the [security notes](./design/security.md)
for the application's AWS boundaries.

## IAM user authentication for the hackathon MVP

Use this alternative when an administrator authorizes IAM user credentials for
local MVP testing. The Identity Center and workload-role recommendations above
remain the preferred production approach.

1. Ask an AWS administrator to open **IAM → Users → Create user**, create a user
   named `indra` (or an approved username), and attach the AWS-managed
   `SecurityAudit` and `ViewOnlyAccess` policies. These are broad read-only audit
   baselines, not a guarantee that every assessment API is authorized; review
   their scope and any missing read permissions with the administrator.
2. Read-only audit permissions do not automatically allow creating access keys:
   creating credentials is a write operation. Request `iam:CreateAccessKey`
   permission from the administrator. **`iam:CreateAccessKey` is an IAM permission,
   not an AWS-managed policy name.** A user cannot grant this permission to themself
   using read-only access.
3. Have the administrator open the user's **Permissions → Add permissions →
   Create inline policy**, select the JSON editor, and add the illustrative policy
   below. Replace `<AWS_ACCOUNT_ID>` and `<IAM_USERNAME>` with the actual account
   and username. If the user has an IAM path, use their complete user ARN,
   including that path. This policy permits creation and listing only for that
   user's own IAM identity; it does not grant key rotation or deletion actions.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ManageOwnAccessKeys",
      "Effect": "Allow",
      "Action": [
        "iam:CreateAccessKey",
        "iam:ListAccessKeys"
      ],
      "Resource": "arn:aws:iam::<AWS_ACCOUNT_ID>:user/<IAM_USERNAME>"
    }
  ]
}
```

An explicit deny, permissions boundary, or organization policy can still block
creation. Ask the administrator to resolve those restrictions rather than
broadening permissions yourself. Console navigation can require additional read
permissions; the example is narrowly scoped to the access-key operations.

4. Using an authorized console session, open **IAM → Users → indra → Security
   credentials → Access keys → Create access key**. Select the appropriate use
   case and follow the prompts. Save the access key ID and secret access key
   securely; the secret is displayed only at creation. Never use root access keys.
5. Configure the named CLI profile interactively on the backend host:

```bash
aws configure --profile indra-audit
```

Enter the authorized access key ID and secret at the prompts, choose the audit
region (for example `us-east-1`), and choose `json` output. The CLI stores these
long-term credentials in the host's shared credentials file; restrict file access
and use an approved secrets store for secure retention. Never commit credentials
to GitHub or expose them in frontend JavaScript. Follow the credential-handling
rules in sections 3 and 4 above.

6. Verify the expected account and IAM user, then test a read-only regional API:

```bash
aws sts get-caller-identity \
  --profile indra-audit

aws ec2 describe-instances \
  --region us-east-1 \
  --profile indra-audit
```

Identity verification does not establish audit authorization. A successful EC2
response with no instances is valid, but only covers that account and region.
IAM users are global within an AWS account; EC2 and many other AWS services are
regional. Repeat relevant read-only checks in the intended audit regions.
Select `indra-audit` as `AWS_PROFILE` in the backend terminal using the method in
section 4; no credentials should be sent to the application API.

AWS references: [access-key permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-keys_required-permissions.html),
[managing access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html),
[CLI configure](https://docs.aws.amazon.com/cli/latest/reference/configure/),
[caller identity](https://docs.aws.amazon.com/cli/latest/reference/sts/get-caller-identity.html),
and [EC2 describe-instances](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instances.html).

## STS AssumeRole prerequisites and credential flow

The backend uses `boto3.Session` and the standard credential chain, so it can
consume an AWS role profile configured outside the application. There is no
separate application-level AssumeRole onboarding flow documented or implemented
in this repository.

- **Initial authentication:** the SDK needs an authenticated source identity
  before calling `sts:AssumeRole`, such as an approved source profile or workload
  identity. A role ARN alone is not authentication. An IAM user's own-key policy
  above does not grant permission to assume a role.
- **Trust and authorization:** the target role's trust policy must trust the
  intended source principal and satisfy any required conditions (such as an
  external ID or MFA). For cross-account access, the source identity also needs
  `sts:AssumeRole` authorization scoped to the target role ARN. In the same
  account, a trust policy naming the principal directly can grant access without
  a separate identity-policy allow, subject to applicable policy evaluation.
- **Temporary credentials:** a configured SDK role profile specifies `role_arn`
  and its `source_profile` or supported `credential_source`. Boto3 obtains an
  access key ID, secret access key, session token, and expiration from STS and
  refreshes assumed-role credentials through its supported provider. Manually
  supplied temporary credentials require all three credential values and must
  be renewed when they expire. Prefer temporary credentials for production.
- **Assessment permissions:** Boto3 service clients use the resolved credentials
  for the existing read-only assessment operations. The target role's permissions
  policy must authorize the audit reads; trust and `sts:AssumeRole` permission
  alone do not provide them. Use administrator-approved read-only policies for
  MVP testing and scoped audit policies for production. Session policies and
  other policy controls can further restrict effective access.

See AWS's [AssumeRole API](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html)
and [Boto3 role credential configuration](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#assume-role-provider).

## Incomplete assessment reporting

Report unauthorized or incomplete audit checks as `NOT_ASSESSED`, with the
missing permission, affected service, region, or other reason where known.
Do not interpret denied access or an unfinished check as a passing security
result. This is reporting guidance, not a claim that the current backend
uniformly implements this status; review assessment coverage before relying on
results. Existing credential safety requirements above apply to both IAM user
and temporary role credentials.
