# SetVault

Self-hosted vault for DJ live sets. Upload FLAC/WAV/MP3, get waveforms,
metadata, and a private streaming player.

## Quick start (production)

Prereqs: Docker 24+, Compose v2.

```bash
cp .env.example .env
# Edit .env: set SECRET_KEY, BASE_URL, POSTGRES_PASSWORD, etc.

docker compose -f infra/docker/compose.yml up -d
```

Then open `http://localhost:8000` (or whatever `BASE_URL` you configured
behind your reverse proxy). The first user is created via the dev-seed
endpoint or by running an invite-redeem flow against the API.

The published images are multi-arch (amd64/arm64) and ship the SvelteKit
frontend bundled inside the web image — there is no separate frontend
container.

## Local development

```bash
# Backend (FastAPI + uvicorn, hot reload):
uv sync --all-extras --all-groups
uv run alembic upgrade head
uv run uvicorn setvault_web.main:app --reload --port 8000

# Frontend (SvelteKit dev server, hot reload on :4173):
cd frontend
npm install
npm run dev -- --port 4173
```

See `infra/docker/compose.dev.yml` for the Postgres + Redis + tusd stack
used during development.
