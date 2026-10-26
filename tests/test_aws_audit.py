"""Isolated boto3 API tests for the direct AWS auditor."""

from datetime import datetime
from unittest.mock import Mock, patch

import boto3
from botocore.stub import Stubber

from app.tools.audit.aws_audit import AWSAuditor


def client_for(service: str):
    return boto3.client(
        service,
        region_name="us-east-1",
        aws_access_key_id="test-access-key",
        aws_secret_access_key="test-secret-key",
    )


def auditor_with_clients(**clients: object) -> AWSAuditor:
    session = Mock()
    session.client.side_effect = lambda service, **kwargs: clients[service]
    with patch("app.tools.audit.aws_audit.boto3.Session", return_value=session):
        auditor = AWSAuditor()
    return auditor


def test_get_enabled_regions_returns_enabled_region_names():
    ec2 = client_for("ec2")
    auditor = auditor_with_clients(ec2=ec2)
    with Stubber(ec2) as stubber:
        stubber.add_response(
            "describe_regions",
            {
                "Regions": [
                    {"RegionName": "us-east-1", "OptInStatus": "opt-in-not-required"},
                    {"RegionName": "eu-west-1", "OptInStatus": "opted-in"},
                ]
            },
            {
                "Filters": [
                    {
                        "Name": "opt-in-status",
                        "Values": ["opt-in-not-required", "opted-in"],
                    }
                ]
            },
        )

        assert auditor.get_enabled_regions() == ["us-east-1", "eu-west-1"]


def test_s3_audit_reports_disabled_public_access_and_missing_encryption():
    s3 = client_for("s3")
    auditor = auditor_with_clients(s3=s3)
    with Stubber(s3) as stubber:
        stubber.add_response("list_buckets", {"Buckets": [{"Name": "example-bucket"}]})
        stubber.add_response(
            "get_bucket_location",
            {"LocationConstraint": "us-east-1"},
            {"Bucket": "example-bucket"},
        )
        stubber.add_response(
            "get_public_access_block",
            {
                "PublicAccessBlockConfiguration": {
                    "BlockPublicAcls": True,
                    "IgnorePublicAcls": False,
                    "BlockPublicPolicy": True,
                    "RestrictPublicBuckets": True,
                }
            },
            {"Bucket": "example-bucket"},
        )
        stubber.add_client_error(
            "get_bucket_encryption",
            service_error_code="ServerSideEncryptionConfigurationNotFoundError",
            expected_params={"Bucket": "example-bucket"},
        )
        stubber.add_response(
            "get_bucket_policy_status",
            {"PolicyStatus": {"IsPublic": True}},
            {"Bucket": "example-bucket"},
        )
        stubber.add_response(
            "get_bucket_acl",
            {
                "Owner": {"ID": "owner"},
                "Grants": [
                    {
                        "Grantee": {
                            "Type": "Group",
                            "URI": "http://acs.amazonaws.com/groups/global/AllUsers",
                        },
                        "Permission": "READ",
                    }
                ],
            },
            {"Bucket": "example-bucket"},
        )
        stubber.add_response(
            "get_bucket_versioning",
            {},
            {"Bucket": "example-bucket"},
        )
        stubber.add_response(
            "get_bucket_policy",
            {
                "Policy": (
                    '{"Version":"2012-10-17","Statement":{"Effect":"Deny",'
                    '"Principal":"*","Action":"s3:*","Resource":"*",'
                    '"Condition":{"Bool":{"aws:SecureTransport":"false"}}}}'
                )
            },
            {"Bucket": "example-bucket"},
        )
        stubber.add_response("get_bucket_logging", {}, {"Bucket": "example-bucket"})

        findings = auditor.audit_s3()

    assert {finding["check_id"] for finding in findings} == {
        "s3.public_access_block",
        "s3.default_encryption",
        "s3.public_bucket_policy",
        "s3.public_bucket_acl",
        "s3.versioning",
        "s3.access_logging",
    }
    assert all(finding["resource"] == "example-bucket" for finding in findings)


