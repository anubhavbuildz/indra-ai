# Local knowledge documents

Place only documents you are authorized to use in this directory. The
ingester reads UTF-8 `.md` and `.txt` files; it does not download documents
or contact external sources. Keep attribution in the document itself. During
this scaffold, source titles are derived from the local filename and source
URLs, document dates, versions, and control IDs are left empty unless a future
metadata-aware importer explicitly supplies them.

Run `python scripts/ingest_documents.py` to rebuild the local FAISS index.
Use `--source-dir PATH` to ingest another trusted local directory. Rebuilding
replaces both configured index files. Deploy `index.faiss` and `metadata.pkl`
as a matching pair; the API checks dimensions, schema version, embedding
identifier, and passage count before using either.

`metadata.pkl` is a trusted local artifact. Python pickle can execute code
when loaded. Never accept it from a user, upload endpoint, issue, or external
repository. The current embedding implementation is deterministic local
feature hashing (384 dimensions), not semantic model inference; use it only
as a lexical baseline. A future model adapter must preserve the configured
model identity and vector dimension for both indexing and querying.
