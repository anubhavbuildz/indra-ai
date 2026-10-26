"""AWS audit facade that keeps the existing AWSAuditor interface."""

from typing import Any

import boto3
from botocore.exceptions import ClientError

from app.tools.audit.aws.cloudtrail import CloudTrailAuditMixin
from app.tools.audit.aws.ec2 import EC2AuditMixin
from app.tools.audit.aws.guardduty import GuardDutyAuditMixin
from app.tools.audit.aws.iam import IAMAuditMixin
from app.tools.audit.aws.rds import RDSAuditMixin
from app.tools.audit.aws.s3 import S3AuditMixin
from app.tools.audit.aws.vpc import VPCAuditMixin


class AWSAuditor(
    S3AuditMixin,
    IAMAuditMixin,
    EC2AuditMixin,
    VPCAuditMixin,
    RDSAuditMixin,
    CloudTrailAuditMixin,
    GuardDutyAuditMixin,
):
    """Coordinate service-specific read-only AWS audit checks."""

    def __init__(self, primary_region: str = "us-east-1"):
        self.primary_region = primary_region
        self.session = boto3.Session(region_name=primary_region)

    def get_enabled_regions(self) -> list[str]:
        """Fetch all enabled regions for the AWS account."""
        try:
            ec2 = self.session.client("ec2", region_name=self.primary_region)
            regions = ec2.describe_regions(
                Filters=[{"Name": "opt-in-status", "Values": ["opt-in-not-required", "opted-in"]}]
            )
            return [r["RegionName"] for r in regions.get("Regions", [])]
        except ClientError:
            # Fallback to the primary region if permissions are restricted
            return [self.primary_region]

    def run_audit(self, regions: list[str] | None = None) -> dict[str, Any]:
        """Runs the audit across global services and specified or all enabled regions."""
        findings = []
        audited_services = ["s3", "iam", "cloudtrail"]

        # 1. Run global checks once
        findings.extend(self.audit_s3())
        findings.extend(self.audit_iam())
        findings.extend(self.audit_cloudtrail())

        # 2. Determine target regions
        target_regions = regions if regions else [self.primary_region]

        # 3. Run regional checks
        for reg in target_regions:
            findings.extend(self.audit_ec2(reg))
            findings.extend(self.audit_vpc(reg))
            findings.extend(self.audit_databases(reg))
            findings.extend(self.audit_guardduty(reg))
        audited_services.extend(["ec2", "vpc", "rds", "guardduty"])

        return {
            "audited_regions": target_regions,
            "audited_services": audited_services,
            "total_issues": len(findings),
            "critical_count": sum(1 for f in findings if f.get("severity") == "CRITICAL"),
            "high_count": sum(1 for f in findings if f.get("severity") == "HIGH"),
            "medium_count": sum(1 for f in findings if f.get("severity") == "MEDIUM"),
            "low_count": sum(1 for f in findings if f.get("severity") == "LOW"),
            "findings": findings,
        }
