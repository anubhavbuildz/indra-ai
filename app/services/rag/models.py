"""Typed values shared by the local retrieval components."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedPassage:
    """A local guidance passage with source attribution."""

    title: str
    content: str
    source_name: str
    source_uri: str

    def as_source(self) -> dict[str, str]:
        """Return the public citation fields for a retrieved passage."""
        source = {"title": self.title, "source": self.source_name}
        if self.source_uri:
            source["uri"] = self.source_uri
        return source

    def as_prompt_data(self) -> dict[str, str]:
        """Return passage text and attribution for the compliance prompt."""
        passage = {"title": self.title, "source": self.source_name, "content": self.content}
        if self.source_uri:
            passage["uri"] = self.source_uri
        return passage


@dataclass(frozen=True)
class RagStatus:
    """Local retrieval readiness without loading the embedding model."""

    available: bool
    embedding_model: str
    index_available: bool
    metadata_available: bool
    error_code: str | None = None
