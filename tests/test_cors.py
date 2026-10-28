"""Regression coverage for frontend CORS preflight."""

import pytest


@pytest.mark.parametrize(
    "origin, expected",
    [
        ("http://localhost:5173", 200),
        ("http://127.0.0.1:5173", 200),
        ("https://untrusted.example", 400),
    ],
)
def test_cors_preflight_for_local_frontend(client, origin, expected):
    response = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization",
        },
    )
    assert response.status_code == expected
    if expected == 200:
        assert response.headers["access-control-allow-origin"] == origin
    else:
        assert "access-control-allow-origin" not in response.headers
