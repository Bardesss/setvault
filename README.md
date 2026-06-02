# SetVault

[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.2-brightgreen.svg)](CHANGELOG.md)
[![Container: ghcr.io](https://img.shields.io/badge/container-ghcr.io-1f6feb.svg)](https://github.com/Bardesss/setvault/pkgs/container/setvault)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-ff69b4.svg)](https://github.com/Bardesss/setvault/issues)

**Self-hosted vault for DJ live sets.** Upload FLAC/WAV/MP3 (or rip from
YouTube / SoundCloud / Mixcloud / Internet Archive / Bandcamp via
`yt-dlp`), get waveforms, EBU R128 loudness normalization, time-coded
tracklists, provider-enriched metadata, comments with waveform markers,
per-user RSS feeds, an embeddable player, and an installable PWA.

> Think **Mixcloud × 1001tracklists × Plex-style self-hosted media
> server** — but for DJ live sets specifically, not for individual
> tracks.

---

## ✨ What's in the box (v0.1.0)

| Area | What you get |
|---|---|
| **Ingest** | Resumable multi-GB uploads (tus.io) · paste-URL rip from YT/SC/Mixcloud/Archive/Bandcamp · watch-folder auto-ingest · ffmpeg → Opus + R128 normalize · waveform peaks · chromaprint dedup |
| **Catalog** | LiveSets · Artists · Venues · Series · Parties · Tags · MediaRoots with naming templates · Postgres FTS · recycle bin (14-day grace) · bulk editor |
| **Tracklists** | Per-set editor · reorder + time-shift · M-key live add · paste-parse · 1001tracklists scrape · Tesseract OCR |
| **Enrichment** | Pluggable providers · MusicBrainz · Discogs · AcoustID · per-row Resolve + Bulk resolve + AcoustID "ID this" |
| **Player** | wavesurfer.js · variable speed 0.5×–2× (pitch-preserved) · A↔B loop · `mediaSession` prev/next jumps tracklist entries · per-user persisted state |
| **Engagement** | Comments w/ @mentions + waveform markers · per-set + timestamped bookmarks · private notes · in-app + email notifications |
| **Distribution** | Per-user RSS feeds (favorites / recent / everything) · HMAC-signed short-TTL enclosures · `/embed/[slug]` public player with admin toggle |
| **PWA** | Installable manifest + maskable icons · offline set-detail · audio cache with admin-configurable cap + oldest-first eviction · phone-width across all screens |
| **Admin** | Library webhooks (HMAC + retries) · scheduled tasks · storage-health monitor · streaming backup endpoint · audit log |
| **i18n** | English source + Crowdin GitHub Integration · de / es / fr / nl ready (English fallback while community catches up) |
| **Ops** | Multi-arch GHCR images · SBOM (CycloneDX) + cosign signatures on every release · Alembic migrations · `no-new-privileges` + `cap_drop: ALL` on every container |

Full feature list and release notes: [CHANGELOG.md](CHANGELOG.md).

---

## 🚀 Quick start (Docker compose, GHCR pull)

One image. Three required env vars. Four containers in the stack.
Zero local build — pulls the published multi-arch image from GitHub
Container Registry.

**Prereqs:** Docker 24+, Compose v2, ~2 GB RAM for the stack, and disk
space for your live-set library.

```bash
# 1. Grab the example compose + env files
curl -L -o compose.yml \
  https://raw.githubusercontent.com/Bardesss/setvault/main/infra/docker/compose.example.yml
curl -L -o .env \
  https://raw.githubusercontent.com/Bardesss/setvault/main/.env.example

# 2. Edit .env — exactly three required vars:
#    SECRET_KEY, POSTGRES_PASSWORD, BASE_URL.
#    Generate a strong SECRET_KEY:
openssl rand -base64 48

# 3. Pull and start
docker compose pull
docker compose up -d

# 4. Watch logs until the setvault container is ready
docker compose logs -f setvault
```

Open `http://localhost:1970` (or whatever `BASE_URL` points at behind
your reverse proxy). On first boot, the container:
- auto-generates an internal `TUSD_HOOK_SECRET` (persisted to `${SETVAULT_CONFIG_PATH}/.secrets`)
- synthesizes `DATABASE_URL` from your `POSTGRES_PASSWORD`
- runs `alembic upgrade head`
- starts uvicorn + RQ worker + watchdog under s6-overlay

The first admin is created by enabling `SETVAULT_DEV_SEED=1` for one
boot, hitting `/api/dev/seed-e2e`, then unsetting it — or by running
an invite-redeem flow against the API.

### Image reference

| Image | Pull | Arches |
|---|---|---|
| SetVault (web + worker + watcher under s6-overlay) | `ghcr.io/bardesss/setvault:0.1.2` | `linux/amd64` + `linux/arm64` |
| `:latest` mirrors the most recent tag. | | |

### Verify signatures (optional but encouraged)

Every release image is signed with cosign (keyless, via GitHub OIDC).

```bash
cosign verify ghcr.io/bardesss/setvault:0.1.2 \
  --certificate-identity-regexp "https://github.com/Bardesss/setvault/.github/workflows/docker.yml@.*" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

SBOMs (CycloneDX JSON) are attached to each GitHub Release.

---

## ⚙️ Configuration

All configuration is via environment variables loaded from `.env`. Only
three are required — everything else is defaulted inside the image or
synthesized at first boot.

| Variable | Required | Default | What it does |
|---|---|---|---|
| `SECRET_KEY` | ✅ | — | Signs session cookies + HMAC URLs. **Rotate ⇒ all sessions invalidated.** |
| `POSTGRES_PASSWORD` | ✅ | — | Postgres password. Used by both the postgres container and the auto-synthesized `DATABASE_URL`. |
| `BASE_URL` | ✅ | — | Public URL the app is served from (used in emails, RSS feeds, embed URLs) |
| `DATABASE_URL` | optional | synthesized from POSTGRES_* | Set directly if pointing at an external postgres |
| `REDIS_URL` | optional | `redis://redis:6379/0` | RQ queue + rate-limit store |
| `TUSD_HOOK_SECRET` | optional | auto-generated on first boot | Shared secret tusd uses when calling back into setvault |
| `SETVAULT_*_PATH` | optional | `./.data/*` | Host paths for db / redis / media / cache / config / watch |
| `SETVAULT_VERSION` | optional | `latest` | Pin to a specific image tag |
| `SETVAULT_HTTP_PORT` | optional | `1970` | Host port the setvault service binds (1970 — year of the first DJ live set) |
| `SETVAULT_DEV_SEED` | optional | unset | If `1`, enables `/api/dev/seed-e2e` for first-admin creation. Unset in production. |
| `PUID` / `PGID` | optional | `1000` / `1000` | Container user/group for bind-mount permissions |

### Reverse-proxy tips

- Set `BASE_URL` to your public HTTPS URL so signed enclosures and
  invite links resolve.
- Forward `X-Forwarded-Proto` and `X-Forwarded-For`.
- The web service listens on port `1970`; tusd is internal-only and
  reached via the web service at `/uploads/`.

---

## 🔄 Upgrading

```bash
# Pull the new tag
docker compose pull

# Migrations run automatically on web container start.
docker compose up -d
```

Always read the [CHANGELOG](CHANGELOG.md) for any breaking-change notes
before bumping a major or minor version.

---

## 💾 Backup & restore

The admin backup endpoint streams a single tarball containing a fresh
`pg_dump` + your media files.

```bash
# Authenticated admin session required
curl -fsSL -o setvault-backup-$(date +%F).tar \
  -b 'session=...' -H 'X-CSRF-Token: ...' \
  https://your-instance/api/admin/backup
```

Restore is documented in the wiki (post-v0.1.0). Until then: untar,
`psql < dump.sql`, restore media directories under each `MediaRoot.host_path`.

---

## 🌐 Translations

SetVault is translation-ready via [Crowdin](https://crowdin.com). The
project lives at **https://crowdin.com/project/setvault** — contributions
are welcome.

**To translate:**

1. Sign in (or create a free account) at
   [crowdin.com/project/setvault](https://crowdin.com/project/setvault).
2. Pick a target language (or request a new one from a maintainer).
3. Translate the strings in the in-browser editor.

**How translations flow back:** Crowdin's GitHub Integration handles
both directions — English source pushes up automatically when new keys
land on `main`, and Crowdin opens a PR back with the translated locale
JSON when contributors are done.

**Tips:** `{placeholders}` must stay intact and in matching position;
status badges and keyboard hints are short by design — keep them short.

---

## 🛠 Local development

```bash
# Backend (FastAPI + uvicorn, hot reload):
uv sync --all-extras --all-groups
uv run alembic upgrade head
uv run uvicorn setvault_web.main:app --reload --port 1970

# Frontend (SvelteKit dev server, hot reload on :4173):
cd frontend
npm install
npm run dev -- --port 4173
```

The dev-stack compose file at `infra/docker/compose.dev.yml` runs
Postgres + Redis + tusd locally so the backend has services to talk to.

For the full self-hosted compose stack (web + worker + watcher + db +
redis + tusd), see `infra/docker/compose.yml` (builds from source) or
`infra/docker/compose.example.yml` (pulls from GHCR).

---

## 🏛 Architecture

```
                   ┌─────────────┐
   browsers ─────▶ │   web :1970 │ ─┐
                   └──────┬──────┘  │
                          │         │
            ┌─────────────┘         │
            ▼                       │
    ┌──────────────┐        ┌───────▼───────┐
    │ tusd /uploads│        │  worker (RQ)  │
    └──────────────┘        └───────┬───────┘
            │                       │
            │                       ▼
            │               ┌───────────────┐
            └──────────────▶│   watcher     │   (filesystem events)
                            └───────────────┘
                                    │
                ┌───────────────────┼──────────────────┐
                ▼                   ▼                  ▼
        ┌──────────────┐    ┌──────────────┐   ┌──────────────┐
        │ Postgres 16  │    │   Redis 7    │   │ ffmpeg+fpcalc│
        └──────────────┘    └──────────────┘   └──────────────┘
```

- **`apps/web`** — FastAPI + bundled SvelteKit
- **`apps/worker`** — RQ worker for transcode / waveform / enrichment
  jobs
- **`apps/worker` (watcher)** — `watchdog`-driven filesystem watcher
- **`packages/core`** — SQLAlchemy models, services, RQ job entrypoints
- **`packages/providers`** — metadata provider plugin package
  (MusicBrainz / Discogs / AcoustID)
- **`frontend/`** — SvelteKit source (built into `apps/web/static/`
  inside the web image)
- **`infra/migrations/`** — Alembic revisions
- **`infra/docker/`** — Dockerfiles + compose stacks

---

## 🎨 Design language

The visual identity — **Underground Terminal**: phosphor mint on deep
blue-black, Bricolage Grotesque + JetBrains Mono, dense modular layouts,
keyboard-native interactions — lives in `frontend/design/`. That folder
holds the design tokens, font files, component patterns, and reference
mockups for every main screen plus the marketing landing.

Tokens, fonts, base, and shared component CSS are the single source of
truth, living at `frontend/src/lib/styles/*.css` and
`frontend/static/fonts/*.woff2`. Both the SvelteKit app (via
`+layout.svelte` imports) and the deployed landing page (via the
`scripts/build-site-assets.mjs` copy step run in CI) consume the same
files — no duplication, no drift.

Open `frontend/design/index.html` for a live local preview, or
`npx serve frontend/design` to browse from a local server. To preview
the deployed landing locally, run `npm run site:serve` from `frontend/`.

---

## 🔒 Security

- Argon2 password hashing
- Pure-ASGI CSRF + SecurityHeaders middleware (no Starlette
  `BaseHTTPMiddleware` event-loop races)
- Strict CSP, HSTS preload, X-Frame-Options DENY, Permissions-Policy
  locked down
- HMAC-signed short-TTL share URLs
- SSRF allowlist on URL-rip ingest (YT / SoundCloud / Mixcloud / Internet
  Archive / Bandcamp only)
- Rate-limited login + URL-rip via Redis
- `yt-dlp` exact-pinned (`packages/core/pyproject.toml`) — bump via
  `infra/scripts/update-yt-dlp.sh`
- `security_opt: no-new-privileges` + `cap_drop: ALL` on every container
- Audit log records every state-changing admin action

Report security issues privately to the maintainer rather than via
public GitHub issues.

---

## 📋 Status & roadmap

Each phase is implemented as a single PR against `main` (squash-merged)
with conventional commits driving the CHANGELOG.

| Phase | Status | Themes |
|---|---|---|
| 1 — Design & visual identity | ✅ merged | Tokens, top-5 mockups, landing direction |
| 2A — Foundations & Auth | ✅ merged | Monorepo, data model, local auth, invites |
| 2B — Pipeline & Catalog | ✅ merged | ffmpeg pipeline, FTS, audit |
| 2C — Frontend, Player & Production | ✅ merged | SvelteKit UI, tus uploads, Crowdin |
| 3A — Tracklist editor | ✅ merged | Per-set tracklists, parse, OCR |
| 3B — Provider framework + enrichment | ✅ merged | Pluggable providers, resolve UI |
| 3C — Engagement | ✅ merged | Comments, bookmarks, notes, notifications |
| 4A — URL rip | ✅ merged | Paste-URL ingest via `yt-dlp` |
| 4B — RSS + embed | ✅ merged | Per-user feeds, embeddable player |
| 4C — Mobile PWA polish | ✅ merged | Installable PWA, offline, phone widths |
| 5A — Watch-folder cluster | ✅ merged | §A3 + §A11 + §A12 |
| 5B — Backend backbone | ✅ merged | Recycle purge, naming templates, storage health, dedup |
| 5C — Admin UI surface | ✅ merged | Webhooks, scheduled tasks, health dashboard |
| 5D — Player polish + bulk editor | ✅ merged | Variable speed, A↔B loop, bulk actions |
| 5E — Tech debt | ✅ merged | Pure-ASGI middleware, yt-dlp pin, cache eviction e2e |
| 5F — Release engineering | ✅ merged | CHANGELOG, SBOM, cosign, GHCR, README rewrite, landing page (`v0.1.0`) |
| 5G — Noob-friendly single image | ✅ merged | Single `setvault` image (uvicorn + worker + watcher under s6-overlay), 3-required-env config, 4-service compose, `TARGETARCH` multi-arch fix (`v0.1.1`) |
| 6A — First impressions + browse | ✅ merged | Landing port, home, library, auth/embed/search design-language (`v0.2.0`) |
| **6B — Set detail + engagement** | **🚀 this release** | **Set-detail 3-column rebuild, engagement SidePanel, tracklist editor (`v0.3.0`)** |
| **6C — Global persistent player** | **🚀 this release** | **Persistent audio across navigation, bottom-sheet mini-player, full-screen player, MediaSession lockscreen (`v0.4.0`)** |
| 6D — Admin & management surfaces | ⏳ planned | Admin shell + 12 tabs, Settings, Sets/new |
| 7 — Ingest power tools | ⏳ planned | Interactive search, monitored entities, upgrade-available |
| 8 — Subsonic API + scrobbling | ⏳ planned | Compatibility |
| 9 — Casting | ⏳ planned | DLNA, Chromecast, listen-together rooms |
| 10 — Sonos | ⏳ planned | SMAPI sidecar |
| 11 — Smart playlists + similarity | ⏳ planned | pgvector, BPM/key detection, Snapcast |
| 12 — OIDC + forward-auth | ⏳ planned | SSO + final admin polish |

---

## 🤖 AI-assisted disclosure

SetVault is built with substantial help from AI coding assistants
(primarily Claude Code). Every change is reviewed, tested, and shipped
by the human maintainer — but the bulk of the code is co-authored with
an LLM and commits are marked with `Co-Authored-By: Claude ...`. If
that matters to your threat model or licensing posture, you now know up
front rather than discovering it later.

---

## 📄 License

GPL-3.0-or-later — see [LICENSE](LICENSE).

You are free to use, modify, and self-host SetVault. If you distribute
modified versions, the modifications must remain GPL-3.0. SetVault is
specifically not licensed for SaaS resale without the source being made
available to your users under the same terms.

---

## 🙏 Credits

- **wavesurfer.js** — the heart of the player
- **yt-dlp** — the URL-rip backbone
- **tusd** — resumable uploads done right
- **MusicBrainz / Discogs / AcoustID** — open music metadata
- **Crowdin** — translation tooling for the community

And to every test fixture, every CI red, and every `git rebase
--interactive` that got us here.
