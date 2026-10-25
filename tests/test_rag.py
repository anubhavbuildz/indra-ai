"""RAG index behavior tests."""

import pickle
from pathlib import Path

import pytest

from app.core.config import Settings
from app.services.rag_service import RagService, build_index


def settings_at(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,
        FAISS_INDEX_PATH=tmp_path / "index.faiss",
        FAISS_METADATA_PATH=tmp_path / "metadata.pkl",
    )


def make_document(chunk_id: str, text: str, source_title: str) -> dict[str, str]:
    return {
        "chunk_id": chunk_id,
        "text": text,
        "source_title": source_title,
        "source_url": "",
        "document_version": "test-v1",
        "document_date": "",
        "section_id": "",
    }


def test_missing_index_is_reported_without_fabricated_results(tmp_path):
    service = RagService(settings_at(tmp_path))

    assert service.status()["status"] == "not_indexed"
    assert service.query("network policy") == {"status": "not_indexed", "results": []}


def test_deterministic_index_preserves_attribution(tmp_path):
    settings = settings_at(tmp_path)
    documents = [
        make_document("network-1", "Network firewall restricts inbound traffic.", "Network policy"),
        make_document("storage-1", "Encrypt object storage at rest.", "Storage guidance"),
    ]
    assert build_index(settings, documents) == 2

    service = RagService(settings)
    results = service.query("firewall inbound traffic", limit=1)

    assert service.status()["status"] == "ready"
    assert results["results"][0]["chunk_id"] == "network-1"
    assert results["results"][0]["source_title"] == "Network policy"
    assert results["results"][0]["source_url"] == ""


def test_metadata_mismatch_is_not_used(tmp_path):
    settings = settings_at(tmp_path)
    build_index(settings, [make_document("chunk-1", "Firewall policy.", "Policy")])
    with settings.faiss_metadata_path.open("rb") as metadata_file:
        metadata = pickle.load(metadata_file)
    metadata["documents"].clear()
    with settings.faiss_metadata_path.open("wb") as metadata_file:
        pickle.dump(metadata, metadata_file)

    service = RagService(settings)
    assert service.status()["status"] == "mismatch"
    assert service.query("firewall") == {"status": "mismatch", "results": []}
