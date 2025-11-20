set shell := ["bash", "-c"]

alias pytest := test

default:
    @just --list

setup:
    # Install UI deps (runs agent setup via npm postinstall)
    cd devops-agent && npm install

serve:
    # Start FastAPI dev server with reload
    cd devops-agent/agent && uv run src/main.py

test:
    # Run pytest suite
    cd devops-agent/agent && uv run --group dev pytest -q

fullstack:
    # Run Next.js UI + FastAPI agent together
    cd devops-agent && npm run dev

bootstrap-tools:
    # Download pinned Terraform/Checkov/tfsec/Infracost binaries into .tools/bin
    ./bootstrap-tools.sh

lint:
    # Placeholder for lint command
    echo "Add linting command when ready"

docker-build:
    docker build -t terraform-orchestrator -f infra/Dockerfile .

docker-run:
    docker run --rm --env-file devops-agent/agent/.env -p 8000:8000 \
        -v "$${PWD}:/app" terraform-orchestrator
