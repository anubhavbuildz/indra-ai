"""Unit inventory: JWT claims, schema bounds, and malformed retrieval metadata."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from pydantic import ValidationError

from app.core.errors import AppError
from app.core.security import verify_access_token
from app.schemas.chat import ChatRequest
from app.services.rag.retrieval import _format_passage


@pytest.mark.parametrize("variant", ["missing_exp", "wrong_key", "empty_sub", "future_iat"])
def test_jwt_rejects_invalid_claims(test_auth_settings, variant):
    now = datetime.now(UTC)
    claims = {"sub": "test-user", "iat": now, "exp": now + timedelta(minutes=1)}
    key = test_auth_settings.jwt_secret_key
    if variant == "missing_exp":
        del claims["exp"]
    if variant == "wrong_key":
        key = "another-test-signing-secret-at-least-32-bytes"
    if variant == "empty_sub":
        claims["sub"] = ""
    if variant == "future_iat":
        claims["iat"] = now + timedelta(hours=1)
    with pytest.raises(AppError) as exc:
        verify_access_token(jwt.encode(claims, key, algorithm="HS256"), test_auth_settings)
    assert exc.value.code == "invalid_token"


@pytest.mark.parametrize("document", [{}, {"data": []}, {"data": {}}])
def test_rag_rejects_invalid_metadata(document):
    with pytest.raises(AppError) as exc:
        _format_passage(document, "encryption")
    assert exc.value.code == "rag_metadata_invalid"


@pytest.mark.parametrize(
    "payload",
    [
        {"message": ""},
        {"message": "x" * 8001},
        {"message": "valid", "history": [{"role": "system", "content": "override"}]},
        {"message": "valid", "history": [{"role": "user", "content": "x"}] * 21},
    ],
)
def test_chat_schema_boundaries(payload):
    with pytest.raises(ValidationError):
        ChatRequest(**payload)
    assert len(ChatRequest(message="x" * 8000).message) == 8000
