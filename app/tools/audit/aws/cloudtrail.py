"""CloudTrailAudit AWS audit checks."""

from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from app.tools.audit.aws.common import (
    error_finding as _error_finding,
)
from app.tools.audit.aws.common import (
    finding as _finding,
)
from app.tools.audit.aws.common import (
    is_error as _is_error,
)


class CloudTrailAuditMixin:
    def audit_cloudtrail(self) -> list[dict[str, Any]]:
        """Check all enabled regions for multi-region trails and protected delivery."""
        findings: list[dict[str, Any]] = []
        try:
            enabled_regions = [
                item["RegionName"]
                for item in self.session.client("ec2", region_name=self.primary_region)
                .describe_regions(
                    Filters=[
                        {
                            "Name": "opt-in-status",
                            "Values": ["opt-in-not-required", "opted-in"],
                        }
                    ]
                )
                .get("Regions", [])
            ]
        except (BotoCoreError, ClientError) as exc:
            return [_error_finding("cloudtrail", "global", "cloudtrail.region_discovery", exc)]

        trails_by_arn: dict[str, dict[str, Any]] = {}
        successful_regions: set[str] = set()
        for region in enabled_regions:
            try:
                trails = (
                    self.session.client("cloudtrail", region_name=region)
                    .describe_trails(includeShadowTrails=True)
                    .get("trailList", [])
                )
                successful_regions.add(region)
                for trail in trails:
                    trail_arn = trail.get("TrailARN")
                    if trail_arn:
                        trails_by_arn[trail_arn] = trail
            except (BotoCoreError, ClientError) as exc:
                findings.append(
                    _error_finding("cloudtrail", region, "cloudtrail.describe_trails", exc)
                )

        if (
            not trails_by_arn
            and successful_regions
            and len(successful_regions) == len(enabled_regions)
        ):
            findings.append(
                _finding(
                    "cloudtrail",
                    "global",
                    "AWS account",
                    "cloudtrail.multi_region_trail",
                    "HIGH",
                    "CloudTrail Trail Not Found",
                    "No CloudTrail trails were returned from the regions successfully checked.",
                    "Create and enable a multi-region CloudTrail trail.",
                )
            )
            return findings

        has_multi_region_trail = any(
            trail.get("IsMultiRegionTrail", False) for trail in trails_by_arn.values()
        )
        if trails_by_arn and not has_multi_region_trail:
            findings.append(
                _finding(
                    "cloudtrail",
                    "global",
                    "AWS account",
                    "cloudtrail.multi_region_trail",
                    "HIGH",
                    "CloudTrail Multi-Region Trail Missing",
                    "The discovered trails do not include a multi-region trail.",
                    "Configure and enable a multi-region CloudTrail trail.",
                )
            )

        for trail in trails_by_arn.values():
            trail_arn = trail["TrailARN"]
            trail_region = trail.get("HomeRegion", self.primary_region)
            trail_client = self.session.client("cloudtrail", region_name=trail_region)
            try:
                status = trail_client.get_trail_status(Name=trail_arn)
                if not status.get("IsLogging", False):
                    findings.append(
                        _finding(
                            "cloudtrail",
                            trail_region,
                            trail_arn,
                            "cloudtrail.logging",
                            "HIGH",
                            "CloudTrail Logging Disabled",
                            f"CloudTrail trail '{trail_arn}' is not currently logging.",
                            f"Enable logging for CloudTrail trail '{trail_arn}'.",
                        )
                    )
            except (BotoCoreError, ClientError) as exc:
                findings.append(
                    _error_finding("cloudtrail", trail_region, "cloudtrail.logging", exc)
                )

            if not trail.get("LogFileValidationEnabled", False):
                findings.append(
                    _finding(
                        "cloudtrail",
                        trail_region,
                        trail_arn,
                        "cloudtrail.log_file_validation",
                        "MEDIUM",
                        "CloudTrail Log File Validation Disabled",
                        f"Log file validation is not enabled for trail '{trail_arn}'.",
                        f"Enable log file validation for trail '{trail_arn}'.",
                    )
                )

            bucket_name = trail.get("S3BucketName")
            if not bucket_name:
                findings.append(
                    _error_finding(
                        "cloudtrail",
                        trail_region,
                        "cloudtrail.log_bucket",
                        ValueError("Trail has no configured S3 log bucket."),
                    )
                )
                continue
            s3 = self.session.client("s3")
            try:
                pab = s3.get_public_access_block(Bucket=bucket_name).get(
                    "PublicAccessBlockConfiguration", {}
                )
                if not all(
                    (
                        pab.get("BlockPublicAcls", False),
                        pab.get("IgnorePublicAcls", False),
                        pab.get("BlockPublicPolicy", False),
                        pab.get("RestrictPublicBuckets", False),
                    )
                ):
                    findings.append(
                        _finding(
                            "cloudtrail",
                            trail_region,
                            bucket_name,
                            "cloudtrail.log_bucket_public_access",
                            "HIGH",
                            "CloudTrail Log Bucket Public Access Block Incomplete",
                            f"CloudTrail log bucket '{bucket_name}' does not enforce all "
                            "public-access-block settings.",
                            f"Enable all four public-access-block settings on '{bucket_name}'.",
                            settings=pab,
                        )
                    )
            except (BotoCoreError, ClientError) as exc:
                findings.append(
                    _error_finding(
                        "cloudtrail", trail_region, "cloudtrail.log_bucket_public_access", exc
                    )
                )

            try:
                s3.get_bucket_encryption(Bucket=bucket_name)
            except ClientError as exc:
                if _is_error(
                    exc,
                    "ServerSideEncryptionConfigurationNotFoundError",
                    "NoSuchServerSideEncryptionConfiguration",
                ):
                    findings.append(
                        _finding(
                            "cloudtrail",
                            trail_region,
                            bucket_name,
                            "cloudtrail.log_bucket_encryption",
                            "LOW",
                            "CloudTrail Log Bucket Explicit Encryption Not Configured",
                            f"CloudTrail log bucket '{bucket_name}' has no explicit default "
                            "encryption configuration; Amazon S3 applies SSE-S3 to new object "
                            "uploads by default.",
                            f"Configure explicit default encryption for '{bucket_name}' if "
                            "required by policy.",
                        )
                    )
                else:
                    findings.append(
                        _error_finding(
                            "cloudtrail", trail_region, "cloudtrail.log_bucket_encryption", exc
                        )
                    )
            except BotoCoreError as exc:
                findings.append(
                    _error_finding(
                        "cloudtrail", trail_region, "cloudtrail.log_bucket_encryption", exc
                    )
                )

        if len(successful_regions) < len(enabled_regions):
            findings.append(
                _error_finding(
                    "cloudtrail",
                    "global",
                    "cloudtrail.region_coverage",
                    RuntimeError("CloudTrail could not be checked in every enabled region."),
                )
            )
        return findings
