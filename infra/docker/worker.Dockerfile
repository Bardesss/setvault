# syntax=docker/dockerfile:1.7

# Pin to bookworm: audiowaveform has no trixie package; bookworm deb is stable
FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# audiowaveform is not in Debian repos; download deb and install with its deps
RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg libmagic1 libchromaprint-tools tini ca-certificates curl \
      libmad0 libid3tag0 libgd3 \
      libboost-program-options1.74.0 libboost-filesystem1.74.0 libboost-regex1.74.0 \
    && curl -fsSL https://github.com/bbc/audiowaveform/releases/download/1.10.1/audiowaveform_1.10.1-1-12_amd64.deb \
         -o /tmp/audiowaveform.deb \
    && dpkg -i /tmp/audiowaveform.deb \
    && rm /tmp/audiowaveform.deb \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv
WORKDIR /srv
COPY pyproject.toml ./
COPY packages/core packages/core
COPY apps/worker apps/worker
RUN uv sync --no-dev
ENV PATH="/srv/.venv/bin:${PATH}"
USER 1000:1000
ENTRYPOINT ["tini", "--"]
CMD ["python", "-m", "setvault_worker.entrypoint"]