def test_iam_audit_reports_root_access_keys():
    iam = client_for("iam")
    auditor = auditor_with_clients(iam=iam)
    with Stubber(iam) as stubber:
        stubber.add_response(
            "get_account_summary",
            {"SummaryMap": {"AccountAccessKeysPresent": 1}},
        )

        findings = auditor.audit_iam()

    assert len(findings) == 1
    assert findings[0]["severity"] == "CRITICAL"
    assert findings[0]["resource"] == "AWS Root Account"


def test_regional_audits_report_open_management_ports_and_public_database():
    ec2 = client_for("ec2")
    rds = client_for("rds")
    auditor = auditor_with_clients(ec2=ec2, rds=rds)
    with Stubber(ec2) as ec2_stubber, Stubber(rds) as rds_stubber:
        ec2_stubber.add_response(
            "describe_security_groups",
            {
                "SecurityGroups": [
                    {
                        "GroupId": "sg-example",
                        "GroupName": "public-admin",
                        "IpPermissions": [
                            {
                                "IpProtocol": "tcp",
                                "FromPort": 22,
                                "ToPort": 22,
                                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                            }
                        ],
                    }
                ]
            },
        )
        ec2_stubber.add_response(
            "describe_instances",
            {"Reservations": []},
            {"Filters": [{"Name": "instance-state-name", "Values": ["running"]}]},
        )
        ec2_stubber.add_response("describe_volumes", {"Volumes": []})
        ec2_stubber.add_response(
            "get_ebs_encryption_by_default",
            {"EbsEncryptionByDefault": True},
        )
        ec2_stubber.add_response(
            "describe_snapshots",
            {"Snapshots": []},
            {"OwnerIds": ["self"]},
        )
        rds_stubber.add_response(
            "describe_db_instances",
            {
                "DBInstances": [
                    {
                        "DBInstanceIdentifier": "db-example",
                        "PubliclyAccessible": True,
                        "StorageEncrypted": False,
                        "MultiAZ": False,
                        "BackupRetentionPeriod": 7,
                        "DeletionProtection": True,
                    }
                ]
            },
        )
        rds_stubber.add_response("describe_db_clusters", {"DBClusters": []})
        rds_stubber.add_response(
            "describe_db_snapshots",
            {"DBSnapshots": []},
            {"SnapshotType": "manual"},
        )
        rds_stubber.add_response(
            "describe_db_cluster_snapshots",
            {"DBClusterSnapshots": []},
            {"SnapshotType": "manual"},
        )

        ec2_findings = auditor.audit_ec2("us-east-1")
        rds_findings = auditor.audit_databases("us-east-1")

    assert [finding["title"] for finding in ec2_findings] == ["SSH Open to Internet"]
    assert {finding["title"] for finding in rds_findings} == {
        "Database Instance Publicly Accessible",
        "Database Storage Encryption Disabled",
        "Database Multi-AZ Disabled",
    }


