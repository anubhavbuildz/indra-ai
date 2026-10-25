"""AWS identity lookup through the standard credential chain."""

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError, ProfileNotFound

from app.core.config import Settings
from app.core.errors import AppError


class AWSService:
    """Read-only AWS caller identity check."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def identity(self) -> dict[str, str | None]:
        try:
            session = boto3.Session(region_name=self.settings.aws_region)
            identity = session.client("sts").get_caller_identity()
        except (NoCredentialsError, ProfileNotFound):
            return {
                "status": "not_configured",
                "account": None,
                "arn": None,
                "user_id": None,
                "region": self.settings.aws_region,
            }
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code in {"NoCredentials", "NoCredentialProviders"}:
                return {
                    "status": "not_configured",
                    "account": None,
                    "arn": None,
                    "user_id": None,
                    "region": self.settings.aws_region,
                }
            raise AppError(502, "aws_identity_error", "AWS identity verification failed.") from exc
        except BotoCoreError as exc:
            raise AppError(502, "aws_identity_error", "AWS identity verification failed.") from exc

        return {
            "status": "configured",
            "account": identity.get("Account"),
            "arn": identity.get("Arn"),
            "user_id": identity.get("UserId"),
            "region": self.settings.aws_region,
        }
