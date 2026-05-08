# SetVault — Design Spec

**Date:** 2026-05-08
**Status:** Draft, awaiting final user review

SetVault is a self-hosted live-set manager: upload or rip recorded DJ sets, manage artists/parties/venues/time-coded tracklists, enrich metadata via pluggable third-party APIs, play sets in-app, and stream them to other clients (DLNA, Sonos, Chromecast, Subsonic, RSS).

## 1. Scope & user model

- **Users:** small private group (target: <10 active users). Logins required. Shared library — every authenticated user sees the whole vault. Per-user state (favorites, history, bookmarks, comments, playlists, notes).
- **Scale:** target <10 users, <1000 sets. Architecture chosen so growth past this point doesn't require rewriting core pieces.
- **Hosting target:** Decent x86 server / NUC (4+ cores, 8+ GB RAM). Multi-arch Docker images so ARM64 users (Pi/UnRaid/Synology) work too.
- **Offline-first for core functions.** **Browsing the catalog and playing sets MUST work with zero internet access** — once the host is up on the LAN, no cloud dependency is required for daily use. See §13 for the full online-vs-offline matrix and the implementation rules that follow from this. Online dependencies (URL ripping, metadata enrichment, scrobbling, Chromecast, Sonos SMAPI) are clearly opt-in features that fail gracefully when the WAN is down — they never block core flows.
- **No public mode in v1.** No anonymous access, no public set pages, no community features (follows, likes, profiles).

## 2. Feature catalog

Features grouped A–M. All accepted unless explicitly marked out of scope.

### A. Ingest & acquisition
- **A1.** Direct upload (mp3, flac, wav, aac, m4a, opus). Drag-drop and batch.
- **A2.** URL rip via `yt-dlp` (YouTube, SoundCloud, Mixcloud, Twitch VODs, Bandcamp, anything yt-dlp covers).
- **A3.** Watch folder — drop a file → auto-imported. Multiple watch folders, each bound to a target root folder (J7).
- **A4.** Transcode on ingest. Keep original; produce streaming copy (Opus 128k default, 256k toggle).
- **A5.** Loudness normalization (EBU R128 / ReplayGain) — stored as offset, applied at playback (not baked into file).
- **A6.** Audio fingerprint dedup via chromaprint.
- **A7.** Background job queue with live progress in UI.
- **A8.** **Interactive search across audio sources** — query bar + filters → streamed candidate list from configured ingest sources. **Stock:** YouTube, Mixcloud, Internet Archive, SoundCloud. **Optional / limited:** Bandcamp, Twitch. Per candidate: source, uploader, duration, bitrate (when known), upload date, trust badge, "already in library" flag via chromaprint, inline tracklist preview when the source's own description contains one. One-click ingest seeds the LiveSet draft from search context (artist + venue + date the user queried) and source-intrinsic candidate fields (title, uploader, source URL); multi-select for batch. **Strictly an audio search + download flow** — IngestSources never enrich. Artist / Track / Release / tracklist enrichment is a separate post-ingest pass via the §6 Provider system (D1–D7 + LLM). **1001tracklists is not an IngestSource** — no audio; lives at C3 (paste-URL) and D6 (enrichment). UX + plugin architecture in §5.
- **A9.** **Monitored entities** — Artists, Parties, Venues, Series, or saved searches can be marked **monitored**. A periodic worker runs the same provider search as A8 and surfaces new matches in a "Discoveries" inbox. Per-monitor auto-ingest threshold: above `confidence_threshold`, ingest automatically; below, hold for human review. Drives the *arr-style "set it and forget it" loop.
- **A10.** **Quality / source preferences** — per-monitor or library-wide ranked list (e.g., FLAC > 320 mp3 > Opus 256k > Opus 128k; SoundCloud-verified > YouTube-official > YouTube-reup). When a better source surfaces for an existing set (chromaprint match), it lands in the Discoveries inbox as **upgrade available**. Auto-upgrade is opt-in per rule; original copy moves to recycle bin (J8) by default on upgrade.
- **A11.** **Hardlink + atomic move on ingest** — when a watch-folder file or staged download shares a filesystem with the target root, the pipeline hardlinks (not copies) into `originals/` and atomic-renames outputs into place. Avoids 2× disk and crash-half-written files. Falls back to copy-then-rename across filesystems.
- **A12.** **Unmatched-file inbox** — files arriving via watch folder that can't be auto-matched (no chromaprint hit, no filename hint, no metadata) land in an admin "Unmatched" queue rather than silently dropped or published as untitled. Resolve by linking to an existing set or creating a draft.

### B. Catalog / data model
- **B1.** Artists with aliases, bio, image, country, socials.
- **B2.** Parties / Events with name, edition, date, lineup.
- **B3.** Venues with city/area, country, geo, and **kind** (club, concert hall, arena, outdoor grounds, warehouse, boat, studio/radio, online/livestream, other) — covers indoor clubs through open-air festival grounds and radio-studio recordings.
- **B4.** Live Sets with title, date, set type (opener/closer/B2B/headline/warmup/unknown), duration, source.
- **B5.** Tags / Genres.
- **B6.** Time-coded tracklists with "ID — ID" support.
- **B7.** Track entries: timestamp, artist, title, label, mashup notes — backed by reusable Track entities enriched from external providers.
- **B8.** Reusable Track DB — same track across many sets links to one Track entity.
- **B9.** Labels & Releases linked to Tracks.
- **B10.** Series (e.g., "Essential Mix") grouping related Parties/Sets.

### C. Tracklist editor UX
- **C1.** Live mode: hit `M` while listening → adds entry at playhead.
- **C2.** Paste-and-parse raw tracklist text.
- **C3.** Bulk import from 1001tracklists URL (scrape, ToS-grey, personal-use disclaimer + rate limit).
- **C4.** Time-shift / stretch tracklist if set duration changes.
- **C5.** AcoustID fingerprint lookup per entry (ID-this button).
- **C6.** OCR of tracklist images.
- **C7.** LLM-assisted parsing of messy pasted text (user-configured API).

### D. Metadata enrichment (all providers user-configured)
- **D1.** Discogs.
- **D2.** MusicBrainz.
- **D3.** Beatport.
- **D4.** Spotify.
- **D5.** Last.fm / ListenBrainz.
- **D6.** 1001tracklists scrape (legal-grey; flagged in UI).
- **D7.** AcoustID/Chromaprint fingerprint service.

### E. Player
- **E1.** HTML5 player with waveform (wavesurfer.js v7, regions + timeline + minimap plugins, precomputed peaks).
- **E2.** Tracklist sidebar — current entry highlights live; click row → seek.
- **E3.** Keyboard shortcuts: Space, J/K/L, ←/→, ↑/↓, M (mark), B (bookmark), [/] (cycle entries), Shift+L/R (A↔B markers).
- **E4.** Variable speed 0.5–2× with pitch preservation (Web Audio + soundtouchjs).
- **E5.** Loop region (A↔B markers).
- **E6.** Resume from last position per user.
- **E7.** Time-stamped comments (YouTube-style) with markers on the waveform.
- **E8.** Per-user bookmarks.
- **E9.** Mini-player persists across navigation; mediaSession API for lockscreen control.

### F. Streaming / casting / multi-room
- **F1.** Chromecast support (Cast SDK button in browser).
- **F2.** DLNA/UPnP renderer via `minidlna` sidecar.
- **F3.** Snapcast for synced multi-room (optional, opt-in via compose override).
- **F4.** Listen-together — WebSocket-based synced playback room with chat.
- **F5.** Last.fm / ListenBrainz scrobbling per user.
- **F6.** Subsonic API (read endpoints) so existing apps (Substreamer, DSub, Symfonium, play:Sub) work natively.
- **F7.** AirPlay — out of scope.
- **F8.** Sonos SMAPI native music service — separate sidecar speaking SOAP, native browse/search/queue UX inside Sonos app.

### G. Browse / search
- **G1.** Full-text search across sets, tracklists, comments (Postgres FTS).
- **G2.** "Find sets containing track X" via the reusable Track DB.
- **G3.** Filter sidebar: artist/party/venue/venue-kind/year/genre/duration. Filter state in URL params.
- **G4.** Smart playlists (rule-based; jsonb query DSL).
- **G5.** Recently added / recently played widgets.
- **G6.** "Similar sets" via pgvector cosine similarity on tracklist embeddings (fallback to artist/tag overlap before ≥10 resolved entries).
- **G7.** **Bulk editor** — multi-select sets in any library view → bulk apply: move root folder, retag, change normalization target, re-enrich, re-fingerprint, soft-delete. Confirmation dialog with affected-rows summary; runs as a single tracked job in the queue.

### H. Group/social (within the small group)
- **H1.** Per-user history, favorites, watch-later.
- **H2.** Activity feed ("Bart added 3 sets today") with optional per-user subscription.
- **H3.** Comments at timestamps (threaded, `@mentions` notify).
- **H4.** Private notes per user per set (markdown).

### I. Mobile / PWA
- **I1.** Responsive web from the ground up.
- **I2.** PWA: web manifest, service worker, mediaSession API.
- **I3.** Offline cache of recently played (configurable cap, default 1 GB).

