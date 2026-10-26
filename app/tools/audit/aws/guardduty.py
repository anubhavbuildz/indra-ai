"""GuardDutyAudit AWS audit checks."""

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


class GuardDutyAuditMixin:
    def audit_guardduty(self, region: str) -> list[dict[str, Any]]:
        """Check whether GuardDuty detectors are present and enabled in a region."""
        findings: list[dict[str, Any]] = []
        guardduty = self.session.client("guardduty", region_name=region)
        try:
            detector_ids = _collect_pages(guardduty, "list_detectors", "DetectorIds")
        except (BotoCoreError, ClientError) as exc:
            return [_error_finding("guardduty", region, "guardduty.detector_status", exc)]

        if not detector_ids:
            return [
                _finding(
                    "guardduty",
                    region,
                    "AWS account",
                    "guardduty.detector_status",
                    "HIGH",
                    "GuardDuty Detector Not Found",
                    f"No GuardDuty detector was found in region '{region}'.",
                    f"Enable GuardDuty in region '{region}' if required by the account's "
                    "security policy.",
                )
            ]

        for detector_id in detector_ids:
            try:
                detector = guardduty.describe_detector(DetectorId=detector_id)
                if detector.get("Status") != "ENABLED":
                    findings.append(
                        _finding(
                            "guardduty",
                            region,
                            detector_id,
                            "guardduty.detector_status",
                            "HIGH",
                            "GuardDuty Detector Disabled",
                            f"GuardDuty detector '{detector_id}' has status "
                            f"'{detector.get('Status', 'unknown')}'.",
                            f"Enable GuardDuty detector '{detector_id}' if required by the "
                            "account's security policy.",
                            status=detector.get("Status", "unknown"),
                        )
                    )
            except (BotoCoreError, ClientError) as exc:
                findings.append(
                    _error_finding("guardduty", region, "guardduty.detector_status", exc)
                )
        return findings
