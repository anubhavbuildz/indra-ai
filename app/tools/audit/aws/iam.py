"""IAMAudit AWS audit checks."""

from typing import Any

from botocore.exceptions import ClientError


class IAMAuditMixin:
    def audit_iam(self) -> list[dict[str, Any]]:
        findings = []
        iam = self.session.client("iam")
        try:
            summary = iam.get_account_summary().get("SummaryMap", {})
            if summary.get("AccountAccessKeysPresent", 0) > 0:
                findings.append(
                    {
                        "service": "iam",
                        "region": "global",
                        "resource": "AWS Root Account",
                        "severity": "CRITICAL",
                        "title": "Root Account Access Keys Active",
                        "issue": "Active access keys exist for the root account.",
                        "remediation": "Delete root access keys immediately and enforce IAM roles.",
                    }
                )
        except ClientError as e:
            findings.append({"service": "iam", "region": "global", "error": str(e)})

        return findings
