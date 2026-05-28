# syntax=docker/dockerfile:1.7

# ── Frontend stage ──────────────────────────────────────────────────────────
# Builds the SvelteKit app with @sveltejs/adapter-static. The adapter is
# configured (in frontend/svelte.config.js) to emit the static SPA bundle to
# ../apps/web/src/setvault_web/static (relative to the frontend dir). We
# preserve that relative layout inside the stage so the build writes to a
# stable path we can COPY into the runtime image.
FROM node:20-alpine AS frontend
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json frontend/
RUN cd frontend && npm ci
COPY frontend frontend/
# Pre-create the target directory so adapter-static can write into it. The
# real apps/web tree lives in the next stage; here we only need a sibling
# directory at /build/apps/web/src/setvault_web/static for the build output.
RUN mkdir -p /build/apps/web/src/setvault_web/static
RUN cd frontend && npm run build

# ── Base + Python deps ──────────────────────────────────────────────────────
# Pin to bookworm: audiowaveform has no trixie package; bookworm deb is stable
FROM python:3.12-slim-bookworm AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
# audiowaveform is not in Debian repos; download deb and install with its deps
RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg libmagic1 libchromaprint-tools tini ca-certificates curl \
      tesseract-ocr \
      libmad0 libid3tag0 libgd3 \
      libboost-program-options1.74.0 libboost-filesystem1.74.0 libboost-regex1.74.0 \
    && curl -fsSL https://github.com/bbc/audiowaveform/releases/download/1.10.1/audiowaveform_1.10.1-1-12_amd64.deb \
         -o /tmp/audiowaveform.deb \
    && dpkg -i /tmp/audiowaveform.deb \
    && rm /tmp/audiowaveform.deb \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv

FROM base AS deps
WORKDIR /srv
COPY pyproject.toml uv.lock ./
COPY packages/core/pyproject.toml packages/core/pyproject.toml
COPY packages/providers/pyproject.toml packages/providers/pyproject.toml
COPY apps/web/pyproject.toml apps/web/pyproject.toml
COPY apps/worker/pyproject.toml apps/worker/pyproject.toml
RUN uv sync --frozen --no-install-project || uv sync --no-install-project

FROM deps AS runtime
# apps/worker/pyproject.toml is inherited from the deps stage above so
# the workspace member stays discoverable without dragging in worker src.
COPY packages/core packages/core
COPY packages/providers packages/providers
COPY apps/web apps/web
# Replace the placeholder static dir with the SvelteKit build output.
COPY --from=frontend /build/apps/web/src/setvault_web/static apps/web/src/setvault_web/static
RUN uv sync --no-dev --package setvault-web
ENV PATH="/srv/.venv/bin:${PATH}"
WORKDIR /srv/apps/web
USER 1000:1000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health').read()"
ENTRYPOINT ["tini", "--"]
CMD ["uvicorn", "setvault_web.main:app", "--host", "0.0.0.0", "--port", "8000"]
