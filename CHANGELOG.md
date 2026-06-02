# Changelog

All notable changes to SetVault are documented here. Format adheres to
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0](https://github.com/Bardesss/setvault/compare/v0.1.2...v0.2.0) (2026-05-28)


### Features

* **api:** GET /api/me/home-summary for Phase 6A home KPI grid ([cd5d024](https://github.com/Bardesss/setvault/commit/cd5d024af4fd46e2798e00b6af57b254cdcee387))
* **bookmarks:** FilterBar + grouped-by-set list, restyled cards ([53180ee](https://github.com/Bardesss/setvault/commit/53180eef4e42a97cd8cafd93ca1483ca68423224))
* **components:** FilterBar + SetRow for library / search / bookmarks ([de381d0](https://github.com/Bardesss/setvault/commit/de381d098732d6ea5eeb063e1109d0c6666585c4))
* **components:** RoadmapTag for landing roadmap items ([d7efe43](https://github.com/Bardesss/setvault/commit/d7efe435a89f8b2ad1eb349b643520e83f682623))
* **components:** SectionHeader, KpiGrid+Kpi, ContinueCard, RecentCard ([1efa19b](https://github.com/Bardesss/setvault/commit/1efa19b02a4dec075f694b6b8f66e9e342cd52fd))
* **embed:** compact chrome with brand + Open in SetVault footer ([a7d4ddd](https://github.com/Bardesss/setvault/commit/a7d4ddd51ed4d25e4c546e0b682d3bb6e3fca926))
* **home:** rebuild to match 03-home mockup with KPI grid ([de58271](https://github.com/Bardesss/setvault/commit/de58271f1fc476c92f04c902bd8e03e2cb3971db))
* **invite:** auth-card design language ([be9e40a](https://github.com/Bardesss/setvault/commit/be9e40a407857e747d640b3059c90063696f4430))
* **landing:** port underground-terminal design to deployed site ([98a0bc1](https://github.com/Bardesss/setvault/commit/98a0bc12aa3a1efb0f63d51336d8446d167e1f5b))
* **library:** FilterBar header + list/grid toggle + SetRow ([a4a59ac](https://github.com/Bardesss/setvault/commit/a4a59ac8dacac18d40e9f066321ba1c578ddb4fd))
* **login:** auth-card design language with scanline shell ([4cc86cc](https://github.com/Bardesss/setvault/commit/4cc86cc805063a7fc8a98389bb200d6ed13ea0aa))
* **phase-6a:** first impressions + browse foundation ([21f04de](https://github.com/Bardesss/setvault/commit/21f04de89e372c969bb4761a714d2393812a0e85))
* **reset:** auth-card design language ([192594f](https://github.com/Bardesss/setvault/commit/192594f098e43482c01244013d19ae4c1b54d15a))
* **search:** FilterBar + grouped results design-language ([cf1f5f2](https://github.com/Bardesss/setvault/commit/cf1f5f2f2cfb626d807c613484b36391c947d17a))
* **shell:** TopBar + grouped NavRail per 03-home mockup ([9e3e6ac](https://github.com/Bardesss/setvault/commit/9e3e6ac4449557e91311e2b41c1442469bed4963))
* **shell:** TopBar + grouped NavRail wired into +layout.svelte ([602d503](https://github.com/Bardesss/setvault/commit/602d5036cfdbd8aff59b9f65f951409bd4918073))
* **site:** build-time copy of shared design assets for landing ([595b50f](https://github.com/Bardesss/setvault/commit/595b50fb929f3bfcd776a2e165e14721b4536081))
* **styles:** shared Phase 6A class patterns in components.css ([006adf5](https://github.com/Bardesss/setvault/commit/006adf5ba287560da35b5084c39bdf1f96e2a701))


### Bug Fixes

* **6a:** restore &lt;h1&gt; headings on embed + bookmarks ([2f5ec61](https://github.com/Bardesss/setvault/commit/2f5ec616b772f87a5c1e1e94556d810e853df12c))


### Documentation

* **6a:** design-language pointer in root README + design-package readme refresh ([1e7e8c3](https://github.com/Bardesss/setvault/commit/1e7e8c3bbdafd18b6fec1109d349ecd214d9d116))
* **readme:** bump version refs to v0.1.2 + 6A design-language section ([52602d0](https://github.com/Bardesss/setvault/commit/52602d002f10920419a453009e77146900c831dc))

## [0.1.2](https://github.com/Bardesss/setvault/compare/v0.1.1...v0.1.2) (2026-05-28)

### Features

- **Default HTTP port is now `1970`** (the year of David Mancuso's first
  Loft parties — the year the DJ live set as we know it was born) —
  previously `8000`. Applies to `SETVAULT_HTTP_PORT`, the bundled compose
  file's port mapping, the container's `EXPOSE`, the dev-stack uvicorn
  flag, and the bundled landing's quickstart copy. ([ce490ef](https://github.com/Bardesss/setvault/commit/ce490ef939fa52b5d3762626ee33d21f362ffce8))

  **Breaking change for existing deployments that didn't set
  `SETVAULT_HTTP_PORT` explicitly.** After pulling this version:
  - **If your reverse proxy hits `host:8000`** and you want zero
    operational change, add `SETVAULT_HTTP_PORT=8000` to your `.env`
    before `docker compose up -d`.
  - **If you want the new default**, update the reverse-proxy upstream
    to `host:1970` (or whatever you set `SETVAULT_HTTP_PORT` to) before
    bringing the stack back up.

## [0.1.1] — 2026-05-29

**Noob-friendly self-host.** v0.1.0 shipped two container images
(`setvault-web` + `setvault-worker`) and a six-line `.env` of required
secrets. v0.1.1 collapses that into a **single `setvault` container**
running uvicorn + RQ worker + watchdog under s6-overlay, with **three
required env vars** total and everything else defaulted inside the
image. The self-host compose file drops from six services to four
(`setvault` + `postgres` + `redis` + `tusd`).

### Container

- **Single image**: `ghcr.io/bardesss/setvault:0.1.1` replaces
  `setvault-web` + `setvault-worker`. (Old image names will not be
  republished going forward.)
- **s6-overlay PID 1** supervises uvicorn, the RQ worker, and the
  watchdog watcher. Per-process crashes auto-restart without taking
  down the container.
- **Container-init scripts** (`/etc/cont-init.d/`) run on every boot:
  - `01-defaults` — auto-generates `TUSD_HOOK_SECRET` if missing
    (persisted to `${SETVAULT_CONFIG_PATH}/.secrets`), synthesizes
    `DATABASE_URL` from `POSTGRES_PASSWORD` when no explicit URL is
    given, and chowns bind mounts to `PUID:PGID`.
  - `02-validate` — fails fast with a clear message if required env
    is missing.
  - `03-migrate` — runs `alembic upgrade head` once before any
    longrun starts, with retry-on-postgres-not-ready backoff.
- **Multi-arch fix**: per-arch native binaries (`audiowaveform`,
  `s6-overlay`) are selected from `$TARGETARCH` instead of being
  hardcoded to amd64. v0.1.0's tag attempt failed on the arm64 leg
  because of this; v0.1.1 builds both arches cleanly.
- **Workspace fix**: `packages/providers` (workspace member) is now
  copied into the build context. v0.1.0's `uv sync` failed at
  `Failed to parse entry: setvault-providers`.

### Configuration

- **Required env shrinks to 3**: `SECRET_KEY`, `POSTGRES_PASSWORD`,
  `BASE_URL`. Everything else is defaulted or auto-generated.
- `.env.example` rewritten to a 3-required + commented-optional
  layout (~40 lines, was ~70).
- `compose.example.yml` rewritten to 4 services (was 6).

### Migration from 0.1.0

If you ran v0.1.0:

1. `docker compose pull` — picks up new `setvault:0.1.1` image
2. Replace your `compose.yml` with the new `compose.example.yml`
   (services renamed, fewer of them)
3. Strip `TUSD_HOOK_SECRET` and `PUID`/`PGID` from your `.env` if you
   want — they're defaulted now
4. `docker compose up -d` — `alembic upgrade head` runs automatically
   on first boot

No data migration required; the database schema is unchanged from
0.1.0.

### Fixed

- v0.1.0 docker workflow could not publish on multi-arch tag pushes
  (#23 fix landed but didn't cover the arch issue). v0.1.1 fixes both.
- Old separate Dockerfiles deleted; only `infra/docker/Dockerfile`
  remains.

---

## [0.1.0] — 2026-05-28

**The inaugural release.** Eleven months of design, twenty-one merged
phase PRs, and one private group of DJ-music nerds finally getting the
self-hosted vault they always wanted. SetVault v0.1.0 is the first
publicly tagged build — multi-arch container images on GHCR, SBOMs on
every artifact, cosign signatures on every push.

### Why this exists

Mixcloud went paywall. SoundCloud kept rotting. 1001tracklists is a
read-only museum. Nothing on the market combines **lossless live-set
storage**, **time-coded tracklists**, **provider-enriched metadata**, and
a **private streaming player you actually own** — for the specific shape
of DJ live sets, not for individual tracks. SetVault is that
combination, self-hosted, GPL-3.0, ready to live behind your reverse
proxy.

### ✨ Highlights

- **Resumable multi-GB uploads** via tus.io — pause your laptop, resume
  on your phone
- **Paste-URL ingest** from YouTube / SoundCloud / Mixcloud / Internet
  Archive / Bandcamp via `yt-dlp` (SSRF-allowlisted, rate-limited)
- **Watch-folder auto-ingest** — drop files into a host directory and
  SetVault picks them up via `watchdog`
- **Time-coded tracklists** with paste-parse, OCR import, 1001tracklists
  scrape, and an in-player **M-key live add**
- **Provider-enriched metadata** — pluggable framework, MusicBrainz +
  Discogs + AcoustID shipped, response cache + per-field priority + locks
- **wavesurfer.js player** with variable speed (0.5×–2×, pitch-preserved),
  A↔B looping, persisted per-user position, and `mediaSession` controls
  that jump between tracklist entries
- **Engagement layer**: comments with `@mentions` and waveform markers,
  per-set + timestamped bookmarks, private notes, in-app + email
  notifications
- **Per-user RSS feeds** (favorites / recent / everything) with
  `ApiToken` auth and HMAC-signed short-TTL enclosure URLs
- **Embeddable `/embed/[slug]` player** with admin `embed_allowed` toggle
  and a dedicated per-route CSP
- **Installable PWA** with offline set-detail, audio cache cap (admin-
  configurable, oldest-first eviction) and a phone-width pass across the
  whole UI
- **Internationalization-ready** via Crowdin GitHub Integration — English
  source, de / es / fr / nl stubs in place
- **Hardened by default** — Argon2 password hashing, CSRF middleware,
  strict CSP + HSTS, SSRF allowlist on URL-rip, rate-limited login,
  `no-new-privileges` + `cap_drop: ALL` on every container

### Ingest

- ffmpeg → Opus transcode with EBU R128 loudness normalization
- waveform peak extraction cached on disk
- chromaprint dedup via AcoustID fingerprints
- per-`MediaRoot` naming templates
- URL-rip rate limit: 5/hour, 50/day per user

### Catalog

- LiveSet model with first-class Artists, Venues, Series, Parties, Tags,
  and MediaRoots
- Postgres full-text search across titles, artists, tags, venues
- Soft delete with a 14-day purge grace and a recycle-bin UI
- Bulk editor: `soft_delete` / `retag` / `move_root` over selected sets

### Player polish (§5D)

- Variable speed slider (0.5× – 2.0×, 0.05 step) with pitch preservation
- A↔B loop region (`[` set A, `]` set B, `\` clear) with visual band
- Playback rate persisted per user per set via `UserSetState`
- Keyboard: `space` play/pause, `←` `→` seek, `<` `>` rate ±0.05,
  `[` `]` `\` loop, `M` live-add tracklist entry

### Admin surface (§5C)

- Library webhooks with HMAC signing and exponential-backoff retries
- Scheduled tasks (cron-style + `rq-scheduler`)
- Storage health monitor (capacity per `MediaRoot`, oversized-set alarms)
- Watch-folder configuration UI with unmatched-file queue
- Streaming backup endpoint (`pg_dump` + `tar` over chunked response)

### PWA (§4C / §5E)

- Manifest + maskable icons + theme-color
- Service worker: cache-first static, network-first navigation, audio
  cache-first with capacity enforcement
- Offline set-detail page works after first online load
- Audio cap is admin-configurable; lowering it triggers immediate
  eviction via a `MessageChannel` round-trip
- Phone-width responsive across login / library / set detail / settings

### Distribution (§4B)

- Per-user RSS at `/api/feeds/{kind}/feed.rss?token=...` (kinds:
  `favorites`, `recent`, `everything`)
- `ApiToken` model with revocable tokens, listed in settings
- HMAC-signed enclosure URLs with admin-configurable TTL (default 1 h)
- Embeddable player at `/embed/[slug]` with per-route CSP allowing
  `frame-ancestors *`

### Internationalization

- Source strings: 145 keys in `frontend/src/lib/i18n/locales/en.json`
- de / es / fr / nl scaffolded; svelte-i18n falls back to English while
  Crowdin contributors catch up
- Crowdin GitHub Integration handles both directions automatically

### Tech stack

- **Backend**: FastAPI on async SQLAlchemy 2 (Postgres 16), Redis 7 + RQ
  + `rq-scheduler`, Alembic migrations, structlog
- **Frontend**: SvelteKit (adapter-static, bundled into the web image),
  wavesurfer.js 7, svelte-i18n
- **Workers**: Python `rq` worker + a `watchdog`-driven watcher process
- **Uploads**: tusd resumable-upload sidecar
- **Audio**: ffmpeg, fpcalc (chromaprint), pytesseract
- **Containers**: multi-arch (`linux/amd64`, `linux/arm64`) images on
  `ghcr.io`

### Security

- Argon2 password hashing
- HMAC-signed short-TTL share URLs (`signed_urls.py`)
- Pure-ASGI CSRF + SecurityHeaders middleware (no `BaseHTTPMiddleware`
  task-group races)
- Strict CSP, HSTS, X-Frame-Options DENY, Permissions-Policy locked down
- SSRF allowlist on URL-rip ingest
- Rate-limited login + URL-rip via Redis
- `security_opt: no-new-privileges` + `cap_drop: ALL` on every container
- `yt-dlp` exact-pinned with an `infra/scripts/update-yt-dlp.sh` updater

### Release engineering (§5F)

- Conventional commits + [release-please](https://github.com/googleapis/release-please)
  managing future tags and `CHANGELOG.md`
- Container images published to GHCR on every `v*` tag
- **SBOM** (CycloneDX, via Syft) attached to each release
- **Cosign keyless signatures** on each published image (verify with
  `cosign verify --certificate-identity-regexp ...`)
- `infra/docker/compose.example.yml` — copy-paste self-host stack that
  pulls from GHCR (no local build needed)
- Expanded `.env.example` documenting every configurable variable

### Known follow-ups (post-v0.1.0)

- Real-device PWA install screenshots (headless tests cover manifest +
  icons + SW registration; `beforeinstallprompt` requires a real device)
- Crowdin translations land back as they're completed by contributors
- Phase 6 — ingest power tools (interactive search, monitored entities,
  quality preferences, upgrade-available flow)
- Phases 7–11 per `README.md` (Subsonic, casting, Sonos, smart playlists,
  OIDC + forward-auth)

### Co-authored

The vast majority of this codebase was pair-programmed with Claude Code
(Opus 4.x). Every change is reviewed, tested, and shipped by the human
maintainer — but the commits are marked with `Co-Authored-By` and the
contribution shape is honest.

---

[0.1.1]: https://github.com/Bardesss/setvault/releases/tag/v0.1.1
[0.1.0]: https://github.com/Bardesss/setvault/releases/tag/v0.1.0
