# AWS CLI and identity setup

Complete this setup before installing or running Indra if you plan to use its
AWS audit workflow. Indra's backend uses Boto3's standard AWS credential
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

**Do not use the AWS account root user for Indra or day-to-day AWS work.** Do
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

Indra's AWS audit tools perform read-only checks across selected services,
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
profile or permission assignment before using Indra.

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

## Before installing Indra

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
