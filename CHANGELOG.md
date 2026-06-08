# Changelog

All notable changes to SetVault are documented here. Format adheres to
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0](https://github.com/Bardesss/setvault/compare/v0.5.0...v0.6.0) (2026-06-08)


### Features

* **deploy:** single-container bundled mode + external datastores from one image ([f932c09](https://github.com/Bardesss/setvault/commit/f932c090210ebb694e1301121015eae390759497))
* **docker:** 00-mode cont-init resolves bundled/external + /data paths ([0e912d4](https://github.com/Bardesss/setvault/commit/0e912d430e9876bbafd3301174f3071bd4b1775f))
* **docker:** bundle tusd + Caddy proxy; uvicorn binds mode port ([8e48215](https://github.com/Bardesss/setvault/commit/8e4821567d9d4d67ab61ec8d6343d54d397533e3))
* **docker:** bundled Postgres + init-db oneshot; migrate via s6-rc deps ([980e79e](https://github.com/Bardesss/setvault/commit/980e79e0a250fb9e03b25deba705b1c801f13810))
* **docker:** bundled Redis s6 service (idle in external mode) ([daf972e](https://github.com/Bardesss/setvault/commit/daf972ea37f7729a4eeaebfe7842340ceafea11a))
* **docker:** external compose (pg18, tusd bundled) + compose.aio.yml + env docs ([0e31b80](https://github.com/Bardesss/setvault/commit/0e31b8040f878f990b79fac3e9f8833862c664f8))
* **docker:** install PG18, Redis, tusd, Caddy; mode-aware ENV ([06f06d6](https://github.com/Bardesss/setvault/commit/06f06d6e88c2bdb4cd25c68f42c6a67261383efb))
* **docker:** mode-detection lib + unit tests for bundled/external ([9eb2a44](https://github.com/Bardesss/setvault/commit/9eb2a440633834582de4588826ad77e45b68254f))


### Bug Fixes

* **docker:** external-mode boot — PG18 volume path + init-db readiness ([896168b](https://github.com/Bardesss/setvault/commit/896168b39803b89c979c01273e57661b8659ca03))
* **docker:** make bundled single-container image actually boot ([c75ac53](https://github.com/Bardesss/setvault/commit/c75ac53b8846c867158aa52fbbfc53c29affa39d))


### Documentation

* **readme:** bundled vs external install paths + PG18 caveat ([79893c4](https://github.com/Bardesss/setvault/commit/79893c42c9e0acedcc240bd7b47f290cbce1c161))
* **readme:** flip 6D to merged; bundled deploy is the sole this-release row ([6e81756](https://github.com/Bardesss/setvault/commit/6e81756ec6e770284c46495f357badb068b04e15))

## [0.5.0](https://github.com/Bardesss/setvault/compare/v0.4.0...v0.5.0) (2026-06-08)


### Features

* **admin:** connectors adopts AdminTable + EmptyState ([f185249](https://github.com/Bardesss/setvault/commit/f18524937201b3e2a1d38744523486bece3f80f9))
* **admin:** EmptyState, StatusBlock, AdminTable, AdminForm components ([a957a15](https://github.com/Bardesss/setvault/commit/a957a15ed002d7ebdef1d9bf22b8ce69f86d3601))
* **admin:** health adopts StatusBlock/AdminTable/EmptyState ([8955e7f](https://github.com/Bardesss/setvault/commit/8955e7fabb4d5948946c2b7b2f9b68f4344dfbd0))
* **admin:** jobs adopts AdminTable + EmptyState ([1460129](https://github.com/Bardesss/setvault/commit/1460129cabcfda2183acb7c578e083ead4a1812e))
* **admin:** providers adopts AdminTable + AdminForm ([d3fa1c9](https://github.com/Bardesss/setvault/commit/d3fa1c98641bb9220909fd03c9f0ea11bf14bc69))
* **admin:** recycle adopts AdminTable/EmptyState + shared buttons ([1a94ec6](https://github.com/Bardesss/setvault/commit/1a94ec672fefebd0d3c064b399e41cab31db3ee1))
* **admin:** restyle shell to shared chrome (banner + tabs) ([5af9d80](https://github.com/Bardesss/setvault/commit/5af9d80757487109db695a07a2c30661bb769202))
* **admin:** storage adopts AdminTable + EmptyState ([2ea0dcc](https://github.com/Bardesss/setvault/commit/2ea0dcc24138c66a2bc21488b1d932b1cc9a0d54))
* **admin:** system adopts StatusBlock/AdminTable ([b449d02](https://github.com/Bardesss/setvault/commit/b449d021d56bbf983adaae768f573dcd4de9e9de))
* **admin:** tasks adopts AdminTable/EmptyState + shared buttons ([5636fcf](https://github.com/Bardesss/setvault/commit/5636fcf0f7a447ed3dc5a320f773763a2e37fdb9))
* **admin:** unmatched adopts AdminTable/EmptyState + shared buttons ([eb7847d](https://github.com/Bardesss/setvault/commit/eb7847de0ea648005581fc428e8eee0fadae9fd7))
* **admin:** users adopts AdminTable + EmptyState ([c143822](https://github.com/Bardesss/setvault/commit/c143822f182bc3ff87e68de291e6ab5f5d6d5b73))
* **admin:** watch-folders adopts AdminTable/AdminForm/EmptyState ([14b0cbe](https://github.com/Bardesss/setvault/commit/14b0cbe4afe37987d742cb9f054a63f7134a182f))
* **admin:** webhooks adopts AdminTable/AdminForm/EmptyState ([234b607](https://github.com/Bardesss/setvault/commit/234b607b3ba1b4fac4a577454c573869e9b4cebe))
* **phase-6d:** shared admin components across 12 tabs + Settings + Sets/new ([1770f87](https://github.com/Bardesss/setvault/commit/1770f87c95c449fa4b29006ac4f0de8d0b342d4b))
* **sets-new:** design-language pass with shared TabStrip ([f3d4688](https://github.com/Bardesss/setvault/commit/f3d468811bb016d93bc2524f150184362188e31d))
* **settings:** TabStrip layout + shared form/status components ([b3a5bc7](https://github.com/Bardesss/setvault/commit/b3a5bc728c9384ecc3757a5ade989ffcbf973d06))
* **styles:** shared .btn:disabled state ([d707e4e](https://github.com/Bardesss/setvault/commit/d707e4edf57afd0460068c6ef15e5df60582b699))
* **styles:** shared admin chrome classes for Phase 6D ([fe83323](https://github.com/Bardesss/setvault/commit/fe833237787aff01b1357beaf9d2cff4608bb08e))


### Bug Fixes

* **admin:** restore muted style for unmatched picker no-matches row ([adb0e63](https://github.com/Bardesss/setvault/commit/adb0e63f370fbb809b68cf86ad09017097dc79da))
* **styles:** drop duplicate .btn-danger from Phase 6D block ([58366ca](https://github.com/Bardesss/setvault/commit/58366ca293eb499060b9c6e6d231751dad5c3cfb))


### Documentation

* **readme:** mark 6D admin/management as this release ([c784079](https://github.com/Bardesss/setvault/commit/c7840793030a7737b3dbaf27b1073bacf8f4e4dc))

## [0.4.0](https://github.com/Bardesss/setvault/compare/v0.3.0...v0.4.0) (2026-06-02)


### Features

* **phase-6c:** global persistent player + mobile mini/full-screen ([4814b9b](https://github.com/Bardesss/setvault/commit/4814b9b90eb0397f8c25e80ea5c80cf8abe4cc61))
* **player:** audio engine service (stores/audio.ts) for 6C ([9e7b0a1](https://github.com/Bardesss/setvault/commit/9e7b0a1890ab29b5bd0183517a30c1d293db65ba))
* **player:** AudioHost — init engine + app-wide shortcuts (6C) ([029c0c7](https://github.com/Bardesss/setvault/commit/029c0c70f5c91ef1af889f428fc703b8b9dd8339))
* **player:** FullScreenPlayer overlay + fullscreen guard (6C) ([697edd4](https://github.com/Bardesss/setvault/commit/697edd4f8ca12f93c2795a831574900d999c91d4))
* **player:** rewrite MiniPlayer as persistent bottom-sheet (6C) ([563e9dd](https://github.com/Bardesss/setvault/commit/563e9dd7f78ae85ca530482611af8e2b46c38d8e))
* **player:** slim set-page Player onto the audio service (6C) ([5e597a7](https://github.com/Bardesss/setvault/commit/5e597a7a67ffe3ad65cbf9974457b73d8f9b1eed))
* **player:** Waveform view bound to the shared audio element (6C) ([7c16b80](https://github.com/Bardesss/setvault/commit/7c16b809f3cf9f52b6c0b99c7cf975668dff67c1))
* **styles:** mobile mini-player + full-screen player classes (6C) ([c3d680b](https://github.com/Bardesss/setvault/commit/c3d680b917863f2a5dcca7f4f8daeb1a89ba2bb6))


### Bug Fixes

* **player:** attach engine &lt;audio&gt; to the DOM so playback starts (6C) ([a0abc93](https://github.com/Bardesss/setvault/commit/a0abc93d79643c09ef43553ad0e71179c5b51925))
* **player:** render Waveform from URL, not the engine element (6C) ([6bcf36a](https://github.com/Bardesss/setvault/commit/6bcf36a2fc1c709695743c71aef079af6ab22e3d))
* **sw:** don't cache.put 206 range responses — fixes audio playback (6C) ([ee44c64](https://github.com/Bardesss/setvault/commit/ee44c64af93f7d8d45a5d2c1b58161cc2df49fbd))


### Documentation

* **readme:** mark 6C global persistent player as this release ([5d2cf4c](https://github.com/Bardesss/setvault/commit/5d2cf4cade7ef45e8eb69e84f14345e0116765a5))

## [0.3.0](https://github.com/Bardesss/setvault/compare/v0.2.0...v0.3.0) (2026-06-02)


### Features

* **engagement:** TabStrip + SidePanel; flat prop on engagement components ([4306d13](https://github.com/Bardesss/setvault/commit/4306d138d4e5936fbc21ca617a0ed30b4da428c5))
* **phase-6b:** set detail rebuild + engagement SidePanel + tracklist editor ([2cda1bc](https://github.com/Bardesss/setvault/commit/2cda1bc0191f76460f2fa4bde1d467c3493f61db))
* **player:** restyle to wave-stage + transport-bar (01 mockup) ([cb6ee1f](https://github.com/Bardesss/setvault/commit/cb6ee1ffcff9eaf4d17c26c69e5807713bba2561))
* **set-detail:** rebuild to 01 mockup — hero + body-grid + SidePanel ([7bb077f](https://github.com/Bardesss/setvault/commit/7bb077fe72cd26a85bf1b39117410669f6868c02))
* **styles:** set-detail layout classes for Phase 6B ([6c28490](https://github.com/Bardesss/setvault/commit/6c28490d115c38fa1b1bbe0aaec274f0a6b7bca2))
* **tracklist:** accept bracketed [hh:mm:ss] paste timestamps ([cb55ef3](https://github.com/Bardesss/setvault/commit/cb55ef3b7b778dc744f2503088b4e6cddc660552))
* **tracklist:** restyle rows to .track-row (01 mockup) ([9c89515](https://github.com/Bardesss/setvault/commit/9c8951556f8d264d0b6caee6d1d06ce4e7f6c294))


### Documentation

* **readme:** roadmap to Phase 6 mockup-parity split + renumber 7–12 ([6685acd](https://github.com/Bardesss/setvault/commit/6685acd82afd27a7136e31a11561b994612517bb))

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