def test_ec2_audit_reports_ipv6_all_protocol_ingress_and_public_snapshot():
    ec2 = client_for("ec2")
    auditor = auditor_with_clients(ec2=ec2)
    with Stubber(ec2) as stubber:
        stubber.add_response(
            "describe_security_groups",
            {
                "SecurityGroups": [
                    {
                        "GroupId": "sg-example",
                        "GroupName": "public-all",
                        "IpPermissions": [
                            {
                                "IpProtocol": "-1",
                                "Ipv6Ranges": [{"CidrIpv6": "::/0"}],
                            }
                        ],
                    }
                ]
            },
        )
        stubber.add_response(
            "describe_instances",
            {"Reservations": []},
            {"Filters": [{"Name": "instance-state-name", "Values": ["running"]}]},
        )
        stubber.add_response(
            "describe_volumes",
            {
                "Volumes": [
                    {
                        "VolumeId": "vol-unencrypted",
                        "Size": 8,
                        "State": "in-use",
                        "CreateTime": datetime(2025, 1, 1),
                        "AvailabilityZone": "us-east-1a",
                        "Attachments": [],
                        "Tags": [],
                        "Encrypted": False,
                        "VolumeType": "gp3",
                    }
                ]
            },
        )
        stubber.add_response("get_ebs_encryption_by_default", {"EbsEncryptionByDefault": True})
        stubber.add_response(
            "describe_snapshots",
            {
                "Snapshots": [
                    {
                        "SnapshotId": "snap-example",
                        "VolumeId": "vol-example",
                        "State": "completed",
                        "StartTime": datetime(2025, 1, 1),
                        "Progress": "100%",
                        "OwnerId": "123456789012",
                        "Description": "test snapshot",
                        "VolumeSize": 8,
                        "Encrypted": True,
                    }
                ]
            },
            {"OwnerIds": ["self"]},
        )
        stubber.add_response(
            "describe_snapshot_attribute",
            {"SnapshotId": "snap-example", "CreateVolumePermissions": [{"Group": "all"}]},
            {"Attribute": "createVolumePermission", "SnapshotId": "snap-example"},
        )

        findings = auditor.audit_ec2("us-east-1")

    assert {finding["check_id"] for finding in findings} == {
        "ec2.security_group.world_ingress",
        "ec2.ebs.volume_encryption",
        "ec2.ebs.snapshot_public",
    }
    ingress = next(
        finding for finding in findings if finding["check_id"] == "ec2.security_group.world_ingress"
    )
    assert ingress["severity"] == "CRITICAL"
    assert ingress["evidence"]["public_cidrs"] == ["::/0"]
    volume_finding = next(
        finding for finding in findings if finding["check_id"] == "ec2.ebs.volume_encryption"
    )
    assert volume_finding["resource"] == "vol-unencrypted"


def test_rds_audit_reports_disabled_backups_deletion_protection_and_public_snapshots():
    rds = client_for("rds")
    auditor = auditor_with_clients(rds=rds)
    with Stubber(rds) as stubber:
        stubber.add_response(
            "describe_db_instances",
            {
                "DBInstances": [
                    {
                        "DBInstanceIdentifier": "db-example",
                        "PubliclyAccessible": False,
                        "StorageEncrypted": True,
                        "MultiAZ": True,
                        "BackupRetentionPeriod": 0,
                        "DeletionProtection": False,
                    }
                ]
            },
        )
        stubber.add_response(
            "describe_db_clusters",
            {
                "DBClusters": [
                    {
                        "DBClusterIdentifier": "cluster-example",
                        "BackupRetentionPeriod": 0,
                        "DeletionProtection": False,
                    }
                ]
            },
        )
        stubber.add_response(
            "describe_db_snapshots",
            {
                "DBSnapshots": [
                    {
                        "DBSnapshotIdentifier": "snapshot-example",
                        "DBInstanceIdentifier": "db-example",
                        "SnapshotCreateTime": datetime(2025, 1, 1),
                        "Engine": "postgres",
                        "Status": "available",
                        "Port": 5432,
                        "SnapshotType": "manual",
                        "VpcId": "vpc-example",
                        "AvailabilityZone": "us-east-1a",
                        "EngineVersion": "16.1",
                        "LicenseModel": "postgresql-license",
                        "OptionGroupName": "default:postgres-16",
                        "PercentProgress": 100,
                        "MasterUsername": "dbadmin",
                        "Encrypted": True,
                        "AllocatedStorage": 20,
                        "DBSnapshotArn": (
                            "arn:aws:rds:us-east-1:123456789012:snapshot:snapshot-example"
                        ),
                    }
                ]
            },
            {"SnapshotType": "manual"},
        )
        stubber.add_response(
            "describe_db_snapshot_attributes",
            {
                "DBSnapshotAttributesResult": {
                    "DBSnapshotIdentifier": "snapshot-example",
                    "DBSnapshotAttributes": [
                        {"AttributeName": "restore", "AttributeValues": ["all"]}
                    ],
                }
            },
            {"DBSnapshotIdentifier": "snapshot-example"},
        )
        stubber.add_response(
            "describe_db_cluster_snapshots",
            {"DBClusterSnapshots": [{"DBClusterSnapshotIdentifier": "cluster-snapshot-example"}]},
            {"SnapshotType": "manual"},
        )
        stubber.add_response(
            "describe_db_cluster_snapshot_attributes",
            {
                "DBClusterSnapshotAttributesResult": {
                    "DBClusterSnapshotIdentifier": "cluster-snapshot-example",
                    "DBClusterSnapshotAttributes": [
                        {"AttributeName": "restore", "AttributeValues": ["all"]}
                    ],
                }
            },
            {"DBClusterSnapshotIdentifier": "cluster-snapshot-example"},
        )

        findings = auditor.audit_databases("us-east-1")

    assert {finding["check_id"] for finding in findings} == {
        "rds.backup_retention",
        "rds.deletion_protection",
        "rds.cluster_backup_retention",
        "rds.cluster_deletion_protection",
        "rds.snapshot_public",
        "rds.cluster_snapshot_public",
    }


