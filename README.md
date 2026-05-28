# SetVault

Self-hosted vault for DJ live sets. Upload FLAC/WAV/MP3 (or rip from
YouTube/SoundCloud/Mixcloud via `yt-dlp`), get waveforms, EBU R128
loudness normalization, time-coded tracklists, and a private streaming
player. Built for a small private group of DJ-music enthusiasts.

Think Mixcloud × 1001tracklists × a Plex-style self-hosted media server —
but for **DJ live sets specifically**, not for individual tracks.

> **AI-assisted disclosure.** SetVault is built with substantial help from
> AI coding assistants (primarily Claude Code). Every change is reviewed,
> tested, and shipped by the human maintainer — but the bulk of the code
> is co-authored with an LLM and the commits are marked as such. If that
> matters to your threat model or licensing posture, you now know up
> front rather than discovering it later.

## Status

Iterating in numbered phases against the spec at
`docs/superpowers/specs/2026-05-08-setvault-design.md`. Each phase is its
own implementation plan under `docs/superpowers/plans/`.

| Phase | Status | What landed |
|---|---|---|
| 1 — Design & visual identity | ✅ merged | Design tokens, top-5 HTML mockups, landing-page direction (`frontend/design/`) |
| 2A — Foundations & Auth | ✅ merged | Monorepo (`apps/web`, `apps/worker`, `packages/*`), Postgres data model, local auth, invites + password reset |
| 2B — Pipeline & Catalog | ✅ merged | ffmpeg → Opus transcode · EBU R128 normalize · waveform peaks · artist / venue / series / party CRUD · LiveSet CRUD + streaming · Postgres FTS · audit events |
| 2C — Frontend, Player & Production | ✅ merged | SvelteKit UI (login, home, library, set detail with wavesurfer player, settings, admin) · tus.io resumable uploads · `svelte-i18n` + Crowdin sync · multi-arch bundled web image + production compose |
| 3A — Tracklist editor (raw) | ✅ merged | Track DB · per-set tracklist CRUD + reorder + time-shift · M-key live add · paste-parse · 1001tracklists scrape (admin-gated) · Tesseract OCR |
| 3B — Provider framework + enrichment | ✅ merged | Pluggable `setvault-providers` package · MusicBrainz / Discogs / AcoustID · response cache + per-field priority + locks · `/admin/providers` UI · per-row Resolve + Bulk resolve + AcoustID "ID this" |
| 3C — Engagement | ✅ merged | Comments (with `@mentions` + waveform markers) · per-set + timestamped bookmarks · private notes · in-app + email notifications |
| 4A — yt-dlp URL rip | ✅ merged | Paste-URL ingest tab on `/sets/new` · idempotent against platform IDs · 5/hour 50/day rate limit · SSRF allowlist (YT / SoundCloud / Mixcloud / Internet Archive / Bandcamp) |
| 4B — RSS feeds + embeddable player | ✅ merged | Per-user RSS (favorites / recent / everything) with token-scoped `ApiToken` · HMAC-signed short-TTL enclosure URLs · `/embed/[slug]` public player with `embed_allowed` admin toggle · per-route CSP exception |
| 4C — Mobile PWA polish | ✅ merged | Installable PWA (manifest + maskable icons) · service worker with cache-first/network-first strategies · `mediaSession` prev/next jumps tracklist entries · phone-width pass across all screens · offline audio cache with admin-configurable cap |
| 5 — Compatibility | ⏳ planned | Subsonic API + scrobbling |
| 6 — Casting | ⏳ planned | DLNA, Chromecast, listen-together rooms |
| 7 — Sonos | ⏳ planned | SMAPI sidecar |
| 8 — Polish | ⏳ planned | Smart playlists, pgvector similarity, BPM/key detection, Snapcast |
| 9 — OIDC + landing page release | ⏳ planned | OIDC, admin polish, GitHub Pages landing page |

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

## Translations

SetVault is translation-ready via [Crowdin](https://crowdin.com). The
project lives at **https://crowdin.com/project/setvault** — anyone is
welcome to contribute.

### How to translate

1. Sign in (or create a free account) at
   [crowdin.com/project/setvault](https://crowdin.com/project/setvault).
2. Pick a target language (or request a new one from a maintainer).
3. Translate the strings in the in-browser editor. You can leave
   suggestions even without proofreader access — they'll be reviewed.

### How translations flow back

The Crowdin GitHub Integration handles the round-trip:
- New English source strings in `frontend/src/lib/i18n/locales/en.json`
  are pushed to Crowdin automatically when they reach `main`.
- When translations are ready, Crowdin opens a PR back to this repo
  (typically on an `l10n_main` branch) with the locale JSON files.
- The SvelteKit app picks them up automatically once merged — no manual
  wiring per locale.

### Tips for translators

- The UI is **dense** by design (track lists, status badges, keyboard
  hints). Aim for compact translations where possible; layouts target
  English-sized strings but tolerate ~30% expansion (DE/NL/FR fit).
- `{placeholders}` in source strings (`Review {count} parsed entries:`)
  must stay intact and in matching grammatical position.
- Status badge labels (`raw`, `resolved`, `acoustid_confirmed`) and
  keyboard hints (`space play/pause`) are short by design — keep them
  short.

## License

MIT — see [LICENSE](LICENSE).
