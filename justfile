set shell := ["bash", "-c"]

alias pytest := test

default:
    @just --list

setup:
    # Create venv and install dependencies
    python -m venv .venv
    . .venv/bin/activate && pip install -r requirements.txt

serve:
    # Start FastAPI dev server with reload
    . .venv/bin/activate && uvicorn app.main:app --reload

test:
    # Run pytest suite
    . .venv/bin/activate && pytest -q

lint:
    # Placeholder for lint command
    echo "Add linting command when ready"

docker-build:
    docker build -t terraform-orchestrator -f infra/Dockerfile .

docker-run:
    docker run --rm --env-file .env -p 8000:8000 \
        -v "$${PWD}:/app" terraform-orchestrator

agui:
    # Launch AG-UI dojo (assumes repo cloned at ../ag-ui)
    command -v pnpm >/dev/null || { echo "pnpm is required. Install via 'corepack enable'."; exit 1; }
    cd ../ag-ui && AGENT_FRAMEWORK_PYTHON_URL=http://localhost:8000/agui pnpm turbo run dev --filter=demo-viewer
