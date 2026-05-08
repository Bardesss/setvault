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
- **A3.** Watch folder — drop a file → auto-imported.
- **A4.** Transcode on ingest. Keep original; produce streaming copy (Opus 128k default, 256k toggle).
- **A5.** Loudness normalization (EBU R128 / ReplayGain) — stored as offset, applied at playback (not baked into file).
- **A6.** Audio fingerprint dedup via chromaprint.
- **A7.** Background job queue with live progress in UI.

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
- **J6.** **SMTP outbound email** — admin-configured (host, port, username, password, encryption [STARTTLS/SSL/none], from address, from name, reply-to). Used for: account invites, password reset, email verification, `@mention` notifications, optional weekly activity digest. **Test-email button** in admin. **Graceful fallback when SMTP is not configured:** invite and password-reset flows show the one-time link in the admin UI for manual copy-paste — the app stays fully functional without an SMTP server. Per-user **notification preferences** (email vs in-app vs off) for each notification kind. Outbound mail goes through the worker queue so SMTP timeouts never block web requests.
- **J7.** **Configurable storage paths (sonarr/radarr/lidarr-style root folders).** Two distinct concerns:
  - **App-internal volumes** (`db`, `redis`, `cache`, `config`) — each independently bind-mountable to any host path via per-volume env override. Expected on local fast storage; small.
  - **Audio root folders** — admin-managed in the UI, **one or more**. Each entry: name, host path, optional max-bytes cap, default-for-ingest flag. New `LiveSet`s are assigned to a root folder at ingest (admin-set default when multiple); the per-set on-disk layout (`originals/`, `stream/`, `waveform/`, `thumbs/`) is rooted within whichever root folder the set lives in. Common shape: bulk audio on a mounted NAS / SMB / NFS / ZFS share as a root folder, DB and config on local SSD.
  - **Health checks** — periodic read/write probe per root folder; admin Storage tab surfaces unreachable / read-only / near-full roots prominently and the `/admin/system` view shows aggregate state.
  - **Remote path mappings** — when a worker container sees a different host path than the web container (e.g., worker on a different host that mounts the NAS at a different point), admin can configure source-path → app-path mappings, analogous to *arr's "Remote Path Mappings."
  - **Watch folders** (A3) are admin-managed alongside root folders, with the same path-config UX and may live on a different mount than any root folder.
  - **No paths hard-coded** in the image. Moving an existing deployment to new mount points is a stop-edit-start operation, not a rebuild.

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
- **User** — id, email, username, display_name, password_hash*, oidc_subject*, role(admin|user), avatar_url, quota_bytes*, email_verified_at*, last_seen_at
- **OidcProvider** — id, issuer_url, client_id, client_secret_encrypted, scopes, enabled, auto_provision
- **ApiToken** — id, user_id, name, token_hash, scopes (`subsonic`|`rss`|`sonos`|`api`), created_at, last_used_at, revoked_at*
- **EmailToken** — id, user_id* (null for invites that haven't been redeemed), email, kind(`invite`|`password_reset`|`verify_email`|`unsubscribe`), token_hash, payload jsonb (e.g., role for invites, notification kind for unsubscribe), expires_at, used_at*, created_by*, created_at
- **NotificationPreference** — PK(user_id, kind), channel(`email`|`in_app`|`both`|`off`), updated_at
- **SmtpConfig** — single-row admin config: host, port, username*, password_encrypted*, encryption(`starttls`|`ssl`|`none`), from_address, from_name, reply_to*, enabled, last_test_at*, last_test_result*

### Catalog
- **Artist** — id, name, slug, aliases[], bio, image_url, country, socials jsonb, external_ids jsonb, enrichment_status jsonb
- **Venue** — id, name, slug, kind(`club`|`concert_hall`|`arena`|`outdoor`|`warehouse`|`boat`|`studio`|`online`|`other`), city_or_area*, country*, lat*, lon*, capacity*, website* — `city_or_area` accepts both city names ("Amsterdam") and named outdoor sites ("Recreatiegebied Spaarnwoude"); `country` and geo are nullable so radio/online venues don't need them; `kind` drives icon/filter UX
- **Series** — id, name, slug, description, image_url
- **Party** — id, name, slug, series_id*, venue_id*, date*, description
- **LiveSet** — id, slug, title, party_id*, venue_id*, date*, set_type, duration_seconds, source_type, source_url*, media_root_id, audio_path, streaming_path, waveform_path, normalized_lufs*, description, uploaded_by, duplicate_of* — `audio_path` etc. are root-relative and resolved against `MediaRoot.host_path` at read time, so a root folder can be remounted at a different host path without DB rewrites
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
- **ProviderConfig** — id, provider_kind, name, enabled, priority, encrypted_config jsonb, created_at, updated_at
- **ProviderResponse** — id, provider_kind, query_key (text), response jsonb, fetched_at, expires_at — cache for upstream calls
- **SetFingerprint** — id, live_set_id, fingerprint_hash, duration_seconds — for dedup
- **MediaRoot** — id, name, host_path, enabled, default_for_ingest bool, max_bytes*, last_health_check_at*, last_health_status (`ok`|`unreachable`|`readonly`|`near_full`|`unknown`), created_at — *arr-style audio root folder; one or more, admin-managed in UI
- **WatchFolder** — id, name, host_path, target_media_root_id, enabled, created_at — admin-managed ingest source paths (A3), each pointing at a target root folder for the imported set
- **RemotePathMapping** — id, scope (`worker`|`watch`|`other`), from_path, to_path, created_at — translates host paths between the web container and worker/watch contexts when their mounts differ

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

Both produce a draft `LiveSet` and queue the same downstream pipeline.

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
- **Sessions** — HTTP-only secure cookie, 30-day rolling. CSRF token on mutations.
- **Roles** — `admin` and `user`. Admins manage users/providers/OIDC/quotas/jobs/SMTP; everyone else does the rest.

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

Tabs: Users • Providers • OIDC • Email • Jobs • Storage • Watch folders • Backup • System.

- **Users** — list, invite, deactivate, set quota, force-logout, reset password. When SMTP is not configured, invite/reset modals show the one-time link to copy and send manually.
- **Providers** — list, enable/disable, edit config, test connection, drag-order priority.
- **OIDC** — issuers, add/edit/remove, auto-provision toggle.
- **Email** — SMTP host/port/encryption/auth/from. **Send test email** button. Last test result + timestamp shown inline.
- **Jobs** — last 500 cross-user, filter by status/kind, view payload + log, retry failed.
- **Storage** — **Root folders** (add/edit/remove, host path, free-space, last health probe, default-for-ingest toggle, optional max-size cap), **Remote path mappings** (when worker mounts differ from web), per-user usage, total volume, breakdown by file type, orphan cleanup.
- **Watch folders** — list of admin-configured ingest source paths (A3), each bound to a target root folder; per-folder enable/disable and last-scan status.
- **Backup** — one-click DB dump + audio tarball; configurable schedule. CLI restore.
- **System** — version, queue depth, Redis stats, environment summary (no secrets).

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
/settings               account, scrobbling, RSS token, API tokens
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
| OIDC SSO (J5) | OIDC issuer usually external | Local accounts continue to work. OIDC button error-states cleanly. |

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
