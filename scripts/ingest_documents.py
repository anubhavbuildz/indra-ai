"""Build the local FAISS index from plain-text and Markdown knowledge files."""

import argparse
import hashlib
import re
from pathlib import Path

from app.core.config import get_settings
from app.services.rag_service import build_index

MAX_DOCUMENT_BYTES = 5 * 1024 * 1024
SUPPORTED_SUFFIXES = {".md", ".txt"}


def chunk_document(path: Path, root: Path, chunk_size: int = 1_200) -> list[dict[str, str]]:
    """Extract text chunks and retain source identity from local paths."""
    if path.stat().st_size > MAX_DOCUMENT_BYTES:
        raise ValueError(f"Document exceeds {MAX_DOCUMENT_BYTES} bytes: {path}")
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    if not resolved_path.is_relative_to(resolved_root):
        raise ValueError(f"Document path escapes the knowledge-base directory: {path}")
    content = resolved_path.read_text(encoding="utf-8")
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", content)]
    paragraphs = [part for part in paragraphs if part]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 1 > chunk_size:
            chunks.append(current)
            current = ""
        while len(paragraph) > chunk_size:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(paragraph[:chunk_size])
            paragraph = paragraph[chunk_size:]
        current = f"{current} {paragraph}".strip()
    if current:
        chunks.append(current)
    relative_path = resolved_path.relative_to(resolved_root).as_posix()
    title = resolved_path.stem.replace("_", " ").replace("-", " ").strip()
    output = []
    for chunk_number, text in enumerate(chunks):
        chunk_hash = hashlib.sha256(f"{relative_path}:{chunk_number}:{text}".encode()).hexdigest()[:16]
        output.append(
            {
                "chunk_id": chunk_hash,
                "text": text,
                "source_title": title,
                "source_url": "",
                "document_version": "",
                "document_date": "",
                "section_id": "",
            }
        )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rebuild the local FAISS index from .md and .txt files in a source directory."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=get_settings().knowledge_base_path,
        help="Directory containing locally licensed .md/.txt documents.",
    )
    args = parser.parse_args()
    source_dir = args.source_dir.resolve()
    if not source_dir.is_dir():
        parser.error(f"Source directory does not exist: {source_dir}")
    documents = [
        chunk
        for path in sorted(source_dir.rglob("*"))
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
        for chunk in chunk_document(path, source_dir)
    ]
    count = build_index(get_settings(), documents)
    print(f"Indexed {count} passage(s) from {source_dir}.")


if __name__ == "__main__":
    main()
