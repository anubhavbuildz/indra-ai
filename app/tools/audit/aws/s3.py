"""S3Audit AWS audit checks."""

import json
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from app.tools.audit.aws.common import (
    collect_pages as _collect_pages,
)
from app.tools.audit.aws.common import (
    error_finding as _error_finding,
)
from app.tools.audit.aws.common import (
    finding as _finding,
)
from app.tools.audit.aws.common import (
    is_error as _is_error,
)


class S3AuditMixin:
    def audit_s3(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        s3 = self.session.client("s3")
        try:
            buckets = _collect_pages(s3, "list_buckets", "Buckets")
        except (BotoCoreError, ClientError) as exc:
            return [_error_finding("s3", "global", "s3.list_buckets", exc)]

        for b in buckets:
            name = b["Name"]
            bucket_region = "global"
            try:
                location = s3.get_bucket_location(Bucket=name).get("LocationConstraint")
                bucket_region = location or "us-east-1"
            except (BotoCoreError, ClientError) as exc:
                findings.append(_error_finding("s3", bucket_region, "s3.bucket_region", exc))

            try:
                pab = s3.get_public_access_block(Bucket=name)
                cfg = pab.get("PublicAccessBlockConfiguration", {})
                is_secure = all(
                    [
                        cfg.get("BlockPublicAcls", False),
                        cfg.get("IgnorePublicAcls", False),
                        cfg.get("BlockPublicPolicy", False),
                        cfg.get("RestrictPublicBuckets", False),
                    ]
                )
                if not is_secure:
                    findings.append(
                        _finding(
                            "s3",
                            bucket_region,
                            name,
                            "s3.public_access_block",
                            "HIGH",
                            "S3 Public Access Block Disabled",
                            "Bucket does not enforce all public access block protections.",
                            f"Enable all four Public Access Block settings on bucket '{name}'.",
                            settings=cfg,
                        )
                    )
            except ClientError as exc:
                if _is_error(exc, "NoSuchPublicAccessBlockConfiguration"):
                    findings.append(
                        _finding(
                            "s3",
                            bucket_region,
                            name,
                            "s3.public_access_block",
                            "HIGH",
                            "S3 Public Access Block Disabled",
                            "Bucket has no bucket-level public access block configuration.",
                            f"Enable all four Public Access Block settings on bucket '{name}'.",
                        )
                    )
                else:
                    findings.append(
                        _error_finding("s3", bucket_region, "s3.public_access_block", exc)
                    )
            except BotoCoreError as exc:
                findings.append(_error_finding("s3", bucket_region, "s3.public_access_block", exc))

            try:
                s3.get_bucket_encryption(Bucket=name)
            except ClientError as exc:
                if _is_error(exc, "ServerSideEncryptionConfigurationNotFoundError"):
                    findings.append(
                        _finding(
                            "s3",
                            bucket_region,
                            name,
                            "s3.default_encryption",
                            "LOW",
                            "S3 Explicit Default Encryption Not Configured",
                            "No explicit bucket encryption configuration was returned; Amazon S3 "
                            "automatically encrypts new object uploads with SSE-S3 by default.",
                            f"Configure an explicit SSE-S3 or KMS default if required by policy "
                            f"for bucket '{name}'.",
                        )
                    )
                else:
                    findings.append(
                        _error_finding("s3", bucket_region, "s3.default_encryption", exc)
                    )
            except BotoCoreError as exc:
                findings.append(_error_finding("s3", bucket_region, "s3.default_encryption", exc))

            try:
                policy_status = s3.get_bucket_policy_status(Bucket=name).get("PolicyStatus", {})
                if policy_status.get("IsPublic", False):
                    findings.append(
                        _finding(
                            "s3",
                            bucket_region,
                            name,
                            "s3.public_bucket_policy",
                            "CRITICAL",
                            "S3 Bucket Policy Is Public",
                            "AWS classifies the bucket policy as public.",
                            f"Review and restrict the bucket policy for '{name}'.",
                            policy_status=policy_status,
                        )
                    )
            except ClientError as exc:
                if not _is_error(exc, "NoSuchBucketPolicy"):
                    findings.append(
                        _error_finding("s3", bucket_region, "s3.public_bucket_policy", exc)
                    )
            except BotoCoreError as exc:
                findings.append(_error_finding("s3", bucket_region, "s3.public_bucket_policy", exc))

            try:
                acl = s3.get_bucket_acl(Bucket=name)
                public_grants = [
                    grant
                    for grant in acl.get("Grants", [])
                    if grant.get("Grantee", {})
                    .get("URI", "")
                    .endswith(("/AllUsers", "/AuthenticatedUsers"))
                ]
                if public_grants:
                    findings.append(
                        _finding(
                            "s3",
                            bucket_region,
                            name,
                            "s3.public_bucket_acl",
                            "HIGH",
                            "S3 Bucket ACL Grants Broad Access",
                            "Bucket ACL grants access to all users or all authenticated AWS users.",
                            f"Remove public or authenticated-user ACL grants from '{name}'.",
                            grants=public_grants,
                        )
                    )
            except (BotoCoreError, ClientError) as exc:
                findings.append(_error_finding("s3", bucket_region, "s3.public_bucket_acl", exc))

            try:
                versioning = s3.get_bucket_versioning(Bucket=name)
                if versioning.get("Status") != "Enabled":
                    findings.append(
                        _finding(
                            "s3",
                            bucket_region,
                            name,
                            "s3.versioning",
                            "MEDIUM",
                            "S3 Bucket Versioning Disabled",
                            "Bucket versioning is not enabled.",
                            f"Enable versioning on bucket '{name}'.",
                            status=versioning.get("Status", "Disabled"),
                        )
                    )
            except (BotoCoreError, ClientError) as exc:
                findings.append(_error_finding("s3", bucket_region, "s3.versioning", exc))

            try:
                policy_response = s3.get_bucket_policy(Bucket=name)
                policy = json.loads(policy_response.get("Policy", "{}"))
                statements = policy.get("Statement", [])
                if isinstance(statements, dict):
                    statements = [statements]
                denies_insecure_transport = any(
                    statement.get("Effect") == "Deny"
                    and statement.get("Principal") == "*"
                    and statement.get("Condition", {}).get("Bool", {}).get("aws:SecureTransport")
                    in (False, "false")
                    for statement in statements
                    if isinstance(statement, dict)
                )
                if not denies_insecure_transport:
                    findings.append(
                        _finding(
                            "s3",
                            bucket_region,
                            name,
                            "s3.tls_only",
                            "MEDIUM",
                            "S3 Bucket Does Not Enforce TLS",
                            "No bucket policy deny for insecure transport was found.",
                            "Add a bucket policy that denies requests when "
                            "aws:SecureTransport is false.",
                        )
                    )
            except ClientError as exc:
                if _is_error(exc, "NoSuchBucketPolicy"):
                    findings.append(
                        _finding(
                            "s3",
                            bucket_region,
                            name,
                            "s3.tls_only",
                            "MEDIUM",
                            "S3 Bucket Does Not Enforce TLS",
                            "Bucket has no policy enforcing secure transport.",
                            "Add a bucket policy that denies requests when "
                            "aws:SecureTransport is false.",
                        )
                    )
                else:
                    findings.append(_error_finding("s3", bucket_region, "s3.tls_only", exc))
            except (BotoCoreError, json.JSONDecodeError, TypeError, AttributeError) as exc:
                findings.append(_error_finding("s3", bucket_region, "s3.tls_only", exc))

            try:
                logging = s3.get_bucket_logging(Bucket=name).get("LoggingEnabled")
                if not logging:
                    findings.append(
                        _finding(
                            "s3",
                            bucket_region,
                            name,
                            "s3.access_logging",
                            "LOW",
                            "S3 Server Access Logging Disabled",
                            "Bucket server access logging is not enabled.",
                            f"Enable server access logging for bucket '{name}'.",
                        )
                    )
            except (BotoCoreError, ClientError) as exc:
                findings.append(_error_finding("s3", bucket_region, "s3.access_logging", exc))

        return findings
