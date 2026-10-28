"""Optional QA selection and traceability plugin; preserves existing test files."""

import json
from pathlib import Path

import pytest


def pytest_collection_modifyitems(items):
    cases = json.loads(Path("design/qa/qa-cases.json").read_text())
    for item in items:
        node = item.nodeid.split("[")[0]
        matches = [case for case in cases if case["path"] == node]
        if matches:
            category = matches[0]["category"]
            item.user_properties.append(("case_id", matches[0]["id"]))
        else:
            category = next(
                (
                    name
                    for name in ("unit", "integration", "security", "performance")
                    if f"test_qa_{name}.py" in node
                ),
                None,
            )
            matches = [
                case
                for case in cases
                if case["category"] == category
                and case["path"].split("::")[0] == node.split("::")[0]
            ]
            if matches:
                item.user_properties.append(("case_id", matches[0]["id"]))
        if not matches or category is None:
            raise pytest.UsageError(f"No documented QA case for {node}")
        item.add_marker(getattr(pytest.mark, category))


def pytest_load_initial_conftests():
    import os
    import tempfile

    os.environ.update(
        {
            "APP_ENV": "development",
            "DEBUG": "false",
            "API_V1_PREFIX": "/api/v1",
            "AUTH_USERNAME": "",
            "AUTH_PASSWORD": "",
            "JWT_SECRET_KEY": "",
            "NVIDIA_API_KEY": "",
            "AWS_EC2_METADATA_DISABLED": "true",
            "DATABASE_URL": "sqlite:///"
            + str(Path(tempfile.mkdtemp(prefix="indra-qa-")) / "test.db"),
        }
    )


@pytest.fixture(autouse=True)
def block_external_sockets(monkeypatch):
    import socket

    def blocked(*args, **kwargs):
        raise AssertionError("QA forbids real network connections; use a boundary fixture")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)
