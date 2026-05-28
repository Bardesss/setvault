# syntax=docker/dockerfile:1.7
#
# SetVault — single all-in-one image (v0.1.1+).
#
# Runs three processes under s6-overlay (PID 1):
#   - uvicorn      → FastAPI + bundled SvelteKit on :1970
#   - rq worker    → transcode / waveform / enrichment / bulk jobs
#   - watcher      → watchdog-driven WatchFolder ingest
#
# Multi-arch (linux/amd64 + linux/arm64). Per-arch native deps are
# selected from $TARGETARCH so QEMU builds don't try to install
# amd64 binaries on arm64.

ARG S6_OVERLAY_VERSION=3.2.1.0

# ── Frontend stage ──────────────────────────────────────────────────────────
FROM node:20-alpine AS frontend
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json frontend/
RUN cd frontend && npm ci
COPY frontend frontend/
RUN mkdir -p /build/apps/web/src/setvault_web/static
RUN cd frontend && npm run build

# ── Base: native deps + s6-overlay ──────────────────────────────────────────
# bookworm pin matches the audiowaveform deb's boost ABI.
FROM python:3.12-slim-bookworm AS base
ARG TARGETARCH
ARG S6_OVERLAY_VERSION
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

# Apt-installable deps (same on every arch).
RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg libmagic1 libchromaprint-tools tini ca-certificates curl xz-utils \
      tesseract-ocr \
      libmad0 libid3tag0 libgd3 \
      libboost-program-options1.74.0 libboost-filesystem1.74.0 libboost-regex1.74.0 \
    && rm -rf /var/lib/apt/lists/*

# audiowaveform — BBC publishes per-arch debs.
RUN case "${TARGETARCH}" in \
      amd64) AW_ARCH=amd64 ;; \
      arm64) AW_ARCH=arm64 ;; \
      *) echo "Unsupported TARGETARCH=${TARGETARCH}" >&2 && exit 1 ;; \
    esac && \
    curl -fsSL "https://github.com/bbc/audiowaveform/releases/download/1.10.1/audiowaveform_1.10.1-1-12_${AW_ARCH}.deb" \
      -o /tmp/audiowaveform.deb && \
    dpkg -i /tmp/audiowaveform.deb && \
    rm /tmp/audiowaveform.deb

# s6-overlay — process supervisor. Standard LinuxServer-style install.
RUN case "${TARGETARCH}" in \
      amd64) S6_ARCH=x86_64 ;; \
      arm64) S6_ARCH=aarch64 ;; \
    esac && \
    curl -fsSL "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz" -o /tmp/s6-noarch.tar.xz && \
    curl -fsSL "https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${S6_ARCH}.tar.xz" -o /tmp/s6-arch.tar.xz && \
    tar -C / -Jxpf /tmp/s6-noarch.tar.xz && \
    tar -C / -Jxpf /tmp/s6-arch.tar.xz && \
    rm /tmp/s6-noarch.tar.xz /tmp/s6-arch.tar.xz

RUN pip install --no-cache-dir uv

# ── Deps layer ──────────────────────────────────────────────────────────────
FROM base AS deps
WORKDIR /srv
COPY pyproject.toml uv.lock ./
COPY packages/core/pyproject.toml packages/core/pyproject.toml
COPY packages/providers/pyproject.toml packages/providers/pyproject.toml
COPY apps/web/pyproject.toml apps/web/pyproject.toml
COPY apps/worker/pyproject.toml apps/worker/pyproject.toml
RUN uv sync --frozen --no-install-project || uv sync --no-install-project

# ── Runtime ─────────────────────────────────────────────────────────────────
FROM deps AS runtime
COPY packages/core packages/core
COPY packages/providers packages/providers
COPY apps/web apps/web
COPY apps/worker apps/worker
COPY alembic.ini ./
COPY infra/migrations infra/migrations
COPY --from=frontend /build/apps/web/src/setvault_web/static apps/web/src/setvault_web/static
RUN uv sync --no-dev

# s6 services + container init scripts.
COPY infra/docker/s6-rc.d /etc/s6-overlay/s6-rc.d
COPY infra/docker/cont-init.d /etc/cont-init.d
RUN chmod +x /etc/cont-init.d/* /etc/s6-overlay/s6-rc.d/*/run /etc/s6-overlay/s6-rc.d/*/up 2>/dev/null || true

ENV PATH="/srv/.venv/bin:${PATH}"

# Defaults for the noob-friendly compose path. DATABASE_URL is left
# unset so cont-init can synthesize it from POSTGRES_PASSWORD; override
# directly if you point at an external postgres.
ENV REDIS_URL=redis://redis:6379/0 \
    POSTGRES_USER=setvault \
    POSTGRES_DB=setvault \
    POSTGRES_HOST=postgres \
    POSTGRES_PORT=5432 \
    SETVAULT_MEDIA_PATH=/srv/media \
    SETVAULT_CACHE_PATH=/srv/cache \
    SETVAULT_CONFIG_PATH=/srv/config \
    SETVAULT_WATCH_FOLDERS_PATH=/srv/watch \
    PUID=1000 \
    PGID=1000

WORKDIR /srv/apps/web

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:1970/api/health').read()"

EXPOSE 1970

ENTRYPOINT ["/init"]
