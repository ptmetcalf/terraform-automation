FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

ENV TOOLS_INSTALL_DIR=/opt/terraform-tools/bin
ENV PATH="${TOOLS_INSTALL_DIR}:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    unzip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app
COPY docs /app/docs
COPY infra /app/infra

RUN python - <<'PY'\nfrom app.services.tool_installer import ensure_tool_binaries\nensure_tool_binaries()\nPY

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
