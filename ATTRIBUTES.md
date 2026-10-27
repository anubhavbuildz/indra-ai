# Third-Party Attributions

Indra uses the third-party software and services listed below. Package names
and links identify their respective projects; each remains subject to its own
copyright, license, and terms. Consult the package's upstream license and
notices before redistributing it. The project license does not replace or
modify those terms.

The lists cover direct dependencies declared in `pyproject.toml` and
`frontend/package.json`, including development and optional dependencies.
They are not an inventory of transitive dependencies. The Python environment
and `frontend/package-lock.json` identify resolved packages; consult each
package's included license and notice files for its applicable terms.

## Backend Python packages

| Package | Project |
| --- | --- |
| Alembic | [sqlalchemy/alembic](https://github.com/sqlalchemy/alembic) |
| boto3 | [boto/boto3](https://github.com/boto/boto3) |
| faiss-cpu | [facebookresearch/faiss](https://github.com/facebookresearch/faiss) |
| FastAPI | [fastapi/fastapi](https://github.com/fastapi/fastapi) |
| httpx | [encode/httpx](https://github.com/encode/httpx) |
| NumPy | [numpy/numpy](https://github.com/numpy/numpy) |
| openai (OpenAI Python SDK) | [openai/openai-python](https://github.com/openai/openai-python) |
| PyJWT | [jpadilla/pyjwt](https://github.com/jpadilla/pyjwt) |
| pydantic-settings | [pydantic/pydantic-settings](https://github.com/pydantic/pydantic-settings) |
| sentence-transformers | [UKPLab/sentence-transformers](https://github.com/UKPLab/sentence-transformers) |
| SQLAlchemy | [sqlalchemy/sqlalchemy](https://github.com/sqlalchemy/sqlalchemy) |
| uvicorn[standard] | [encode/uvicorn](https://github.com/encode/uvicorn) |
| psycopg[binary] (optional PostgreSQL extra) | [psycopg/psycopg](https://github.com/psycopg/psycopg) |
| pre-commit (development) | [pre-commit/pre-commit](https://github.com/pre-commit/pre-commit) |
| pytest (development) | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) |
| pytest-cov (development) | [pytest-dev/pytest-cov](https://github.com/pytest-dev/pytest-cov) |
| ruff (development) | [astral-sh/ruff](https://github.com/astral-sh/ruff) |

## Frontend JavaScript packages

| Package | Project |
| --- | --- |
| @tanstack/react-query | [TanStack/query](https://github.com/TanStack/query) |
| class-variance-authority | [joe-bell/cva](https://github.com/joe-bell/cva) |
| clsx | [lukeed/clsx](https://github.com/lukeed/clsx) |
| framer-motion | [motiondivision/motion](https://github.com/motiondivision/motion) |
| lucide-react | [lucide-icons/lucide](https://github.com/lucide-icons/lucide) |
| react | [facebook/react](https://github.com/facebook/react) |
| react-dom | [facebook/react](https://github.com/facebook/react) |
| react-markdown | [remarkjs/react-markdown](https://github.com/remarkjs/react-markdown) |
| react-router-dom | [remix-run/react-router](https://github.com/remix-run/react-router) |
| recharts | [recharts/recharts](https://github.com/recharts/recharts) |
| remark-gfm | [remarkjs/remark-gfm](https://github.com/remarkjs/remark-gfm) |
| tailwind-merge | [dcastil/tailwind-merge](https://github.com/dcastil/tailwind-merge) |
| @eslint/js | [eslint/eslint](https://github.com/eslint/eslint) |
| @vitejs/plugin-react | [vitejs/vite-plugin-react](https://github.com/vitejs/vite-plugin-react) |
| autoprefixer | [postcss/autoprefixer](https://github.com/postcss/autoprefixer) |
| eslint | [eslint/eslint](https://github.com/eslint/eslint) |
| eslint-plugin-react | [jsx-eslint/eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) |
| eslint-plugin-react-hooks | [facebook/react](https://github.com/facebook/react) |
| globals | [sindresorhus/globals](https://github.com/sindresorhus/globals) |
| postcss | [postcss/postcss](https://github.com/postcss/postcss) |
| tailwindcss | [tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) |
| vite | [vitejs/vite](https://github.com/vitejs/vite) |

## NVIDIA inference

The backend is configured by default to request the
`nvidia/Nemotron-3_5-Lightning` model through the Nebius Token Factory endpoint
(`https://api.tokenfactory.nebius.com/v1`). This is a configurable integration,
not bundled NVIDIA software. NVIDIA's model and associated materials remain
subject to NVIDIA's terms; the inference endpoint is operated by Nebius and is
subject to Nebius's terms. Model availability and terms may change.

- NVIDIA Nemotron information: [NVIDIA Nemotron](https://developer.nvidia.com/nemotron)
- Nebius Token Factory documentation: [Nebius Token Factory](https://docs.tokenfactory.nebius.com/)

NVIDIA and Nemotron are trademarks or registered trademarks of NVIDIA
Corporation. Nebius and Token Factory are trademarks of their respective
owners. Mention of these names does not imply endorsement or affiliation.

## GitHub Copilot

GitHub Copilot, an AI coding assistant from GitHub, was used as a development
aid. Suggestions were reviewed and integrated by project contributors.
Copilot is not a runtime dependency or part of the application. GitHub and
Copilot are trademarks of GitHub, Inc.; this attribution does not imply
endorsement or affiliation.

- [About GitHub Copilot](https://docs.github.com/en/copilot/about-github-copilot/what-is-github-copilot)

## Documentation and retrieved source materials

Project documentation under `design/` and the project README files describe
this application and its implementation. Third-party products and packages
remain the property of their respective owners; the links above point to their
project sources and documentation.

The RAG feature can retrieve passages from the locally configured FAISS index
and metadata. Those passages are third-party source material only when their
underlying documents are third-party works. The repository does not establish
the copyright owner or license for every document represented by a local
index. Keep each ingested document's source, author, license, and required
notices with the source corpus, and retain the citation metadata when rebuilding
or distributing the index. Runtime citations identify retrieved sources but
do not grant rights to reproduce them.
