"""AWS identity service tests."""

from unittest.mock import Mock, patch

from botocore.exceptions import NoCredentialsError

from app.core.config import Settings
from app.services.aws_service import AWSService


def test_missing_credentials_return_not_configured():
    with patch("app.services.aws_service.boto3.Session", side_effect=NoCredentialsError()):
        response = AWSService(Settings(_env_file=None)).identity()

    assert response["status"] == "not_configured"
    assert response["account"] is None


def test_identity_returns_only_non_secret_metadata():
    sts = Mock()
    sts.get_caller_identity.return_value = {
        "Account": "000000000000",
        "Arn": "arn:aws:iam::000000000000:user/test",
        "UserId": "test-user",
    }
    session = Mock()
    session.client.return_value = sts
    with patch("app.services.aws_service.boto3.Session", return_value=session):
        response = AWSService(Settings(_env_file=None)).identity()

    assert response["status"] == "configured"
    assert response["account"] == "000000000000"
    assert "secret" not in str(response).lower()
