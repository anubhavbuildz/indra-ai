"""EC2Audit AWS audit checks."""

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


class EC2AuditMixin:
    def audit_ec2(self, region: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        ec2 = self.session.client("ec2", region_name=region)

        try:
            sgs = _collect_pages(ec2, "describe_security_groups", "SecurityGroups")
            for sg in sgs:
                sg_id = sg["GroupId"]
                sg_name = sg.get("GroupName", "unknown")
                for rule in sg.get("IpPermissions", []):
                    from_port = rule.get("FromPort")
                    to_port = rule.get("ToPort")
                    public_ipv4 = [
                        item.get("CidrIp")
                        for item in rule.get("IpRanges", [])
                        if item.get("CidrIp") == "0.0.0.0/0"
                    ]
                    public_ipv6 = [
                        item.get("CidrIpv6")
                        for item in rule.get("Ipv6Ranges", [])
                        if item.get("CidrIpv6") == "::/0"
                    ]
                    if not public_ipv4 and not public_ipv6:
                        continue

                    protocol = rule.get("IpProtocol", "-1")
                    all_ports = protocol == "-1" or from_port is None or to_port is None
                    exposed_all_ports = all_ports or (from_port == 0 and to_port == 65535)
                    exposed_management_port = (
                        not all_ports
                        and from_port is not None
                        and to_port is not None
                        and (from_port <= 22 <= to_port or from_port <= 3389 <= to_port)
                    )
                    if exposed_management_port and from_port == to_port == 22:
                        title = "SSH Open to Internet"
                    elif exposed_management_port and from_port == to_port == 3389:
                        title = "RDP Open to Internet"
                    else:
                        title = "Inbound Access Open to Internet"
                    severity = (
                        "CRITICAL" if exposed_all_ports or exposed_management_port else "HIGH"
                    )
                    port_description = (
                        "all ports" if exposed_all_ports else f"ports {from_port}-{to_port}"
                    )
                    protocol_description = (
                        "all protocols" if protocol == "-1" else f"protocol {protocol}"
                    )
                    public_cidrs = public_ipv4 + public_ipv6
                    findings.append(
                        _finding(
                            "ec2",
                            region,
                            f"{sg_name} ({sg_id})",
                            "ec2.security_group.world_ingress",
                            severity,
                            title,
                            f"Inbound {protocol_description}, {port_description} is open to "
                            f"{', '.join(public_cidrs)}.",
                            f"Restrict inbound access on security group '{sg_id}' to trusted "
                            "sources and required ports.",
                            protocol=protocol,
                            from_port=from_port,
                            to_port=to_port,
                            public_cidrs=public_cidrs,
                        )
                    )
        except (BotoCoreError, ClientError) as exc:
            findings.append(_error_finding("ec2", region, "ec2.security_group.world_ingress", exc))

        try:
            reservations = _collect_pages(
                ec2,
                "describe_instances",
                "Reservations",
                Filters=[{"Name": "instance-state-name", "Values": ["running"]}],
            )
            for res in reservations:
                for inst in res.get("Instances", []):
                    pub_ip = inst.get("PublicIpAddress")
                    if pub_ip:
                        findings.append(
                            _finding(
                                "ec2",
                                region,
                                inst.get("InstanceId", "unknown"),
                                "ec2.instance.public_ip",
                                "LOW",
                                "Public IP Assigned to Instance",
                                f"Running instance has public IP {pub_ip}.",
                                "Relocate instance to a private subnet behind an ALB or NAT "
                                "Gateway.",
                                public_ip=pub_ip,
                            )
                        )
        except (BotoCoreError, ClientError) as exc:
            findings.append(_error_finding("ec2", region, "ec2.instance.public_ip", exc))

        try:
            volumes = _collect_pages(ec2, "describe_volumes", "Volumes")
            for volume in volumes:
                if not volume.get("Encrypted", False):
                    volume_id = volume.get("VolumeId", "unknown")
                    findings.append(
                        _finding(
                            "ec2",
                            region,
                            volume_id,
                            "ec2.ebs.volume_encryption",
                            "HIGH",
                            "EBS Volume Encryption Disabled",
                            f"EBS volume '{volume_id}' is not encrypted.",
                            "Encrypt the volume using an approved migration or replacement plan.",
                            volume_type=volume.get("VolumeType"),
                            attached_instances=[
                                attachment.get("InstanceId")
                                for attachment in volume.get("Attachments", [])
                            ],
                        )
                    )
        except (BotoCoreError, ClientError) as exc:
            findings.append(_error_finding("ec2", region, "ec2.ebs.volume_encryption", exc))

        try:
            encryption = ec2.get_ebs_encryption_by_default()
            if not encryption.get("EbsEncryptionByDefault", False):
                findings.append(
                    _finding(
                        "ec2",
                        region,
                        "AWS account",
                        "ec2.ebs.default_encryption",
                        "HIGH",
                        "EBS Default Encryption Disabled",
                        "EBS encryption by default is disabled in this region.",
                        "Enable EBS encryption by default in the audited region.",
                    )
                )
        except (BotoCoreError, ClientError) as exc:
            findings.append(_error_finding("ec2", region, "ec2.ebs.default_encryption", exc))

        try:
            snapshots = _collect_pages(
                ec2,
                "describe_snapshots",
                "Snapshots",
                OwnerIds=["self"],
            )
            for snapshot in snapshots:
                snapshot_id = snapshot["SnapshotId"]
                try:
                    permissions = ec2.describe_snapshot_attribute(
                        Attribute="createVolumePermission",
                        SnapshotId=snapshot_id,
                    ).get("CreateVolumePermissions", [])
                except (BotoCoreError, ClientError) as exc:
                    findings.append(_error_finding("ec2", region, "ec2.ebs.snapshot_public", exc))
                    continue
                if any(permission.get("Group") == "all" for permission in permissions):
                    findings.append(
                        _finding(
                            "ec2",
                            region,
                            snapshot_id,
                            "ec2.ebs.snapshot_public",
                            "CRITICAL",
                            "EBS Snapshot Publicly Shared",
                            f"Snapshot '{snapshot_id}' grants create-volume permission to all "
                            "AWS accounts.",
                            f"Remove public create-volume permission from snapshot "
                            f"'{snapshot_id}'.",
                        )
                    )
        except (BotoCoreError, ClientError) as exc:
            findings.append(_error_finding("ec2", region, "ec2.ebs.snapshot_public", exc))

        return findings