### J. Admin / ops
- **J1.** Per-user storage quotas.
- **J2.** Backup / export — DB dump + audio tarball; one-click + scheduled. Restore via CLI.
- **J3.** Reverse-proxy / subpath safe (`X-Forwarded-*`, `BASE_URL` env).
- **J4.** Per-user API tokens (scoped: `subsonic`, `rss`, `sonos`).
- **J5.** OIDC SSO (Authelia/Authentik/Keycloak/Pocket-ID compatible).
- **J6.** **SMTP outbound email** — admin-configured (host, port, username, password, encryption [STARTTLS/SSL/none], from address, from name, reply-to). Used for: account invites, password reset, email verification, `@mention` notifications, optional weekly activity digest. **Test-email button** in admin. **Graceful fallback when SMTP is not configured:** invite and password-reset flows show the one-time link in the admin UI for manual copy-paste — the app stays fully functional without an SMTP server. Per-user **notification preferences** (email vs in-app vs off, and which connector) for each notification kind. Outbound mail goes through the worker queue so SMTP timeouts never block web requests. SMTP is implemented as one row of the broader notification-connector framework (J12) — the admin UI lives under the **Connectors** tab.
- **J7.** **Configurable storage paths (sonarr/radarr/lidarr-style root folders).** Two distinct concerns:
  - **App-internal volumes** (`db`, `redis`, `cache`, `config`) — each independently bind-mountable to any host path via per-volume env override. Expected on local fast storage; small.
  - **Audio root folders** — admin-managed in the UI, **one or more**. Each entry: name, host path, optional max-bytes cap, default-for-ingest flag. New `LiveSet`s are assigned to a root folder at ingest (admin-set default when multiple); the per-set on-disk layout (`originals/`, `stream/`, `waveform/`, `thumbs/`) is rooted within whichever root folder the set lives in. Common shape: bulk audio on a mounted NAS / SMB / NFS / ZFS share as a root folder, DB and config on local SSD.
  - **Health checks** — periodic read/write probe per root folder; admin Storage tab surfaces unreachable / read-only / near-full roots prominently and the `/admin/system` view shows aggregate state.
  - **Remote path mappings** — when a worker container sees a different host path than the web container (e.g., worker on a different host that mounts the NAS at a different point), admin can configure source-path → app-path mappings, analogous to *arr's "Remote Path Mappings."
  - **Watch folders** (A3) are admin-managed alongside root folders, with the same path-config UX and may live on a different mount than any root folder.
  - **No paths hard-coded** in the image. Moving an existing deployment to new mount points is a stop-edit-start operation, not a rebuild.
- **J8.** **Recycle bin / soft-delete** — deleting a set sets `deleted_at` + `purge_after_at` and moves files to `<root>/.trash/<set_id>/` instead of unlinking. Sets in the bin disappear from library views and player but remain visible in admin Recycle bin tab. A scheduled job purges entries past their retention window (admin-configurable, default 14 days). Restore-now and purge-now per item. Bulk delete (G7) and quality-upgrades (A10) flow through the bin.
- **J9.** **Customizable on-disk naming per root folder** — token vocabulary `{Artist}/{Year}/{Party} - {Date}.{ext}`, with `{Artist} {Party} {Series} {Venue} {Date} {Year} {Slug} {Type} {SetId} {Ext}`. Default is opaque `originals/<set_id>/...` (UUID, safest). Per-root override switches to human-readable so Plex/Jellyfin/Symfonium browsing the same files shows sane names. Re-applying a template to existing sets is an explicit admin action that physically moves files and updates DB paths atomically.
- **J10.** **PUID / PGID container user mapping** — `setvault-web` and `setvault-worker` honor `PUID`/`PGID` env (default 1000:1000) so files written to bind-mounted host paths land owned by the host user, not `root`. Same convention as the LinuxServer.io image family — no chowning bind mounts after the fact.
- **J11.** **Health page** — single consolidated `/admin/health` view: storage roots (free space, last probe, status), provider connectivity (last success, error rate), notification connectors (last delivery), OIDC issuer reachability, queue depth + worker liveness, expired/expiring tokens, version + update availability. Items raise a top-bar dot when degraded. Same data exposed at `/api/health` for external monitoring (Uptime Kuma, healthchecks.io).
- **J12.** **Notification connectors** — pluggable outbound channels alongside SMTP (J6). Stock kinds: `webhook` (generic POST), `discord`, `telegram`, `apprise` (covers ~80 services), `slack`, `ntfy`, `gotify`. Each connector: name, kind, encrypted_config, scope filter (which event kinds + users + severities). SMTP from J6 is reframed as one connector with kind=`smtp`. Per-user `NotificationPreference` extends to pick which connector(s) to deliver via.
- **J13.** **Forward-auth header trust** — admin can enable trust of `X-Forwarded-User` / `X-Forwarded-Email` / `X-Forwarded-Groups` from a configured upstream proxy (Authelia / Authentik / Pocket-ID forward-auth mode). Requests carrying those headers from an allowlisted upstream IP/CIDR auto-authenticate (and auto-provision if admin-toggled). Headers are ignored when not enabled or arriving from outside the allowlist — no silent privilege escalation.
- **J14.** **Scheduled tasks UI** — admin tab listing all periodic jobs (re-check failed enrichment, prune temp, fingerprint orphans, monitor scans, root-folder health probes, recycle-bin purge, GitHub release poll): last run, next run, last result, manual "Run now". Backed by `rq-scheduler` introspection.
- **J15.** **Library refresh webhook on ingest** — admin-configured webhooks fire on set publish/update/delete. Pre-baked recipes for Plex (`/library/sections/<id>/refresh`), Jellyfin (`/Library/Refresh`), Emby, Subsonic-compatible peers, generic JSON POST. Lets neighboring stacks pick up new SetVault content without polling.
- **J16.** **"New version available" banner** — `setvault-scheduler` polls GitHub Releases (rate-limited, ETag-aware, daily) and surfaces a dismissible/snoozeable admin-only banner when a newer tag is available, with a link to the release notes. No auto-update — Docker users drive the upgrade.
- **J17.** **Translations / i18n via Crowdin** — frontend strings (`svelte-i18n`, JSON) and backend strings (`Babel`, gettext `.po`) sourced from `frontend/src/lib/i18n/` and `apps/web/i18n/`. **Crowdin for Open Source** (free for OSS projects) syncs via the Crowdin GitHub Action: pushes source strings on every commit to `main`, opens automated PRs back with new translations + completeness updates. Repo-root `crowdin.yml` declares the file mapping. All locale files bundled into the Docker image — runtime never reaches Crowdin, fully offline (§12). Per-user `User.locale` setting → admin default → `Accept-Language` → English. RTL languages supported from day 1 via `dir="rtl"` and CSS logical properties (Phase 1 Design constraint). **Hosted Weblate** is a drop-in alternative with the same JSON / `.po` workflow if Crowdin terms ever change. Detail in §15.

### K. Spicy nice-to-haves
- **K1.** BPM/key detection on ingest (essentia or aubio).
- **K2.** Podcast-style chapter markers in stream URLs (TracklistEntries → ID3 chapters → renders natively in podcast apps).
- **K3.** RSS feed per user (favorites / recently-added / everything; consume in any podcast app).
- **K4.** Embeddable player (`<iframe src="…/embed/<set>">`).
- **K5.** Stem separation (Demucs) — out of scope.

### L. Project deliverables
- **L1.** README at repo root: hero, screenshots, **system requirements** (see §13), Docker quickstart, env reference, per-provider walkthroughs (Discogs/MB/Beatport/Spotify/AcoustID/LLM), reverse-proxy examples (Caddy/Traefik/nginx), Sonos SMAPI setup, backup/restore, upgrade path, troubleshooting.
- **L2.** Landing page in `/site/`: SvelteKit static-adapter build, deployed to GitHub Pages via `.github/workflows/deploy-site.yml` on push to `main`. Sections: hero, what-is, feature gallery, screenshots, **system requirements**, quickstart, link to repo, link to docs. CNAME file for custom domain.

### M. Release & distribution
- **M1.** GitHub Releases on `v*` tag push: lint + test → multi-arch buildx (`linux/amd64`, `linux/arm64`) → push to GHCR as `ghcr.io/<owner>/setvault-{web,worker,sonos}:{vX.Y.Z, X.Y, X, latest}`.
- **M2.** Release notes via release-please (Conventional Commits → CHANGELOG.md → tagged release with notes).
- **M3.** SBOM + provenance attestations attached to releases.
- **M4.** Image signing via cosign keyless.
- **M5.** Compose example versioned at `infra/docker/compose.example.yml`.
- **M6.** Landing page reads latest release tag from GitHub API at build time and shows it in hero.

## 3. System architecture

### Deployment shape

Single `docker-compose.yml` orchestrating:

| Container | Purpose |
|---|---|
| `setvault-web` | FastAPI app — REST API, WebSocket, serves SvelteKit static build. |
| `setvault-worker` | Same Python image, runs `rq worker`. yt-dlp, ffmpeg, fingerprinting, scrapes, enrichment. Replicas scale horizontally. |
| `setvault-scheduler` | `rq-scheduler` for periodic jobs (re-check failed enrichment, prune temp). |
| `setvault-dlna` | `minidlna` sidecar pointed read-only at the audio volume. |
| `setvault-sonos` | Dedicated FastAPI service speaking Sonos SMAPI (SOAP). Lives on its own subdomain so Sonos's cloud has a stable HTTPS URL. |
| `postgres` | Postgres 16 with pgvector extension. |
| `redis` | Queue + pub/sub for live updates (job progress, listen-together, now-playing). |
| `caddy` *(optional)* | Bundled reverse proxy with auto-HTTPS via Let's Encrypt. Skippable if user has their own. |

All app containers (`setvault-web`, `setvault-worker`, `setvault-sonos`) honor `PUID` / `PGID` env (default `1000:1000`) and drop privileges at startup so files written into bind-mounted host paths land owned by the host user. LinuxServer.io-style — no post-hoc chowning of NAS mounts.

### Volumes

- **Audio (multi-root, *arr-style)** — the music. Largest. Implemented as one or more **MediaRoot** entries (admin-managed, see J7); each `LiveSet` belongs to exactly one root. Layout under each root:
  - `originals/<set_id>/<filename>` — untouched source
  - `stream/<set_id>.opus` — streaming copy
  - `waveform/<set_id>.json` — peaks for wavesurfer
  - `thumbs/<set_id>.jpg` — cover
  - `tmp/<job_id>/...` — cleaned after job
- `db` — Postgres data
- `redis` — Redis data
- `cache` — derived artifacts (regenerable but slow)
- `config` — provider keys, encrypted at rest with key derived from `SECRET_KEY`

Each app-internal volume above (`db`, `redis`, `cache`, `config`) is independently bind-mountable to any host path via env override (`SETVAULT_<NAME>_PATH`); root folders are managed at runtime in the admin UI rather than baked into compose. env

