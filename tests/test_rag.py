"""Unit and API integration coverage for local retrieval."""

import pickle
from pathlib import Path
from unittest.mock import AsyncMock

import faiss
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.main import app
from app.services.rag import RagService, RetrievedPassage, retrieval
from app.services.rag.store import load_store, resolve_store_path


def _write_store(directory: Path) -> tuple[Path, Path]:
    index_path = directory / "security.index"
    metadata_path = directory / "security.pkl"
    index = faiss.IndexFlatIP(3)
    index.add(
        np.array(
            [
                [0.1, 0.1, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float32,
        )
    )
    faiss.write_index(index, str(index_path))
    documents = [
        {
            "source_document": title,
            "data": {
                "document_title": title,
                "abstract_or_summary": f"Guidance about {title.lower()}.",
                "source": {"source_name": title, "source_uri": f"https://example.test/{i}"},
            },
        }
        for i, title in enumerate(("Encryption", "Logging", "Identity"))
    ]
    with metadata_path.open("wb") as file:
        pickle.dump(documents, file)
    return index_path, metadata_path


def test_retriever_returns_faiss_ranked_passages_and_sources(tmp_path, monkeypatch):
    index_path, metadata_path = _write_store(tmp_path)

    class EmbeddingModel:
        def encode(self, *_args, **_kwargs):
            return np.array([0.0, 1.0, 0.0], dtype=np.float32)

    monkeypatch.setattr(retrieval, "load_embedding_model", lambda _: EmbeddingModel())
    passages = retrieval.RagRetriever(
        "test-model",
        index_path,
        metadata_path,
    ).retrieve("logging controls")

    assert passages[0].title == "Logging"
    assert {passage.title for passage in passages} == {"Logging", "Encryption", "Identity"}
    assert passages[0].source_uri == "https://example.test/1"
    assert passages[0].as_source() == {
        "title": "Logging",
        "source": "Logging",
        "uri": "https://example.test/1",
    }


def test_store_loader_rejects_document_count_mismatch(tmp_path):
    index_path, metadata_path = _write_store(tmp_path)
    with metadata_path.open("wb") as file:
        pickle.dump([], file)

    with pytest.raises(AppError) as error:
        load_store(str(index_path), str(metadata_path))

    assert error.value.code == "rag_metadata_mismatch"


def test_resolve_store_path_preserves_absolute_paths(tmp_path):
    assert resolve_store_path(tmp_path / "store.index") == tmp_path / "store.index"


def test_rag_query_route_returns_passages_and_citations(client: TestClient, monkeypatch):
    passage = RetrievedPassage(
        title="Encryption",
        content="Enable encryption at rest.",
        source_name="Security guide",
        source_uri="https://example.test/encryption",
    )
    query = AsyncMock(return_value=[passage])
    monkeypatch.setattr(RagService, "query", query)

    response = client.post(
        "/api/v1/rag/query",
        json={"question": "How do I encrypt data?"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "question": "How do I encrypt data?",
        "passages": [
            {
                "title": "Encryption",
                "content": "Enable encryption at rest.",
                "source": "Security guide",
                "uri": "https://example.test/encryption",
            }
        ],
        "sources": [
            {
                "title": "Encryption",
                "source": "Security guide",
                "uri": "https://example.test/encryption",
            }
        ],
    }
    query.assert_awaited_once()


def test_rag_status_route_reports_missing_files(
    client: TestClient,
    test_auth_settings: Settings,
    tmp_path,
):
    index_path = tmp_path / "missing.index"
    metadata_path = tmp_path / "missing.pkl"
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None,
        AUTH_USERNAME=test_auth_settings.auth_username,
        AUTH_PASSWORD=test_auth_settings.auth_password,
        JWT_SECRET_KEY=test_auth_settings.jwt_secret_key,
        FAISS_INDEX_PATH=index_path,
        FAISS_METADATA_PATH=metadata_path,
    )
    try:
        response = client.get("/api/v1/rag/status")
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 200
    assert response.json()["available"] is False
    assert response.json()["index_available"] is False
    assert response.json()["metadata_available"] is False


def test_rag_query_returns_safe_error_when_store_is_missing(
    client: TestClient,
    test_auth_settings: Settings,
    tmp_path,
):
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None,
        AUTH_USERNAME=test_auth_settings.auth_username,
        AUTH_PASSWORD=test_auth_settings.auth_password,
        JWT_SECRET_KEY=test_auth_settings.jwt_secret_key,
        FAISS_INDEX_PATH=tmp_path / "missing.index",
        FAISS_METADATA_PATH=tmp_path / "missing.pkl",
    )
    try:
        response = client.post(
            "/api/v1/rag/query",
            json={"question": "How should I protect data?"},
        )
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "rag_store_unavailable"
    assert str(tmp_path) not in response.text


def test_rag_query_validates_question_length(client: TestClient):
    response = client.post(
        "/api/v1/rag/query",
        json={"question": "x" * 8_001},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
