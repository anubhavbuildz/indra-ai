.PHONY: install dev test lint format ingest

install:
	python -m pip install -e '.[dev]'

dev:
	uvicorn app.main:app --reload

test:
	pytest --cov=app --cov-report=term-missing

lint:
	ruff check .

format:
	ruff format .

ingest:
	python scripts/ingest_documents.py
