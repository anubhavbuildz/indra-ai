"""Shared AWS audit finding and pagination helpers."""

from typing import Any

from botocore.exceptions import ClientError


def error_finding(service: str, region: str, check_id: str, error: Exception) -> dict[str, Any]:
    code = (
        error.response.get("Error", {}).get("Code", type(error).__name__)
        if isinstance(error, ClientError)
        else type(error).__name__
    )
    return {
        "service": service,
        "region": region,
        "check_id": check_id,
        "error": code,
        "issue": f"Audit check could not complete ({code}).",
    }


def finding(
    service: str,
    region: str,
    resource: str,
    check_id: str,
    severity: str,
    title: str,
    issue: str,
    remediation: str,
    **evidence: Any,
) -> dict[str, Any]:
    return {
        "service": service,
        "region": region,
        "resource": resource,
        "check_id": check_id,
        "severity": severity,
        "title": title,
        "issue": issue,
        "remediation": remediation,
        **({"evidence": evidence} if evidence else {}),
    }


def is_error(error: ClientError, *codes: str) -> bool:
    return error.response.get("Error", {}).get("Code", "") in codes


def collect_pages(client: Any, operation: str, result_key: str, **parameters: Any) -> list[Any]:
    return [
        item
        for page in client.get_paginator(operation).paginate(**parameters)
        for item in page.get(result_key, [])
    ]