def test_cloudtrail_audit_checks_multiregion_logging_and_log_bucket_protection():
    ec2 = Mock()
    ec2.describe_regions.return_value = {
        "Regions": [{"RegionName": "us-east-1"}, {"RegionName": "eu-west-1"}]
    }
    cloudtrail = Mock()
    cloudtrail.describe_trails.return_value = {
        "trailList": [
            {
                "Name": "organization-trail",
                "TrailARN": "arn:aws:cloudtrail:us-east-1:123456789012:trail/organization-trail",
                "HomeRegion": "us-east-1",
                "IsMultiRegionTrail": True,
                "LogFileValidationEnabled": True,
                "S3BucketName": "audit-logs",
            }
        ]
    }
    cloudtrail.get_trail_status.return_value = {"IsLogging": True}
    s3 = Mock()
    s3.get_public_access_block.return_value = {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        }
    }
    s3.get_bucket_encryption.return_value = {"ServerSideEncryptionConfiguration": {}}
    auditor = auditor_with_clients(ec2=ec2, cloudtrail=cloudtrail, s3=s3)

    findings = auditor.audit_cloudtrail()

    assert findings == []
    assert cloudtrail.describe_trails.call_count == 2
    cloudtrail.describe_trails.assert_called_with(includeShadowTrails=True)
    cloudtrail.get_trail_status.assert_called_once_with(
        Name="arn:aws:cloudtrail:us-east-1:123456789012:trail/organization-trail"
    )


def test_guardduty_audit_reports_missing_detector():
    guardduty = Mock()
    guardduty.get_paginator.return_value.paginate.return_value = [{"DetectorIds": []}]
    auditor = auditor_with_clients(guardduty=guardduty)

    findings = auditor.audit_guardduty("eu-west-1")

    assert len(findings) == 1
    assert findings[0]["check_id"] == "guardduty.detector_status"
    assert findings[0]["title"] == "GuardDuty Detector Not Found"
    assert findings[0]["region"] == "eu-west-1"


def test_vpc_audit_reports_default_vpc_without_flow_logs():
    ec2 = client_for("ec2")
    auditor = auditor_with_clients(ec2=ec2)
    with Stubber(ec2) as stubber:
        stubber.add_response(
            "describe_vpcs",
            {"Vpcs": [{"VpcId": "vpc-example", "IsDefault": True}]},
        )
        stubber.add_response(
            "describe_flow_logs",
            {"FlowLogs": []},
            {"Filters": [{"Name": "resource-id", "Values": ["vpc-example"]}]},
        )

        findings = auditor.audit_vpc("us-east-1")

    assert [finding["title"] for finding in findings] == [
        "Default VPC In Use",
        "VPC Flow Logs Disabled",
    ]