### Repo layout

```
setvault/
  apps/
    web/                # FastAPI (api + ws + serves frontend)
    worker/             # thin RQ worker entrypoint, reuses web's code
    sonos-smapi/        # SOAP service (own deployable)
  packages/
    core/               # domain models, services — imported by web + worker + sonos
    providers/          # pluggable metadata provider implementations
  frontend/             # SvelteKit, builds to apps/web/static
  site/                 # landing page (SvelteKit static-adapter, GH Pages target)
  infra/
    docker/             # Dockerfiles, compose.yml, compose.override.example.yml
    migrations/         # alembic
  .github/
    workflows/          # CI: test, build, release, deploy-site
  README.md
```

### Configuration model

- `.env` for secrets and host config (`SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `BASE_URL`, `OIDC_*` if present).
- All per-app runtime config (provider API keys, OIDC issuers, quotas, OIDC auto-provision toggle, etc.) in DB, edited via admin UI. Secret values encrypted at rest with a key derived from `SECRET_KEY`.

### Self-hosted assets (offline-first)

Per §12, the app shell never reaches the internet. All fonts (woff2), icon SVGs, JS chunks, CSS, and any other static assets are bundled into the `setvault-web` image and served by the FastAPI app. No CDN links, no `https://fonts.googleapis.com`, no external script tags. Service worker (I2) caches the shell aggressively so first-paint after a cold start is fast even on a network-isolated host.

### Stack

- **Backend:** FastAPI (Python 3.12), async. REST + WebSocket. SQLAlchemy 2.x + Alembic.
- **Worker:** RQ on Redis. Reuses backend code.
- **DB:** Postgres 16 + pgvector.
- **Frontend:** SvelteKit (TS). TanStack Query for server state, small Svelte store for player/queue. Builds to static — served by FastAPI.
- **Audio:** yt-dlp, ffmpeg, chromaprint/`fpcalc`, `pyacoustid`, librosa or essentia for BPM/key.
- **Reverse proxy:** Caddy bundled (skippable).
- **Multi-arch images:** linux/amd64 + linux/arm64.

## 4. Data model

All entities are Postgres tables. `*` = nullable. `jsonb` for provider blobs.

### Identity & auth
- **User** — id, email, username, display_name, password_hash*, oidc_subject*, role(admin|user), avatar_url, quota_bytes*, locale* (BCP-47 e.g. `en`, `nl`, `pt-BR`; null = use system default), email_verified_at*, last_seen_at
- **OidcProvider** — id, issuer_url, client_id, client_secret_encrypted, scopes, enabled, auto_provision
- **ApiToken** — id, user_id, name, token_hash, scopes (`subsonic`|`rss`|`sonos`|`api`), created_at, last_used_at, revoked_at*
- **EmailToken** — id, user_id* (null for invites that haven't been redeemed), email, kind(`invite`|`password_reset`|`verify_email`|`unsubscribe`), token_hash, payload jsonb (e.g., role for invites, notification kind for unsubscribe), expires_at, used_at*, created_by*, created_at
- **NotificationPreference** — PK(user_id, kind), channel(`email`|`in_app`|`both`|`off`), connector_id* (specific connector preference; null = any matching connector), updated_at — SMTP-specific configuration moved into the `NotificationConnector` table (J12); the row with kind=`smtp` carries host/port/encryption/from/reply-to inside `encrypted_config`

### Catalog
- **Artist** — id, name, slug, aliases[], bio, image_url, country, socials jsonb, external_ids jsonb, enrichment_status jsonb
- **Venue** — id, name, slug, kind(`club`|`concert_hall`|`arena`|`outdoor`|`warehouse`|`boat`|`studio`|`online`|`other`), city_or_area*, country*, lat*, lon*, capacity*, website* — `city_or_area` accepts both city names ("Amsterdam") and named outdoor sites ("Recreatiegebied Spaarnwoude"); `country` and geo are nullable so radio/online venues don't need them; `kind` drives icon/filter UX
- **Series** — id, name, slug, description, image_url
- **Party** — id, name, slug, series_id*, venue_id*, date*, description
- **LiveSet** — id, slug, title, party_id*, venue_id*, date*, set_type, duration_seconds, source_type, source_url*, media_root_id, audio_path, streaming_path, waveform_path, normalized_lufs*, description, uploaded_by, duplicate_of*, deleted_at*, purge_after_at* — `audio_path` etc. are root-relative and resolved against `MediaRoot.host_path` at read time, so a root folder can be remounted at a different host path without DB rewrites; `deleted_at`/`purge_after_at` drive the recycle bin (J8)
- **LiveSetArtist** — m2m: live_set_id, artist_id, position, role(main|b2b|support|vs)
- **Tag** — id, name, slug, kind(genre|mood|vibe|custom)
- **LiveSetTag** — m2m
- **Label** — id, name, slug, website, external_ids
- **Release** — id, title, label_id*, catalog_number*, release_date*, cover_url, external_ids
- **Track** — id, title, primary_artist_id*, additional_artists[]*, mix_name, label_id*, release_id*, year*, bpm*, key*, isrc*, external_ids, enrichment_status
- **ReleaseTrack** — m2m, ordered

### Tracklist & engagement
- **TracklistEntry** — id, live_set_id, position, start_seconds, end_seconds*, track_id*, raw_label, mashup_with[], edit_notes, status(raw|resolved|acoustid_confirmed), confidence*
- **TracklistComment** — id, live_set_id, user_id, parent_id*, start_seconds*, body, created_at
- **Bookmark** — id, user_id, live_set_id, position_seconds, label*
- **UserSetState** — PK(user_id, live_set_id), position_seconds, completed bool, updated_at
- **Favorite** — PK(user_id, live_set_id), created_at
- **ListeningHistory** — append-only: user_id, live_set_id, started_at, ended_at, last_position_seconds
- **Playlist** — id, user_id, name, slug, description, kind(manual|smart), query_dsl jsonb*
- **PlaylistEntry** — m2m, ordered
- **PrivateNote** — PK(user_id, live_set_id), body_md, updated_at
- **ActivityEvent** — id, user_id, kind, subject_type, subject_id, payload, created_at

### System
- **Job** — id (RQ id), kind, status, progress_pct, message, payload jsonb, result jsonb, initiated_by, created_at, started_at*, finished_at*
- **ProviderConfig** — id, provider_kind, name, enabled, priority, encrypted_config jsonb, created_at, updated_at — stores §6 metadata-enrichment provider configs (D1–D7 + LLM)
- **IngestSourceConfig** — id, source_kind, name, enabled, priority, encrypted_config jsonb, rate_limit_config jsonb, capabilities[] (cached from plugin advertisement), last_success_at*, last_error*, last_error_at*, auto_disabled_at*, created_at, updated_at — mirror of ProviderConfig for §5 IngestSource plugins (YouTube, Mixcloud, Internet Archive, SoundCloud, optional Bandcamp/Twitch). The interactive search Sources checklist and the monitor-rule source filter both read from rows where `enabled=true`.
- **ProviderResponse** — id, provider_kind, query_key (text), response jsonb, fetched_at, expires_at — cache for upstream calls (covers both metadata providers and ingest-source search responses; `provider_kind` namespace separates `meta:discogs` from `ingest:youtube`)
- **SetFingerprint** — id, live_set_id, fingerprint_hash, duration_seconds — for dedup
- **MediaRoot** — id, name, host_path, enabled, default_for_ingest bool, max_bytes*, naming_template* (token string per J9; null = opaque `<set_id>` layout), last_health_check_at*, last_health_status (`ok`|`unreachable`|`readonly`|`near_full`|`unknown`), created_at — *arr-style audio root folder; one or more, admin-managed in UI
- **WatchFolder** — id, name, host_path, target_media_root_id, enabled, created_at — admin-managed ingest source paths (A3), each pointing at a target root folder for the imported set
- **RemotePathMapping** — id, scope (`worker`|`watch`|`other`), from_path, to_path, created_at — translates host paths between the web container and worker/watch contexts when their mounts differ
- **MonitorRule** — id, kind(`artist`|`party`|`venue`|`series`|`search_query`), target_id*, query_dsl jsonb*, source_filter jsonb (which providers to consult), confidence_threshold float (auto-ingest above; inbox below), quality_profile_id*, enabled, last_run_at*, last_match_at*, created_by, created_at — drives A9 monitored auto-ingest
- **QualityProfile** — id, name, source_ranking jsonb (ordered list of source kinds + bitrate floors), upgrade_existing bool, created_at — referenced by MonitorRule and library defaults; powers A10
- **Discovery** — id, monitor_rule_id*, source_kind, source_url, candidate_metadata jsonb, fingerprint*, status(`new`|`ingested`|`dismissed`|`upgrade_available`), matches_existing_set_id*, confidence, surfaced_at, resolved_at*, resolved_by* — inbox of provider hits awaiting human or auto decision
- **UnmatchedFile** — id, host_path, watch_folder_id, fingerprint*, probed_metadata jsonb, status(`new`|`linked`|`dismissed`), linked_set_id*, surfaced_at, resolved_at*, resolved_by* — A12 unmatched inbox
- **NotificationConnector** — id, kind(`smtp`|`webhook`|`discord`|`telegram`|`apprise`|`slack`|`ntfy`|`gotify`), name, encrypted_config jsonb, enabled, scope_filter jsonb (event kinds + users + min severity), last_used_at*, last_status*, last_error*, created_at — J12 pluggable channels; SMTP from J6 is one row of this table
- **WebhookSubscription** — id, target_url, kind(`plex`|`jellyfin`|`emby`|`subsonic`|`generic`), events[] (publish/update/delete), encrypted_secret*, headers jsonb, enabled, last_fired_at*, last_status*, created_at — J15 library-refresh webhooks
- **ForwardAuthConfig** — single-row admin config: enabled, trusted_upstream_cidrs[], header_user, header_email, header_groups, auto_provision bool, group_role_mapping jsonb (J13)
- **AuditEvent** — id, actor_user_id*, actor_kind(`user`|`system`|`api_token`|`forward_auth`), action (string, e.g., `user.role_changed`, `media_root.removed`, `secret_key.rotated`), target_type*, target_id*, before jsonb*, after jsonb*, ip*, user_agent*, created_at — append-only audit trail; retention configurable, default 1 year (§14)
- **RateLimitOverride** — id, scope(`endpoint_tier`|`user`|`ip`|`source_kind`), key, limit_per_minute*, limit_per_hour*, lockout_after*, notes, created_by, created_at — admin overrides for the §14 default rate-limit tiers
- **SystemConfig** — single-row admin globals: default_locale (BCP-47, default `en`), enabled_locales[] (subset of locales whose translation completeness is above admin-set threshold; auto-populated from the bundled locale manifest), locale_completeness_threshold_pct (default 80), llm_draft_translations_enabled bool (default false), updated_at — home for future global toggles

### Indexes & search

- Postgres FTS `tsvector` columns on `Artist.name+aliases`, `LiveSet.title+description`, `Track.title+primary_artist`, `Party.name`. Updated via triggers.
- B-tree on `LiveSet.date desc`, `LiveSet.uploaded_by`, `TracklistEntry(live_set_id, start_seconds)`, `ListeningHistory(user_id, started_at desc)`.
- GIN on jsonb `external_ids` (lookup by provider id).
- pgvector column `LiveSet.embedding` (vector(384)) — averaged from resolved track embeddings; cosine ops for "similar sets."

### Design nuances

1. **Track DB reuse:** `TracklistEntry.track_id` references the canonical `Track`. "Sets containing track X" is one indexed query. Enriched metadata propagates everywhere automatically.
2. **`raw_label` preserved** on every TracklistEntry even after resolution — provides ground truth when a scrape/parse is wrong.
3. **Job table mirrors RQ state** so historical/failed jobs survive Redis flushes and the UI doesn't round-trip Redis to render history.
4. **Per-field provenance:** every enriched field on Artist/Track/Release records who set it (user / provider) + confidence + locked bool. Auto-enrichment never overwrites locked fields.

## 5. Ingest pipeline & background jobs

### Entry points

1. **Direct upload** — drag-drop or file picker, frontend uses tus.io for resumable chunked upload. Backend writes to `tmp/`, then commits.
2. **URL rip** — paste URL → yt-dlp job extracts audio + scrapes metadata (title, uploader, duration, original cover, description) → pre-fills LiveSet draft.
3. **Interactive search** — query bar across all configured upload-source providers (yt-dlp providers + 1001tracklists), candidate browser, one-click ingest. Detail in next subsection. Drives both A8 (manual) and A9 (monitored auto-ingest, via Discoveries inbox).
4. **Watch folder** — admin-configured host paths (one or more) scanned periodically + via inotify when available. Files matching by fingerprint to an existing set are deduped (or surface as A10 quality upgrades); files with no match land in the A12 unmatched inbox.

All four produce a draft `LiveSet` and queue the same downstream pipeline.

### Interactive search UX

Third tab on the user-facing "Add Set" page: `Upload` | `URL` | `Search`. (Watch folders are admin-managed, not a user-facing add path.)

- **Query bar + filters:** free-text query plus optional Artist / Venue / Year / Min duration / **Sources checklist** (populated from whichever IngestSource plugins admin has enabled — see plugin architecture below).
- **Streamed candidate list:** rows arrive as each source responds; per-source loading shimmer; one rate-limited or offline source doesn't block the others. Each row: source platform, uploader, title, duration, bitrate (when known), upload date, trust badge, actions.
- **Trust badges:**
  - `verified` — uploader is the artist's own channel (cross-checked via Spotify/MusicBrainz IDs) or a known label/event official account.
  - `known` — established mix channel above a follower-count threshold.
  - none — random uploader.
  - `duplicate` — chromaprint matches a set already in the library.
- **Already-in-library banner** — chromaprint match against existing fingerprints flags candidates that are dupes / re-uploads / quality upgrades.
- **Cross-candidate dedup** — when two candidates fingerprint-match each other, group them into a single row with `(N alternative uploads)` expand control. The user picks which source ingests.
- **Per-row actions:**
  - `Add` → hands off to A2 URL-rip pipeline with metadata pre-filled from search context.
  - `▸ TL` → expand inline preview: description, thumbnail, parsed tracklist (when the source's description contains one), and a "why this matched" line showing the matched alias / venue / date hits.
- **Multi-select + Add all** — batch ingest with one shared metadata anchor, runs as a single tracked job in the queue.
- **Metadata enrichment is a separate post-ingest flow.** Interactive search exists only to find audio and pull it down. Once a set is ingested, the §6 metadata-enrichment Providers (D1–D7 + LLM) populate canonical Artist / Track / Release entities and resolve tracklist entries. D6 (1001tracklists scrape) attaches tracklists during this phase; users can also paste a 1001tracklists URL via C3 to bind a tracklist to any existing set. None of these are IngestSources — they have no audio.
- **No-results state** — suggestions ("try without venue", "use artist alias", "expand year filter").

### Ingest source plugin architecture

Parallel to — and **disjoint from** — the §6 metadata Provider system. IngestSources find and download audio; Providers enrich Artist / Track / Release / tracklist data after the audio has landed. Neither does the other's job. Lives in `packages/ingest_sources/`. Each source implements:

```python
class IngestSource(Protocol):
    kind: str                       # "youtube" | "mixcloud" | "internet_archive" | "soundcloud" | ...
    capabilities: set[Cap]          # {SEARCH, DOWNLOAD, RATE_LIMITED, AUTH_REQUIRED}

    async def search(self, query: SearchQuery) -> AsyncIterator[Candidate]: ...
    async def fetch_candidate_details(self, url: str) -> CandidateDetails: ...
    async def download(self, url: str, dest: Path) -> DownloadResult: ...
```

`Candidate` is source-intrinsic — the data the platform already advertises about its own listing (title, uploader, duration, bitrate, upload_date, thumbnail_url, source_url, optional fingerprint hint). `CandidateDetails` extends it with description text, full formats list, and uploader-profile data — fetched on-demand for the `▸ TL` expand action and just before download. **Neither is enrichment.** Mapping a downloaded set to canonical Artists / Tracks / Releases, fetching bios, resolving tracklists against the Track DB — all of that is the §6 Provider system's job and runs as separate downstream jobs in the ingest pipeline.

**Stock implementations:**

| Source | Search | Download | Notes |
|---|---|---|---|
| `youtube` | yt-dlp `ytsearch:` | yt-dlp | High reliability; yt-dlp keeps up with site changes via weekly updates. |
| `mixcloud` | `api.mixcloud.com` REST (no key) | yt-dlp | DJ-mix-native; best signal-to-noise for our domain. |
| `internet_archive` | `advancedsearch.php` open API | direct HTTP | Hosts a lot of legit DJ archives (Essential Mix vault, BBC R1 sets). |
| `soundcloud` | yt-dlp `scsearch:` | yt-dlp | Fragile — new public API keys closed since 2017; rate limits hit faster than YouTube. |

**Optional / off by default:**

| Source | Why limited |
|---|---|
| `bandcamp` | No search API; site-scrape only; weak signal for DJ sets (Bandcamp's content is mostly singles/albums). |
| `twitch` | Helix API requires OAuth client_id/secret; no global VOD search — only channel-scoped. Useful when you know a specific DJ streams there. |

**Capability semantics:**

- `SEARCH` advertised → source appears in the interactive-search Sources checklist (A8) and is eligible for monitor scans (A9).
- `DOWNLOAD` advertised → source can handle URL-rip (A2) for matching URLs.
- A source can advertise `SEARCH` without `DOWNLOAD` (a discovery-only source) or vice versa. Mixing capabilities is normal — Mixcloud uses its public API for search and yt-dlp for download in the same plugin.
- **No metadata-enrichment capability exists in this protocol.** An IngestSource that has a rich description, channel bio, or anything else of that flavor exposes it via `fetch_candidate_details` for *display* during the search/preview step — it never writes to canonical Artist / Track / Release entities. That contract belongs to §6 Providers. 1001tracklists is **not** an IngestSource for this same reason; it lives in §6 as D6.

**Admin UI** — under **Providers → Ingest sources** subtab: enable/disable, reorder priority, configure auth (Twitch client_id/secret; future per-source API keys), set per-source rate limits. Per-source state — last successful query, error rate, last rate-limit timestamp — feeds the J11 Health page. A source failing for >24h auto-disables itself with an admin notification.

**Drop-in extensibility** — adding a new source (Beatsource, MixesDB, BBC Sounds, niche radio archives, …) is a new class file plus admin enable. The interactive search, monitored auto-ingest, and URL-rip flows all pick it up automatically based on capabilities.

### Storage hygiene on ingest

- **Same-FS hardlinks (A11):** when the source file (watch-folder drop, staged yt-dlp download) lives on the same filesystem as the target root folder, the pipeline `link()`s into `originals/<set_id>/` rather than copying. No 2× disk usage on hardlink-friendly setups.
- **Cross-FS fallback:** different filesystems → copy to a tmp dir on the *target* root's FS, then atomic-rename into place. Crash mid-write never produces a half-written file in the published path.
- **Output writes** (`stream/`, `waveform/`, `thumbs/`) all use the same tmp-then-rename pattern.
- **Recycle bin (J8):** "delete" moves the set's directory tree to `<root>/.trash/<set_id>/` and stamps `purge_after_at` on the row. Background job purges past the retention window.

### Pipeline (chained RQ jobs)

```
[ingest source]
    ↓
[probe]            ffprobe: duration, codec, bitrate, channels
    ↓
[fingerprint]      chromaprint/fpcalc → AcoustID → check Track DB + dedup
    ↓ (skip if exact dup unless user overrides)
[transcode]        ffmpeg → Opus 128k streaming copy (256k toggle)
    ↓
[normalize]        EBU R128 scan → store gain offset
    ↓
[waveform]         peaks JSON for wavesurfer.js (~1 KB/min)
    ↓
[autotag]          BPM/key analysis (optional toggle)
    ↓
[ready]            LiveSet → "published"; ActivityEvent fired
```

### Progress + UX

Each job posts to Redis pub/sub. Backend WebSocket forwards to frontend. Live progress in a "Jobs" drawer. Failed jobs surface with retry + log excerpt.

### Dedup

Chromaprint hash + duration → `SetFingerprint` table. Match within ±2 s and >95% similarity → block re-upload, point at existing set. Override available; creates sibling LiveSet with `duplicate_of` pointer.

### Design choices

- **Streaming copy is mandatory** even with cheap disk: keeps player code format-agnostic, keeps DLNA/SMAPI/Subsonic services dead simple (they all serve the same opus file).
- **Loudness stored, not baked:** preserves originals; allows re-tuning target loudness without re-encode.
- **Multi-arch images** even though host is x86 NUC: the rest of self-hosted-app userbase often runs ARM (Pi/UnRaid/Synology), and multi-arch buildx is a one-line workflow change.

## 6. Catalog management — tracklist editor & enrichment

### Tracklist editor

Per-set view: player at top, tracklist on the right. Three input modes.

1. **Live mode** — playing the set, hit `M` → row inserts at playhead. Tab through Artist/Title/Mix/Label/Notes; Enter saves. Optimistic UI; saves to DB in background.
2. **Paste-and-parse** — paste raw tracklist; LLM provider parses → structured rows → user reviews diff → accept all / individually. Falls back to a regex parser without LLM (handles `0:00 Artist - Title [Label]` and friends).
3. **Import URL** — paste 1001tracklists URL → scraper job. ToS-grey warning before first run + rate limit.

Each entry has status `raw` / `resolved` / `acoustid_confirmed`. Visible badge per row.

**Bulk resolve** — runs through entries, autosuggests Track matches from DB + providers, surfaces ambiguous ones for human review.

**Time-shift dialog** — "Source audio length changed by +27 s. Shift entries after 01:00:00 by +27 s?" with preview.

**AcoustID per entry** — "ID this" button: backend fingerprints a 15 s window centered on the timestamp, queries AcoustID, returns ranked candidates with confidence.

### Provider plugin architecture

In `packages/providers/`. Each implements:
```python
class Provider(Protocol):
    kind: str
    capabilities: set[Cap]   # {ENRICH_ARTIST, ENRICH_TRACK, ENRICH_RELEASE, LOOKUP_BY_ISRC, FINGERPRINT, PARSE_TEXT, ...}
    async def enrich_artist(self, artist) -> ProviderResult: ...
    async def enrich_track(self, track) -> ProviderResult: ...
    # etc.
```

Stock: Discogs, MusicBrainz, Beatport, Spotify, Last.fm, ListenBrainz, AcoustID, 1001tracklists scrape, OpenAI-compatible LLM. Adding new = drop in a class + admin enables it.

### Provenance & priority

- Every Artist / Track / Release field records (set_by_user | set_by_provider:<kind>, confidence, locked bool). Manually-edited fields get a 🔒 — auto-enrichment never overwrites locked fields.
- **Per-field priority:** admin UI drag-orders providers per field type. Defaults ship sane (Beatport > Discogs > MusicBrainz for `bpm`/`key`; MusicBrainz > Discogs for `isrc`; Spotify > Discogs for `image_url`).

### Caching

`ProviderResponse` table stores raw upstream responses (jsonb + fetched_at + expires_at). TTL configurable per provider. Re-enrich consults cache first.

### LLM provider config

OpenAI-compatible: base URL, model name, API key, monthly token budget cap. Works with OpenAI, OpenRouter, local Ollama, Anthropic via proxy — anything speaking the OpenAI Chat API. Used initially for paste-parse; later, optional cleanup/normalization.

## 7. Playback, streaming, casting

### In-app player

- **wavesurfer.js v7** with regions + timeline + minimap. Reads precomputed peaks JSON.
- **Sticky mini-player** persists across navigation. Click cover → expand to full set view.
- **Tracklist sidebar** — current entry highlights live; click row → seek. Shows timestamp, artist, title, mix, mashup chip if any, `raw` badge for unresolved.
- **Keyboard:** Space, J/L ±10 s, K play/pause, ←/→ ±5 s, ↑/↓ volume, M mark, B bookmark, [/] cycle entries, Shift+L/R A↔B markers.
- **Variable speed 0.5–2× pitch-preserving** (Web Audio + `soundtouchjs`).
- **Loop region** — A↔B colored span.
- **Resume** — `UserSetState` saves position every 5 s; "Resume from 47:12?" toast on return.
- **Time-stamped comments** as colored dots on waveform; hover preview, click to seek + open thread.
- **Bookmarks** — same UX, per-user, optional label.
- **MediaSession API** — lockscreen artwork/title/artist/prev-next mapped to prev/next tracklist entry.

### Casting & multi-room

- **F1. Chromecast** — Cast SDK button. Streams the same Opus URL the player uses; HLS-wrap if codec compat needed.
- **F2. DLNA / UPnP** — `minidlna` sidecar, read-only on `/audio/stream/`. Sonos, Kodi, VLC, smart TVs auto-discover.
- **F3. Snapcast** — opt-in `setvault-snapserver` sidecar. Web player pipes into Snapcast → synced multi-room.
- **F4. Listen-together** — WebSocket room: one host, others join. Server tracks playhead with drift-tolerance buffer; clients smooth into host position. Chat sidebar.
- **F8. Sonos SMAPI** — `setvault-sonos` SOAP service. Implements `getMetadata`, `getMediaURI`, `search`, `getMediaMetadata`, `reportPlaySeconds` (so Sonos plays scrobble back). User adds as custom music service in Sonos app once; native UX thereafter.

### Third-client compatibility

- **F6. Subsonic API** — read endpoints (`getArtists`, `getAlbumList`, `stream`, `download`, `search3`, `getCoverArt`, `getStarred`, `scrobble`). LiveSets → Subsonic "albums," TracklistEntries → "songs." Substreamer/DSub/Symfonium/play:Sub work natively.
- **F5. Scrobbling** — Last.fm and ListenBrainz outbound, configured per user. Listening events → scrobble jobs with retry/backoff.
- **K2. Podcast chapter markers** — stream URL `?chapters=podcast` variant: returns the streaming audio with embedded chapter markers (ID3v2 chapters in MP3 / chapter atoms in MP4) per TracklistEntry. Podcast apps render the tracklist as native chapters.
- **K3. RSS feed** — per user, scope filter (favorites / recently-added / everything). Subscribed in any podcast app.
- **K4. Embeddable player** — `<iframe src="…/embed/<set>">`, slim chrome, no auth required if the set's owner has marked it embed-allowed (admin-controlled toggle).
- **F7. AirPlay** — out of scope.

### Auth for non-browser clients

`ApiToken` entities with scoped capabilities. Subsonic clients use HTTP Basic; RSS embeds the token in the URL; SMAPI uses session-binding via `getSessionId`.

## 8. Auth, search, browse, admin, frontend

### Auth

- **Local accounts** — Argon2id password hashes, email-based invite flow (admin generates invite → email sent via SMTP if configured, otherwise admin gets a copy-paste link). Invite link contains a one-time `EmailToken`; recipient sets username/password to redeem.
- **Password reset** — user enters email on the login screen → if matched, `EmailToken` of kind `password_reset` is created and emailed (or shown to admin if SMTP not configured). Token expires in 1 hour, single-use.
- **Email verification** — sent on first email change; until verified, the user's email-based features (notifications, password reset) keep working with the previous verified address.
- **OIDC** — admin enables in Settings, configures issuer/client_id/secret. Login screen shows "Sign in with <Provider>" alongside local form. First-time OIDC login auto-provisions user (if admin enabled) or maps via email match. OIDC users can skip the verification step (the IdP is the source of truth).
- **Forward-auth (J13)** — admin can trust `X-Forwarded-User` / `X-Forwarded-Email` / `X-Forwarded-Groups` from a configured upstream proxy (Authelia / Authentik / Pocket-ID forward-auth mode). Trust requires both an explicit toggle and an allowlisted upstream IP/CIDR — headers from outside the allowlist are ignored. Group-to-role mapping is admin-configured. Auto-provisioning is opt-in. Cheaper than full OIDC for users already running Authelia in front of their stack.
- **Sessions** — HTTP-only secure cookie, 30-day rolling. CSRF token on mutations.
- **Roles** — `admin` and `user`. Admins manage users/providers/OIDC/quotas/jobs/connectors; everyone else does the rest.

### Notifications

In-app notifications and email notifications share the same trigger logic; the channel is determined per-user, per-kind by `NotificationPreference`.

| Kind | Default channel | Notes |
|---|---|---|
| `mention` | both | `@user` in a comment |
| `comment_on_set_you_uploaded` | in_app | replies/comments on a set you own |
| `set_added_by_followed_user` | in_app | requires user-subscribe (H2) |
| `weekly_digest` | email | opt-in |
| `account_security` | email | password change, new session — never disabled |

### Search & browse

- **Postgres FTS** — global search bar; results split by entity type with autocomplete.
- **Library views:** All Sets / By Artist / By Party / By Venue / By Series / By Tag. Cover-grid and dense-row toggles.
- **"Sets containing track X"** — one click on any track row.
- **Filter sidebar:** artist/party/venue/venue-kind/year/duration/source/tags. State in URL params (shareable, bookmarkable).
- **Smart playlists** — jsonb query DSL; rule-row UI with AND/OR groups.
- **Similar sets** — pgvector cosine similarity on `LiveSet.embedding`. Falls back to artist/tag overlap before ≥10 resolved entries.
- **Saved searches** — bookmark a filtered URL; appears in sidebar.

### Group/social

- Favorites and watch-later in sidebar.
- **Activity feed** on home: last N events from `ActivityEvent`. Filterable. Per-user subscribe optional.
- **Comments** at timestamps; threaded; `@mentions` notify.
- **Private notes** per user per set, markdown.

### Admin (`/admin`)

Tabs: Users • Auth • Providers • Connectors • Storage • Watch folders • Discoveries • Unmatched • Recycle bin • Jobs • Schedule • Health • Backup • System.

- **Users** — list, invite, deactivate, set quota, force-logout, reset password. When no SMTP connector is configured, invite/reset modals show the one-time link to copy and send manually.
- **Auth** — local-account toggles, OIDC issuers (add/edit/remove, auto-provision toggle), Forward-auth (enable, trusted upstream CIDRs, header names, group→role mapping, auto-provision toggle).
- **Providers** — two subtabs:
  - **Metadata** (D1–D7 + LLM enrichment providers — Discogs, MusicBrainz, Beatport, Spotify, Last.fm/ListenBrainz, AcoustID, 1001tracklists scrape, OpenAI-compatible LLM): enable/disable, edit config, test connection, drag-order priority.
  - **Ingest sources** (§5 audio acquisition plugins — YouTube, Mixcloud, Internet Archive, SoundCloud stock; Bandcamp + Twitch optional): enable/disable, edit config (per-source auth where required), per-source rate limits, advertised capabilities (`SEARCH` / `DOWNLOAD`), last successful query, error rate, auto-disable status. Drag-order priority controls candidate ordering when multiple sources return overlapping hits.
- **Connectors** — pluggable notification channels (J12). SMTP, webhook, Discord, Telegram, Apprise, Slack, ntfy, Gotify. Per connector: name, kind, encrypted config, scope filter (event kinds + users + min severity), `Send test` button, last delivery + last error inline.
- **Storage** — **Root folders** (add/edit/remove, host path, free-space, last health probe, default-for-ingest toggle, optional max-size cap, **naming template** per J9 with live preview of how a sample set would lay out on disk), **Remote path mappings** (when worker mounts differ from web), per-user usage, total volume, breakdown by file type, orphan cleanup.
- **Watch folders** — list of admin-configured ingest source paths (A3), each bound to a target root folder; per-folder enable/disable, last-scan status, manual rescan.
- **Discoveries** — A9 monitor inbox: candidate hits from monitored entities awaiting review (or auto-ingested log). Per-row: source, candidate metadata, confidence, "matches existing set" hint, actions (`Ingest`, `Dismiss`, `Set as upgrade`).
- **Unmatched** — A12 inbox of files in watch folders the system couldn't auto-link. Per-row: file path, probed metadata, fingerprint, actions (`Link to existing set`, `Create new draft`, `Dismiss`, `Move out`).
- **Recycle bin** — J8: soft-deleted sets with their `purge_after_at` countdown. Restore-now and purge-now per item; bulk restore/purge.
- **Jobs** — last 500 cross-user, filter by status/kind, view payload + log, retry failed.
- **Schedule** — J14 periodic-tasks UI. Each task: last run, next run, last result, manual `Run now`. Backed by `rq-scheduler` introspection.
- **Health** — J11 consolidated view. Storage roots, providers, connectors, OIDC + forward-auth issuer reachability, queue depth + worker liveness, expired/expiring tokens, version + update availability (J16). Mirrors `/api/health` for external monitoring.
- **Backup** — one-click DB dump + audio tarball; configurable schedule. CLI restore.
- **System** — version, queue depth, Redis stats, environment summary (secrets filtered, §14), library refresh webhooks (J15: list, edit, test-fire, last status), **Rate limits** (per-tier overrides, §14), **Audit log** (filterable, §14), `SECRET_KEY` rotation runbook link.

### Mobile / PWA

- Responsive from the ground up. Mini-player → bottom sheet on mobile; sidebar → drawer.
- PWA: manifest + service worker + mediaSession.
- Offline cache last-played sets (configurable, default 1 GB).
- Mobile-specific: pull-to-refresh on activity; swipe-row gestures on tracklist (resolve / delete).

### Frontend routes (SvelteKit)

```
/                       home (activity + recently added + continue listening)
/sets                   library list (filterable)
/sets/[slug]            set detail (player + tracklist editor)
/sets/[slug]/edit       metadata edit
/artists                list
/artists/[slug]         artist detail (sets, top tracks)
/parties/[slug]         party detail (lineup, sets)
/venues/[slug]          venue detail
/series/[slug]          series detail
/tracks/[id]            track detail (sets containing it)
/playlists              user playlists
/playlists/[id]         playlist detail
/search?q=              global search results
/jobs                   user's job history
/settings               account, language (per-user locale, J17), scrobbling, RSS token, API tokens, notification preferences
/admin/*                admin tabs
/embed/[slug]           minimal embeddable player
```

State: TanStack Query (server state) + Svelte store (player/queue). One multiplexed WebSocket for jobs/activity/listen-together.

## 9. Phasing

Phases ordered to maximize the value of each subsequent phase. Each phase produces concrete artifacts that unblock the next.

1. **Phase 1 — Design & visual identity.** No backend or app code in this phase. Deliverables:
   - **Design tokens:** CSS-variable set (color, type, spacing, radius, motion) with dark + light palettes. Used by both the app and the landing page.
   - **App mockups (HTML/CSS)** for the top 5 screens: **set detail / player**, **tracklist editor**, **library / browse**, **home / activity**, **artist or party detail**. Mobile breakpoints for the player view.
   - **Landing page mockup (HTML/CSS).** Shares the design tokens and component primitives with the app — same brand vocabulary — but uses editorial composition (big hero, scroll-driven feature sections, screenshot/video demos, generous whitespace). Distinct from the app's dense utility composition. Think Linear's marketing site vs. Linear the app: same identity, different layouts.
   - **Component sketch list:** buttons, inputs, dialogs, tabs, status badges, tracklist row, filter sidebar, mini-player — pattern-level, not built yet. Exposed in a `components.html` showcase page.
   - **Live preview entry point:** `frontend/design/index.html` lists every mockup and component page with thumbnails and links. Browseable locally with one command (`npx serve frontend/design` or equivalent). During the `frontend-design` session itself, the visual companion already shows mockups live in the browser as they evolve — the static `frontend/design/` build is what survives the session for ongoing reference.
   - Driven by `docs/design-brief.md` in a fresh `frontend-design` Claude session (likely a separate worktree).
   - **Done when:** mockups review well with the crew, the design language reads coherent across all 5 app screens + the landing page, and `frontend/design/index.html` works as a one-stop preview.
2. **Phase 2 — Core vault.** Auth (local) + SMTP basics (invite + password reset, with copy-paste fallback), upload, transcode/normalize/waveform pipeline, manual catalog (artist/party/venue/set), in-app player matching the Phase-1 design, Postgres FTS basic search. **First runnable build / MVP.**
3. **Phase 3 — Tracklist & enrichment.** Tracklist editor (live + paste), Track DB, provider plugin framework, MusicBrainz + Discogs + AcoustID, comments, bookmarks, `@mention` notifications (in-app + email).
4. **Phase 4 — Ingest & distribution.** yt-dlp URL rip, RSS feeds, embeddable player, mobile PWA polish.
5. **Phase 5 — Compatibility.** Subsonic API + scrobbling.
6. **Phase 6 — Casting.** DLNA, Chromecast, listen-together rooms.
7. **Phase 7 — Sonos.** SMAPI sidecar (heaviest single subsystem).
8. **Phase 8 — Polish.** Smart playlists, pgvector "similar sets", BPM/key detection, Snapcast.
9. **Phase 9 — OIDC, full admin polish, README + GitHub Pages landing page release.**

Each phase becomes its own implementation plan after this spec is approved. Phase 1 (Design) is driven by `docs/design-brief.md` in a separate `frontend-design` session; Phases 2–9 each get a `writing-plans`-produced plan in this repo.

## 10. Out of scope (v1)

- AirPlay (complex on Linux/Docker; modern Sonos already covers via SMAPI).
- Stem separation (Demucs) — too compute-heavy for the host class.
- Public/community features (profiles, follows, public set pages).
- Native iOS/Android apps — covered well enough by PWA + Subsonic clients.
- Anonymous public access.

## 11. Open questions

None at spec sign-off. Implementation plans (one per phase) will surface task-level questions as they arise.

## 12. Offline-first principle & online-dependency matrix

SetVault is self-hosted. Browsing the catalog and playing back sets must continue to work even when the host has **zero internet access** (only LAN). This shapes several architectural choices.

### Core functions that work fully offline

- Sign in (local accounts).
- Browse the library — list, filter, search.
- Open any set, play it in the in-app player, see waveform and tracklist.
- Edit metadata, tracklists, comments, bookmarks, playlists, private notes.
- Cast to LAN-only targets: DLNA renderers (F2), Snapcast (F3), Subsonic clients (F6) on the same LAN.
- Listen-together rooms (F4) — the WS server is local.
- All admin functions except those that need an external service to be reachable.

### Functions that require internet (clearly opt-in, fail gracefully)

| Feature | Why internet | Failure behavior |
|---|---|---|
| **A2** URL rip (yt-dlp) | yt-dlp fetches external sources | Error toast: "no network — try again later." Job marked failed, retryable. |
| **D1–D7** Metadata enrichment providers | Each calls a third-party API | Skipped silently when WAN is down; cached responses still serve. Manual editing always works. |
| **F1** Chromecast | Cast SDK uses Google's cloud | Cast button hidden when SDK can't reach Google. |
| **F5** Last.fm / ListenBrainz scrobbling | Outbound HTTP | Queued in worker; retries with exponential backoff. Listening continues regardless. |
| **F8** Sonos SMAPI | Sonos cloud calls the SMAPI service | Sonos shows the service as offline; LAN DLNA (F2) is the fallback. |
| **J6** SMTP outbound mail | SMTP server is usually external | App degrades to "show invite/reset link to admin" mode (already specified). |
| **J12** Cloud notification connectors (Discord/Telegram/Slack/Apprise) | Each calls a third-party API | Queued in worker; retried with backoff. Self-hosted ntfy/Gotify on the same LAN keep working. In-app notifications continue regardless. |
| **J15** External library-refresh webhooks | Outbound HTTP | Queued and retried. LAN targets (Plex/Jellyfin on same network) keep working. |
| **J16** Update banner (GitHub Releases poll) | Outbound HTTPS to api.github.com | Banner stays whatever it last knew; poll retries on next schedule. |
| **A8 / A9** Interactive search + monitored auto-ingest | Each provider call is a third-party API | Search shows per-source error states; queries cached responses serve when available. Monitored scans pause and resume when the WAN returns. |
| OIDC SSO (J5) | OIDC issuer usually external | Local accounts continue to work. OIDC button error-states cleanly. |
| Forward-auth (J13) | None (proxy is on the LAN) | No degradation — forward-auth works offline. |
| **J17** Translations / i18n at runtime | None — locale files bundled in image | No degradation. |
| Crowdin sync (J17, build-time) | Outbound HTTPS to `api.crowdin.com` | **Build-time / contributor-time only** — never required at runtime by the running instance. Triggered by the i18n-sync GitHub Action; new translations land in the next Docker tag. Repo secrets (`CROWDIN_PERSONAL_TOKEN`, `CROWDIN_PROJECT_ID`) are not present in the runtime environment. |

### Implementation rules that follow

1. **No CDN dependencies in the app shell.** All fonts, icons, and JS libraries are bundled into the Docker image and served from the SetVault host. The `frontend/design/` prototypes (Phase 1) and the production frontend (Phase 2 onward) self-host every asset they reference.
2. **No telemetry / no phone-home.** SetVault never beacons to any external service unless the user has explicitly enabled a feature that requires it.
3. **Service worker caches the app shell.** PWA service worker (I2) caches HTML/CSS/JS/fonts/icons aggressively so the app loads instantly with no network. Recently played sets are cached per the I3 offline policy.
4. **Provider configuration is the gate.** Out of the box, **zero metadata providers are configured**. The app must be fully functional and pleasant to use in that state. Providers are admin-added when (and if) the host has internet.
5. **Network-status awareness.** UI surfaces a small "offline" banner when the browser has lost connection; features that need network grey out or hide rather than silently failing.
6. **Reverse-proxy can sit on a LAN-only domain** (e.g., `setvault.lan`). Sonos SMAPI and external clients are the only things that benefit from public DNS — and they're explicitly opt-in.
7. **Landing page on GitHub Pages is marketing, not the app.** It's external by definition and never required for using SetVault. The README's quickstart is reachable from inside the running app under "Help" so users without internet still see install / config docs.

## 13. Recommended system requirements

These appear (in shorter form) on both the README and the GitHub Pages landing page so users can self-qualify before installing.

### Minimum (works, but slow)

- **CPU:** 2 cores (x86_64 or ARM64). Raspberry Pi 4 / Pi 5 OK; ARM SBCs with hardware float OK.
- **RAM:** 2 GB.
- **Disk:** 2 GB for the app + DB + caches; **plus** your audio library. Live sets are typically 60–120 min Opus 128k ≈ 60–120 MB each. ~1k sets ≈ 100 GB.
- **OS:** any Linux distro that runs Docker 24+ and Docker Compose v2. macOS via Docker Desktop works for evaluation.
- **Network:** local network (LAN access from devices that play sets). HTTPS only required if you want Sonos SMAPI (F8) or external clients (Subsonic, RSS) reaching it remotely.

At minimum, a single ingest job (yt-dlp + transcode + normalize + waveform) for a 90-minute set takes roughly 5–15 minutes on a Pi 4 — usable, but you'll feel it.

### Recommended (good experience)

- **CPU:** 4 cores x86_64 (modern Intel/AMD), or Apple Silicon if running natively. NUC-class or higher.
- **RAM:** 8 GB.
- **Disk:** SSD for the app/DB volume; SSD or fast HDD for audio. **Audio storage:** budget on actual library size — see Minimum note.
- **OS:** Debian/Ubuntu/Fedora/Alpine on bare metal or VM. Docker 24+, Compose v2.
- **Network:** HTTPS terminated at a reverse proxy (Caddy bundled, or your own Traefik/nginx). Public DNS A/AAAA record if you want Sonos SMAPI or external client access; LAN-only deployments don't need this.

A typical ingest job here runs in ~30–90 seconds for a 90-minute set. Multiple users browse, search, and play simultaneously without contention.

### Heavy / power-user

- **CPU:** 6+ cores. Multiple worker replicas can chew through batch enrichment / re-fingerprint runs in parallel.
- **RAM:** 16 GB. Helpful when running BPM/key analysis (K1) on large back-catalogs, or pgvector similarity over many thousands of sets.
- **Disk:** NVMe SSD for the DB/cache volume, dedicated bulk disk (HDD or NAS) for audio. Multi-TB libraries OK.
- **GPU:** not used. Reserved for a possible future Demucs (K5, currently out of scope).

### Software prerequisites (all tiers)

- Docker Engine 24+ and Docker Compose v2.
- A reverse proxy with HTTPS if you expose the app outside your LAN — bundled Caddy works out of the box, or bring your own.
- For ARM64 hosts: nothing extra; multi-arch images (M1) cover you.
- For Sonos SMAPI specifically: a publicly reachable HTTPS endpoint (Sonos's cloud must reach it). LAN-only deployments still get DLNA browse on Sonos via F2 without this requirement.

### Storage planning rule of thumb

```
disk_needed ≈ (avg_set_minutes × 1 MB/min × set_count × 2)
              ↑ original copy + Opus stream copy combined ≈ 2× streaming size in practice
```

For 1000 sets averaging 90 min each: ~180 GB. The app, DB, caches, waveforms, and thumbs add <5 GB.

## 14. Security

Concrete commitments, pulled together with the touchpoints already specified inline (Argon2id passwords in §8, encrypted-at-rest config in §3, forward-auth CIDR allowlist in J13, signed multi-arch images + SBOM in M3/M4).

### Inputs & outputs

- **Schema validation at the API boundary** — every request body / query / path is Pydantic-validated and rejected before the handler runs. Same models drive OpenAPI docs.
- **Output encoding** — SvelteKit auto-escapes by default. Markdown rendering paths (private notes H4, comments H3) sanitize via DOMPurify-equivalent before any `{@html}` use.
- **CSP** — `default-src 'self'`; no inline script except a small boot stub (nonce-bound); no external origins (matches §12 offline-first). All fonts/icons self-hosted.
- **Security headers** — HSTS (preload-eligible), `X-Frame-Options: DENY` everywhere except the embeddable player (K4) on its own origin/path with `frame-ancestors` set instead, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` denying camera/mic/geo/USB.

### Rate limiting

Tiered, Redis-backed counters keyed both per-IP *and* per-user. Admin-overridable in `/admin/system → Rate limits`.

| Tier | Endpoints | Default |
|---|---|---|
| Auth-strict | `POST /login`, password-reset request + redeem, OIDC callback, forward-auth fallback | 5 / min / IP, 20 / hr / IP, exponential backoff after 3 failures, account lockout after N |
| Expensive | A2 URL-rip submission, A8 search query, AcoustID lookup, LLM-parse (C7) | 30 / min / user, 200 / hr / user |
| Standard | everything else (read + write) | 120 / min / user, 5k / hr / user |
| Webhook-out (J15) | per target | 10 / min / target, queue-with-backoff on overflow |

WebSocket frames have a per-connection ceiling separate from HTTP. Per-source ingest rate limits (J7 + `IngestSourceConfig.rate_limit_config`) apply *outbound* on top of these and are honored by the worker pool.

### Account & auth hardening

- **Account lockout** — N consecutive failed logins → temporary lock (admin-configurable; default: 5 attempts → 15 min). Resets on successful auth.
- **Optional TOTP 2FA** — local accounts can enroll voluntarily; admin can require 2FA org-wide or for the `admin` role specifically. OIDC users inherit IdP 2FA.
- **OIDC** — strict `state` and `nonce` validation; PKCE (`S256`) required; `iss` claim cross-checked against the configured issuer; no implicit flow.
- **Forward-auth (J13)** — header trust requires *both* the explicit toggle *and* the upstream IP/CIDR allowlist match. Forward-auth headers from outside the allowlist are stripped at ingress, never echoed in app responses.
- **Session rotation** — session ID rotates on login, role change, password change. Password or role change invalidates all other active sessions for that user.

### URL ingest & outbound-call hardening (A2 / A8 / A9 + provider calls + J15 webhooks + OIDC discovery)

- **SSRF guard** — outbound HTTP refuses private CIDRs (RFC 1918 + ULA), link-local, loopback, cloud metadata IPs (`169.254.169.254`, `fd00:ec2::254`), and unresolved hostnames. Per-target allowlist override applies *only* to admin-added targets (e.g., a J15 webhook pointed at a Plex on `192.168.x.y`).
- **URL scheme allowlist** — `http(s)` only for ingest/webhooks/OIDC; explicitly refuse `file://`, `data://`, `chrome-extension://`, etc.
- **yt-dlp isolation** — workers run yt-dlp under reduced privileges with a per-job scratch dir; per-source cookies (when configured for SoundCloud/Twitch auth) are read-only mounted; downloads obey the per-source rate limit and timeout.

### File upload & filesystem

- **MIME sniff via libmagic** on the first 4 KB; cross-check against declared `Content-Type` *and* file extension; reject mismatches before the file ever leaves `tmp/`.
- **Filename normalization** — Unicode NFC, strip control characters, reject `..` and absolute paths, reject Windows-reserved names (`CON`, `PRN`, etc.) even on Linux hosts so backups restore cleanly.
- **Path traversal guard** — every on-disk path is constructed from `MediaRoot.host_path` + a sanitized relative path, then validated via `realpath` to ensure containment within the root. Any escape rejects.
- **Watch-folder hardening** — symlinks pointing outside the watch folder, device files, FIFOs, and files with unexpected ownership go to the A12 unmatched inbox flagged, never auto-processed.
- **Recycle bin guardrail (J8)** — soft-delete batches are capped at ≤10% of library / ≤500 sets per single operation. Larger ops require an admin confirm-by-typing in the UI. Prevents a stuck script or fat-finger from wiping the vault.

### Secrets

- **At-rest encryption** — provider keys, SMTP/connector configs, OIDC client secrets, watch-folder credentials, ingest-source auth: AES-GCM with per-row nonce, key derived from `SECRET_KEY` (§3).
- **`SECRET_KEY` rotation** — admin CLI `setvault rotate-secret-key` decrypts with old key and re-encrypts with new in one transaction. Documented in README.
- **Log redaction** — middleware strips `Authorization` / `Cookie` / `Set-Cookie` headers, password-/token-shaped query parameters, and any encrypted-config jsonb fields from log output. Stack traces emit the *type* of secret-tagged fields, never the value.
- **`/admin/system` environment summary** filters out anything whose name ends in `_KEY`, `_SECRET`, `_TOKEN`, or `_PASSWORD`.

### Outbound webhooks (J15)

- **HMAC-SHA256 signature** on every request: `X-SetVault-Signature: t=<unix>,v1=<hex>`. Secret per subscription, rotatable from the admin UI. Recipients verify the signature and reject deliveries outside a 5-minute window (replay protection).
- Optional mTLS for high-trust homelab targets (admin uploads a client cert per subscription).

### Audit log

- Append-only **`AuditEvent`** table. See §4 data model.
- Logged actions: user create/edit/disable/role-change, provider/source/connector enable/disable + config edit, `MediaRoot` add/remove, recycle-bin purge-now, force-logout, `SECRET_KEY` rotation, backup create/restore, forward-auth config change.
- Surfaced under `/admin/system → Audit log` with filter by actor / action / target / timeframe. Retention is admin-configurable; default 1 year.

### Container hardening

- Containers run as non-root via `PUID`/`PGID` (J10). Compose example sets `no-new-privileges: true` and an explicit minimal `cap_drop: [ALL]` with a small `cap_add` list (e.g., `CHOWN`, `DAC_OVERRIDE` only where needed).
- `HEALTHCHECK` directives in each image so compose / orchestrators pick up unhealthy state.
- `setvault-worker` doesn't expose ports; only `setvault-web` and `setvault-sonos` are reachable from outside the compose network.

### Dependency & supply chain

- Renovate (or Dependabot) config in repo for backend (`pip`/`uv`) + frontend (`npm`) dependencies.
- CI gate: `pip-audit` and `npm audit` non-zero severity blocks the release workflow.
- SBOM (CycloneDX) + SLSA provenance + cosign keyless signatures already specified in M3/M4.

### Threat-model boundaries

- **In scope:** authenticated users attempting privilege escalation; opaque outsiders scanning the public surface (Sonos SMAPI sidecar, embeddable player K4, RSS feeds with token in URL); compromised dependency supply chain (mitigated by SBOM + provenance + signing).
- **Out of scope (v1):** nation-state actors, post-compromise host-OS persistence, malicious admin (admin is trusted by definition; the audit log is forensic, not preventative); side-channel timing attacks against the crypto primitives we don't implement ourselves.

## 15. Internationalization (i18n)

### Goal

A self-hosted instance can serve any user's preferred locale with **no internet at runtime**. Translations are crowdsourced via a FOSS-friendly platform; the running app never phones home for strings.

### Translation platform

**Primary: Crowdin for Open Source** (`crowdin.com/page/open-source-project-setup-request`).
- Free for OSS projects (application required, granted to public repos with a libre license).
- Maintainer already uses Crowdin for another project — keeps tooling and reviewer workflow consistent across projects.
- GitHub integration via the **Crowdin GitHub Action** + CLI (`crowdin upload sources` / `crowdin download translations`). Repo-root `crowdin.yml` declares which paths map to which target files.
- Translation memory, glossary, MT pre-translation, screenshot context, OCR — all included on the OSS plan.
- Polished UX for translators; lower friction for non-technical contributors.

**Alternative: Hosted Weblate** (`hosted.weblate.org`). FOSS itself, free for libre projects, same JSON / `.po` file workflow. Drop-in if Crowdin's terms ever change or self-hosting the translation platform becomes a hard requirement. Switching cost is near-zero because the file format is portable — neither platform owns the source files, the GitHub repo does.

### Crowdin integration concretely

- Repo root: **`crowdin.yml`** declares source-path patterns and target-locale paths.
  ```yaml
  project_id_env: CROWDIN_PROJECT_ID
  api_token_env: CROWDIN_PERSONAL_TOKEN
  base_path: '.'
  preserve_hierarchy: true
  files:
    - source: '/frontend/src/lib/i18n/en.json'
      translation: '/frontend/src/lib/i18n/%two_letters_code%.json'
      type: 'webxml'
    - source: '/apps/web/i18n/messages.pot'
      translation: '/apps/web/i18n/%two_letters_code%/LC_MESSAGES/messages.po'
      type: 'gettext'
  ```
- GitHub Actions workflow `.github/workflows/i18n-sync.yml` runs on push to `main`: uploads source strings, downloads completed translations, opens a PR titled `i18n: sync from Crowdin` with locale updates.
- `CROWDIN_PERSONAL_TOKEN` and `CROWDIN_PROJECT_ID` live in repo secrets — never in the running app's environment, since runtime doesn't talk to Crowdin.

### Library choice

- **Frontend (SvelteKit):** `svelte-i18n` — mature, file-based JSON, no build step required to add a new locale.
- **Backend (FastAPI + worker):** `Babel` with gettext `.po` / `.mo` files. Used for outbound emails (J6), notification connector message bodies (J12), and any server-rendered strings.
- **Sonos SMAPI sidecar:** uses its own SOAP-level locale mechanism (`getString` with locale param); separate translation surface, but pulls from the same backend `.po` files.

### File layout

```
frontend/src/lib/i18n/
  en.json                            # source of truth; hand-edited
  nl.json                            # PR'd in by Weblate
  de.json
  ...
apps/web/i18n/
  messages.pot                       # source template, generated by extraction
  en/LC_MESSAGES/messages.po
  nl/LC_MESSAGES/messages.po
  ...
```

Source language: English (`en`). All keys are namespaced by feature area (`tracklist.editor.add_entry_button`, `auth.login.password_required`) — never raw English strings as keys. Avoids the "translate to English" round-trip when the source string changes.

### Runtime resolution

Locale precedence per request:

1. `User.locale` (per-user explicit choice).
2. `SystemConfig.default_locale` (admin default).
3. `Accept-Language` header (best match against enabled locales).
4. `en` (always-present fallback).

Locale changes hot-swap without page reload. WebSocket frames pick up the new locale on next connect.

### Pluralization & formatting

- **Plurals + select cases:** ICU MessageFormat (`{count, plural, one {# track} other {# tracks}}`). Both `svelte-i18n` and `Babel` understand it.
- **Date / time / number:** `Intl.*` API on the frontend; `Babel` formatters on the backend. Both honor the resolved locale.
- **Sort / collation:** `Intl.Collator` for library-list ordering — affects how sets sorted by title behave in non-Latin scripts (Cyrillic, Greek, CJK).

### RTL support

- HTML `dir="rtl"` on `<html>` for RTL locales (Arabic, Hebrew, Persian, Urdu).
- CSS uses logical properties (`margin-inline-start`, `padding-inline`, `inset-inline-end`) from **Phase 1 Design** — not retrofitted. The Phase 1 design tokens and component primitives are RTL-clean.
- Player UX: waveform direction stays LTR (Web Audio is direction-agnostic; only the surrounding chrome flips). The J/L keyboard shortcuts stay bound to forward/back regardless of locale; the `←/→` shortcuts swap meaning per browser convention.

### Offline-first compliance (§12)

- Every bundled locale ships in the Docker image. Runtime never fetches from Crowdin / any CDN.
- Translation completeness percentages per locale are pre-computed at build time and shipped as a static manifest (`apps/web/i18n/manifest.json`), so the locale picker can show "Dutch — 98%" without internet.
- New translations land in the next Docker tag via the standard release flow (M1).

### CI checks

- **Missing-key check** — every locale must have all keys present in `en`. Build fails on missing.
- **ICU syntax check** — plural / select / nested-format syntax validated per locale.
- **Pseudo-localization smoke test** — a `[!!Pseudo!!]` locale generated in CI from `en` with diacritics + 30% length expansion. Catches concatenation bugs and layout overflow before real translators touch the strings.
- **Unused-key check** — strings in source files that no key references warn (but don't fail) — translators waste effort otherwise.

### LLM-assisted draft translations (optional, off by default)

- Admin can opt in via `SystemConfig.llm_draft_translations_enabled`. When enabled, the C7 LLM provider produces first-pass drafts when a new locale is opened. Drafts are clearly marked **machine-generated, needs review** in Weblate and never enter production until a human translator approves.
- Off by default to respect human translator agency and avoid LLM hallucinations leaking into shipped strings.

### Stock locales

- **At v1.0:** English (`en`) — source. Source language is the only blocking dep for shipping.
- **Aspirational, community-driven:** Dutch (`nl`), German (`de`), French (`fr`), Spanish (`es`), Brazilian Portuguese (`pt-BR`), Polish (`pl`). The European DJ-set audience makes those a natural seed; not blocking on launch — locales appear as community contributors land them.

### Phasing

- **Phase 1 (Design):** RTL via logical properties baked into design tokens; placeholder copy in mockups extracted as i18n keys, not hardcoded English.
- **Phase 2 (Core vault, MVP):** `svelte-i18n` + `Babel` wired in; English-only at first; Weblate project created and source strings pushed.
- **Phase 9 (OIDC, polish, landing-page release):** community translation drive; ship N≥3 locales above the completeness threshold for release-note prominence.

### Admin UI

Under `/admin/system → Internationalization`:

- Default locale dropdown (drives `SystemConfig.default_locale`).
- Enabled-locales list — auto-populated from the locale manifest, gated by completeness threshold; admin can override individual locales above/below the line.
- Per-locale completeness % display from the bundled manifest.
- Link to "Help translate SetVault" pointing at the Crowdin project page (`crowdin.com/project/setvault`).
- Toggle for LLM-assisted drafts.
