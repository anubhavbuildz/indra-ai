"""VPCAudit AWS audit checks."""

from typing import Any

from botocore.exceptions import ClientError

from app.tools.audit.aws.common import (
    collect_pages as _collect_pages,
)


class VPCAuditMixin:
    def audit_vpc(self, region: str) -> list[dict[str, Any]]:
        findings = []
        ec2 = self.session.client("ec2", region_name=region)

        try:
            vpcs = _collect_pages(ec2, "describe_vpcs", "Vpcs")
            for vpc in vpcs:
                vpc_id = vpc["VpcId"]

                # 1. Default VPC Usage Check
                if vpc.get("IsDefault", False):
                    findings.append(
                        {
                            "service": "vpc",
                            "region": region,
                            "resource": vpc_id,
                            "severity": "LOW",
                            "title": "Default VPC In Use",
                            "issue": (
                                "Default VPC exists; production resources should be in a "
                                "custom, segmented VPC."
                            ),
                            "remediation": (
                                "Provision a non-default custom VPC with separate private and "
                                "public subnets."
                            ),
                        }
                    )

                # 2. VPC Flow Logs Enabled Check
                flow_logs = _collect_pages(
                    ec2,
                    "describe_flow_logs",
                    "FlowLogs",
                    Filters=[{"Name": "resource-id", "Values": [vpc_id]}],
                )

                if not flow_logs:
                    findings.append(
                        {
                            "service": "vpc",
                            "region": region,
                            "resource": vpc_id,
                            "severity": "MEDIUM",
                            "title": "VPC Flow Logs Disabled",
                            "issue": f"VPC '{vpc_id}' does not have traffic flow logs enabled.",
                            "remediation": (
                                f"Enable VPC Flow Logs on '{vpc_id}' publishing to CloudWatch "
                                "or S3."
                            ),
                        }
                    )
        except ClientError as e:
            findings.append({"service": "vpc", "region": region, "error": str(e)})

        return findings
