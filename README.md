# azure-blob-ci-pipeline

A small Python project that lists blobs from a public Azure Blob Storage container and filters them by file extension. The point of the repo is the engineering around the code: a multi-stage GitHub Actions pipeline, meaningful unit tests, and a hardened Dockerfile.

## What's inside

```
.
├── .github/workflows/pipeline.yml   # lint -> test CI pipeline
├── src/adls_client.py               # filter_blobs + main()
├── tests/test_adls_client.py        # pytest suite
├── Dockerfile                       # hardened image
├── .dockerignore                    # keeps build context lean
├── pyproject.toml                   # pytest + ruff config
└── requirements.txt
```

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

ruff check src/
pytest -v
python src/adls_client.py
```

`python src/adls_client.py` hits the public `azurepublicdataset` container anonymously and prints every blob name ending in `.csv.gz`.

## Run it in Docker

```bash
docker build -t azure-blob-ci-pipeline .
docker run --rm azure-blob-ci-pipeline
```

The container runs as a non-root user and only ships the runtime files it needs.

## CI pipeline

`.github/workflows/pipeline.yml` runs on every push and on manual dispatch:

1. **lint** — installs dependencies and runs `ruff check src/`.
2. **test** — gated on `lint`. Installs dependencies, runs `pytest` (uploading the JUnit XML and raw stdout as a workflow artifact), then runs `python src/adls_client.py` end-to-end against the real public container.

If `lint` fails, `test` never runs.

## Dockerfile hardening notes

Each change in [Dockerfile](Dockerfile) has an inline comment explaining why. The high-level fixes versus the starter image:

- Switched the base image from `python:3.12` to `python:3.12-slim` to shrink the image and reduce the attack surface.
- Set `PYTHONDONTWRITEBYTECODE`, `PYTHONUNBUFFERED`, and pip cache flags so logs stream cleanly and the image doesn't carry pip caches.
- Copied `requirements.txt` and installed dependencies before copying the source so unrelated code edits don't bust the dependency layer cache.
- Added a non-root `app` user; the container no longer runs as root.
- Added a `.dockerignore` so `.git`, tests, caches, and CI metadata never enter the build context.
