"""RDSAudit AWS audit checks."""

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


class RDSAuditMixin:
    def audit_databases(self, region: str) -> list[dict[str, Any]]:
        """Audit RDS database instances for exposure and encryption."""
        findings: list[dict[str, Any]] = []
        rds = self.session.client("rds", region_name=region)

        try:
            instances = _collect_pages(rds, "describe_db_instances", "DBInstances")
            for db in instances:
                db_id = db["DBInstanceIdentifier"]

                # 1. Publicly Accessible Database Check
                if db.get("PubliclyAccessible", False):
                    findings.append(
                        {
                            "service": "rds",
                            "region": region,
                            "resource": db_id,
                            "severity": "CRITICAL",
                            "title": "Database Instance Publicly Accessible",
                            "issue": (
                                f"RDS instance '{db_id}' is configured with public IP "
                                "accessibility."
                            ),
                            "remediation": (
                                f"Disable 'PubliclyAccessible' on RDS instance '{db_id}' and "
                                "place it in a private subnet."
                            ),
                        }
                    )

                # 2. Storage Encryption at Rest Check
                if not db.get("StorageEncrypted", False):
                    findings.append(
                        {
                            "service": "rds",
                            "region": region,
                            "resource": db_id,
                            "severity": "HIGH",
                            "title": "Database Storage Encryption Disabled",
                            "issue": f"RDS instance '{db_id}' storage is not encrypted at rest.",
                            "remediation": (
                                f"Enable KMS encryption on storage for RDS instance '{db_id}'."
                            ),
                        }
                    )

                # 3. Multi-AZ Redundancy Check
                if not db.get("MultiAZ", False):
                    findings.append(
                        _finding(
                            "rds",
                            region,
                            db_id,
                            "rds.multi_az",
                            "LOW",
                            "Database Multi-AZ Disabled",
                            f"RDS instance '{db_id}' does not have high-availability "
                            "Multi-AZ failover enabled.",
                            f"Enable Multi-AZ deployment on instance '{db_id}' for production "
                            "resilience.",
                        )
                    )

                if db.get("BackupRetentionPeriod", 0) < 1:
                    findings.append(
                        _finding(
                            "rds",
                            region,
                            db_id,
                            "rds.backup_retention",
                            "HIGH",
                            "RDS Automated Backups Disabled",
                            f"RDS instance '{db_id}' has no automated backup retention period.",
                            f"Configure an appropriate backup retention period for '{db_id}'.",
                            backup_retention_days=db.get("BackupRetentionPeriod", 0),
                        )
                    )

                if not db.get("DeletionProtection", False):
                    findings.append(
                        _finding(
                            "rds",
                            region,
                            db_id,
                            "rds.deletion_protection",
                            "MEDIUM",
                            "RDS Deletion Protection Disabled",
                            f"RDS instance '{db_id}' does not have deletion protection enabled.",
                            f"Enable deletion protection for '{db_id}' where operationally "
                            "appropriate.",
                        )
                    )
        except (BotoCoreError, ClientError) as exc:
            findings.append(_error_finding("rds", region, "rds.instances", exc))

        try:
            clusters = _collect_pages(rds, "describe_db_clusters", "DBClusters")
            for cluster in clusters:
                cluster_id = cluster["DBClusterIdentifier"]
                if cluster.get("BackupRetentionPeriod", 0) < 1:
                    findings.append(
                        _finding(
                            "rds",
                            region,
                            cluster_id,
                            "rds.cluster_backup_retention",
                            "HIGH",
                            "RDS Cluster Automated Backups Disabled",
                            f"RDS cluster '{cluster_id}' has no automated backup retention period.",
                            f"Configure an appropriate backup retention period for '{cluster_id}'.",
                            backup_retention_days=cluster.get("BackupRetentionPeriod", 0),
                        )
                    )
                if not cluster.get("DeletionProtection", False):
                    findings.append(
                        _finding(
                            "rds",
                            region,
                            cluster_id,
                            "rds.cluster_deletion_protection",
                            "MEDIUM",
                            "RDS Cluster Deletion Protection Disabled",
                            f"RDS cluster '{cluster_id}' does not have deletion protection "
                            "enabled.",
                            f"Enable deletion protection for '{cluster_id}' where operationally "
                            "appropriate.",
                        )
                    )
        except (BotoCoreError, ClientError) as exc:
            findings.append(_error_finding("rds", region, "rds.clusters", exc))

        try:
            snapshots = _collect_pages(
                rds,
                "describe_db_snapshots",
                "DBSnapshots",
                SnapshotType="manual",
            )
            for snapshot in snapshots:
                snapshot_id = snapshot["DBSnapshotIdentifier"]
                try:
                    attributes = rds.describe_db_snapshot_attributes(
                        DBSnapshotIdentifier=snapshot_id
                    ).get("DBSnapshotAttributesResult", {})
                except (BotoCoreError, ClientError) as exc:
                    findings.append(_error_finding("rds", region, "rds.snapshot_public", exc))
                    continue
                restore_attributes = next(
                    (
                        attribute.get("AttributeValues", [])
                        for attribute in attributes.get("DBSnapshotAttributes", [])
                        if attribute.get("AttributeName") == "restore"
                    ),
                    [],
                )
                if "all" in restore_attributes:
                    findings.append(
                        _finding(
                            "rds",
                            region,
                            snapshot_id,
                            "rds.snapshot_public",
                            "CRITICAL",
                            "RDS Snapshot Publicly Shared",
                            f"Manual snapshot '{snapshot_id}' allows restore access to all "
                            "AWS accounts.",
                            f"Remove the public restore attribute from snapshot '{snapshot_id}'.",
                        )
                    )
        except (BotoCoreError, ClientError) as exc:
            findings.append(_error_finding("rds", region, "rds.snapshot_public", exc))

        try:
            cluster_snapshots = _collect_pages(
                rds,
                "describe_db_cluster_snapshots",
                "DBClusterSnapshots",
                SnapshotType="manual",
            )
            for snapshot in cluster_snapshots:
                snapshot_id = snapshot["DBClusterSnapshotIdentifier"]
                try:
                    attributes = rds.describe_db_cluster_snapshot_attributes(
                        DBClusterSnapshotIdentifier=snapshot_id
                    ).get("DBClusterSnapshotAttributesResult", {})
                except (BotoCoreError, ClientError) as exc:
                    findings.append(
                        _error_finding("rds", region, "rds.cluster_snapshot_public", exc)
                    )
                    continue
                restore_attributes = next(
                    (
                        attribute.get("AttributeValues", [])
                        for attribute in attributes.get("DBClusterSnapshotAttributes", [])
                        if attribute.get("AttributeName") == "restore"
                    ),
                    [],
                )
                if "all" in restore_attributes:
                    findings.append(
                        _finding(
                            "rds",
                            region,
                            snapshot_id,
                            "rds.cluster_snapshot_public",
                            "CRITICAL",
                            "RDS Cluster Snapshot Publicly Shared",
                            f"Manual cluster snapshot '{snapshot_id}' allows restore access "
                            "to all AWS accounts.",
                            f"Remove the public restore attribute from snapshot '{snapshot_id}'.",
                        )
                    )
        except (BotoCoreError, ClientError) as exc:
            findings.append(_error_finding("rds", region, "rds.cluster_snapshot_public", exc))

        return findings
