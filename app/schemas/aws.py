"""AWS identity API schema."""

from pydantic import BaseModel


class AWSIdentityResponse(BaseModel):
    status: str
    account: str | None = None
    arn: str | None = None
    user_id: str | None = None
    region: str
