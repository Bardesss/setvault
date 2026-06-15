# SetVault

[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.6.0-brightgreen.svg)](CHANGELOG.md)
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

## ✨ What's in the box (v0.9.0)

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

## 🚀 Deploy

SetVault ships as **one image** that runs two ways. Pick one.

**Prereqs:** Docker 24+, Compose v2, ~2 GB RAM for the stack, and disk
space for your live-set library.

### Which do I pick?

| | Bundled (single container) | External datastores |
|---|---|---|
| **Best for** | homelab / single node, simplest setup | shared/managed Postgres+Redis, multi-node |
| **You run** | 1 container | Postgres + Redis + the app (compose) |
| **Datastores** | Postgres + Redis + tusd **inside** the image | your own Postgres + Redis |
| **Upgrades** | app + DB move together (see caveat) | independent |

### Option A — Single container (bundled) — recommended for most

Everything (Postgres 18, Redis, tusd, a Caddy proxy) runs inside the image.
One data volume.

```bash
docker run -d --name setvault -p 1970:1970 \
  -v setvault-data:/data \
  ghcr.io/bardesss/setvault:latest
```

That's it — no secrets to set. On first boot SetVault generates and persists
`SECRET_KEY` and the internal `POSTGRES_PASSWORD`, and defaults `BASE_URL` to
`http://localhost:1970`. Open the app in a browser and the **first-run wizard**
walks you through creating your admin account.

> **Exposing it to the internet?** Set `BASE_URL=https://your-host` (and front a
> TLS proxy) so the session cookie is marked `Secure`. See the deployment-mode
> box below.

Or with compose: copy `.env.example` to `.env` (no vars required in bundled
mode), then `docker compose -f infra/docker/compose.aio.yml up -d`.

The `/data` volume holds the database, Redis, and all media/config — **back it
up**. How you put TLS in front (or whether you need to at all) depends on your
deployment mode — see below.

> ### 🔒 Pick your deployment mode — just set `BASE_URL` correctly
>
> The bundled Caddy serves **plain HTTP on `:1970`** (`auto_https off`). The
> session cookie's `Secure` flag is derived automatically from your `BASE_URL`
> scheme, so the common modes work with no extra configuration:
>
> **A — Exposed to the internet.** Terminate TLS at a reverse proxy (Caddy /
> nginx / Traefik) in front and set `BASE_URL=https://your-host`. SetVault sees
> the `https://` scheme and serves a `Secure` cookie. This is the only safe mode
> for a public origin.
>
> **B — VPN or LAN-only (no reverse proxy).** Your WireGuard/Tailscale tunnel or
> local network already isolates the traffic, so app-layer TLS is redundant.
> Set `BASE_URL` to your plain-HTTP address (e.g. `http://10.x.x.x:1970`) — the
> `http://` scheme tells SetVault to drop the `Secure` flag so login persists. No
> extra flag needed. Just never expose port `1970` to the internet on an
> `http://` `BASE_URL`.
>
> **C — Tailscale serve.** `tailscale serve` issues a real Let's Encrypt cert
> over your tailnet with no reverse proxy; point `BASE_URL` at the
> `https://…ts.net` name and the cookie is `Secure` automatically.
>
> > A plain-HTTP `BASE_URL` previously needed `SETVAULT_ALLOW_INSECURE_COOKIE=1`;
> > that's now inferred from the scheme. The flag still exists as an explicit
> > force-off override for unusual proxy setups — it can only relax the flag,
> > never tighten it.

> **Caveat (bundled mode):** the bundled Postgres is pinned to **PG 18** and
> its data dir is tied to that major version. A future major upgrade can't
> reuse `/data/db` — use external mode for rolling/managed upgrades, or
> dump/restore via the admin backup endpoint. Bundled mode is homelab grade.

On first boot, the container:
- auto-generates `SECRET_KEY`, the internal `POSTGRES_PASSWORD`, and `TUSD_HOOK_SECRET` if unset (persisted to `${SETVAULT_CONFIG_PATH}/.secrets`)
- defaults `BASE_URL` to `http://localhost:1970` if unset
- synthesizes `DATABASE_URL` from the `POSTGRES_PASSWORD`
- runs `alembic upgrade head`
- starts uvicorn + RQ worker + watchdog under s6-overlay

### Create the first admin

Open SetVault in your browser; on a fresh install you'll be redirected to a
first-run wizard that creates your admin account. Nothing else to run.

**Headless / automation alternative.** To bootstrap the admin without the UI
(e.g. scripted provisioning), use the bundled CLI — it reads credentials from
the environment so the password never lands on the command line or in logs:

```bash
docker exec \
  -e ADMIN_EMAIL='you@example.com' \
  -e ADMIN_PASSWORD='a-strong-password-min-12-chars' \
  setvault python -m setvault_web.create_admin
```

- `ADMIN_EMAIL` (required) and `ADMIN_PASSWORD` (required, **≥ 12 characters**).
- `ADMIN_USERNAME` (optional, defaults to the email local-part) and
  `ADMIN_DISPLAY_NAME` (optional, defaults to the username).
- Idempotent: if the user already exists it is promoted to admin; if they are
  already an admin it is a no-op. Re-running is safe.

> **`SETVAULT_DEV_SEED` is dev/e2e only.** The `/api/dev/seed-e2e` endpoint it
> exposes ships a public, well-known credential — it exists solely for the test
> suite. **Never set `SETVAULT_DEV_SEED` in production.** Use the
> `create_admin` CLI above for real deployments.

### Option B — External datastores (compose)

For a managed/shared Postgres + Redis, or when you want to scale the app
separately. Provide `DATABASE_URL` and/or `REDIS_URL` and the bundled
datastores stay off (per-datastore — you can mix).

```bash
cp .env.example .env   # set BASE_URL + your DATABASE_URL/REDIS_URL (or POSTGRES_PASSWORD)
docker compose -f infra/docker/compose.yml up -d
```

This starts `postgres` + `redis` + `setvault` (tusd is inside the app image).

### Image reference

| Image | Pull | Arches |
|---|---|---|
| SetVault (web + worker + watcher under s6-overlay) | `ghcr.io/bardesss/setvault:latest` | `linux/amd64` + `linux/arm64` |
| `:latest` mirrors the most recent tag. | | |

### Verify signatures (optional but encouraged)

Every release image is signed with cosign (keyless, via GitHub OIDC).

```bash
cosign verify ghcr.io/bardesss/setvault:latest \
  --certificate-identity-regexp "https://github.com/Bardesss/setvault/.github/workflows/docker.yml@.*" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

SBOMs (CycloneDX JSON) are attached to each GitHub Release.

---

## ⚙️ Configuration

All configuration is via environment variables loaded from `.env`.
**Bundled (single-container) mode needs zero required vars** — `SECRET_KEY`
and the internal `POSTGRES_PASSWORD` are generated on first boot and `BASE_URL`
defaults to `http://localhost:1970`. External-datastore mode still needs
`BASE_URL` plus a `DATABASE_URL`/`REDIS_URL` (or a `POSTGRES_PASSWORD` for the
bundled datastore it replaces). Everything else is defaulted inside the image
or synthesized at first boot.

| Variable | Required | Default | What it does |
|---|---|---|---|
| `SECRET_KEY` | `auto` (generated on first boot if unset) | generated | Signs session cookies + HMAC URLs. **Rotate ⇒ all sessions invalidated.** |
| `POSTGRES_PASSWORD` | `auto` (bundled; generated if unset) | generated | Postgres password. Used by both the postgres container and the auto-synthesized `DATABASE_URL`. |
| `BASE_URL` | `bundled: auto · external: ✅` | `http://localhost:1970` (bundled) | Public URL the app is served from (used in emails, RSS feeds, embed URLs). Set your `https://` URL when internet-facing. |
| `DATABASE_URL` | optional | synthesized from POSTGRES_* | Set to use an external Postgres; unset = bundled datastore |
| `REDIS_URL` | optional | `redis://redis:6379/0` | Set to use an external Redis; unset = bundled datastore. RQ queue + rate-limit store |
| `TUSD_HOOK_SECRET` | optional | auto-generated on first boot | Shared secret tusd uses when calling back into setvault |
| `SETVAULT_*_PATH` | optional | `./.data/*` | Host paths for db / redis / media / cache / config / watch |
| `SETVAULT_VERSION` | optional | `latest` | Image tag. **Pin to an explicit version in production** (e.g. `0.6.0`) — the default floats on `latest` and an unattended pull can ship a breaking change. |
| `SETVAULT_HTTP_PORT` | optional | `1970` | Host port the setvault service binds (1970 — year of the first DJ live set) |
| `SETVAULT_DEV_SEED` | optional | unset | If `1`, enables the `/api/dev/seed-e2e` test endpoint. Dev/e2e only — for real installs use the first-run wizard. Unset in production. |
| `SETVAULT_ALLOW_INSECURE_COOKIE` | optional | unset | Force-off override for the session-cookie `Secure` flag. Normally unnecessary — `Secure` is derived from your `BASE_URL` scheme (mode B above). Only for unusual proxy setups; can relax the flag, never tighten it. Never set on an internet-exposed `https://` instance. |
| `SETVAULT_FORWARDED_ALLOW_IPS` | optional | — | Upstream IPs trusted to set `X-Forwarded-*` headers (e.g. just your reverse proxy's address). See the forwarded-headers warning below. |
| `PUID` / `PGID` | optional | `1000` / `1000` | Container user/group for bind-mount permissions |

### Reverse-proxy tips

- Set `BASE_URL` to your public **HTTPS** URL so signed enclosures and
  invite links resolve — and so the `Secure` session cookie sticks (see the
  HTTPS warning in the bundled section above).
- Forward `X-Forwarded-Proto` and `X-Forwarded-For`.
- The web service listens on port `1970`; tusd is internal-only and
  reached via the web service at `/uploads/`.

> ### ⚠️ Never publish port 1970 directly (external mode)
>
> SetVault **trusts** `X-Forwarded-*` headers (so it can see the real client
> scheme/IP behind your proxy). If port `1970` is reachable directly, a client
> can spoof `X-Forwarded-For` / `X-Forwarded-Proto` and defeat rate-limiting and
> the `Secure`-cookie logic. **Always** keep `1970` behind a reverse proxy that
> **strips client-supplied `X-Forwarded-For`** and sets it itself. Use
> `SETVAULT_FORWARDED_ALLOW_IPS` to scope which upstream IPs are trusted to set
> those headers (e.g. just your proxy's address).

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

> ### ⚠️ v0.6.0 Postgres 16 → 18 upgrade caveat
>
> The bundled stack now pins **Postgres 18** (previous SetVault builds used
> Postgres 16). A PG 16 data directory is **not** binary-compatible with PG 18
> — Postgres 18 will refuse to start on a 16 data dir. If you ran an earlier
> SetVault on Postgres 16, you must dump on 16 and restore into 18:
>
> 1. **Before upgrading**, on your still-running PG-16 instance, take a backup
>    via the admin backup endpoint (see [Backup & restore](#-backup--restore)).
> 2. Pull `v0.6.0` and start it on a **fresh** data directory (do not reuse the
>    old `/data/db`).
> 3. Restore the backup into the new PG-18-backed instance with the restore CLI.
>
> External-mode operators with managed Postgres should run their provider's
> `pg_dumpall` / major-version upgrade path instead.

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

### Restore

Restore is the inverse, via the bundled restore CLI. The backup tar contains
a `pg_dump` (`db.sql`) plus every media file keyed by MediaRoot. The CLI loads
the dump with `psql` and copies media back under each root's `host_path`.

```bash
# 1. Download the backup tar (authenticated admin session, as above).
# 2. Copy it into the container (or bind-mount it), e.g. to /data:
docker cp setvault-backup-2026-06-08.tar setvault:/data/restore.tar

# 3. Run the restore. It is DESTRUCTIVE — it overwrites the live database
#    and media files — so it refuses to run without --yes.
docker exec setvault \
  python -m setvault_web.restore /data/restore.tar --yes
```

- The DB dump is loaded first; the restore then re-reads the MediaRoots from
  the freshly restored database to know where each root's `host_path` is, then
  copies media into place. `psql` must be on `PATH` (it is in the image).
- `--yes` (or `RESTORE_CONFIRM=1`) is mandatory — without it the CLI exits
  rather than overwrite anything.
- **Bundled mode:** restore loads into the **embedded Postgres 18** — this is
  also the path to migrate a pre-v0.6.0 (PG 16) backup forward (see the
  [upgrade caveat](#-upgrading)). The DB password is never printed; the libpq
  URL passed to `psql` is redacted in all output.

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
        │ Postgres 18  │    │   Redis 7    │   │ ffmpeg+fpcalc│
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

### Hardening — firewall container egress (defense-in-depth)

URL-rip / source ingest hands URLs to `yt-dlp`, which follows HTTP redirects
**without an internal-IP guard**. The host allowlist (YT / SoundCloud /
Mixcloud / Internet Archive / Bandcamp) constrains the *initial* host, but an
allowlisted host could in principle redirect to an internal address. As
defense-in-depth, operators should **firewall the container/worker egress** to
block:

- the cloud metadata endpoint `169.254.169.254` (and `fd00:ec2::254`),
- RFC-1918 / link-local ranges (`10.0.0.0/8`, `172.16.0.0/12`,
  `192.168.0.0/16`, `127.0.0.0/8`, `169.254.0.0/16`).

This stops a redirect-based SSRF from reaching your metadata service or other
internal hosts even if it slips past the host allowlist.

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
| 6B — Set detail + engagement | ✅ merged | Set-detail 3-column rebuild, engagement SidePanel, tracklist editor (`v0.3.0`) |
| 6C — Global persistent player | ✅ merged | Persistent audio across navigation, bottom-sheet mini-player, full-screen player, MediaSession lockscreen (`v0.4.0`) |
| 6D — Admin & management surfaces | ✅ merged | Shared AdminTable/AdminForm/StatusBlock/EmptyState across 12 admin tabs, Settings, Sets/new (`v0.5.0`) |
| Bundled + external deploy | ✅ merged | Single-container (PG+Redis+tusd+Caddy) or external datastores from one image (`v0.6.0`) |
| Pre-launch hardening | ✅ merged | SECRET_KEY/cookie/CSRF gates, `create-admin` + `restore` CLIs, `pg_dump --clean` restore, SSRF/TLS docs (`v0.7.0`) |
| 7A — Ingest sources | ✅ merged | `IngestSource` plugin protocol + YouTube `ytsearch` search, admin Sources tab, `/search` Sources mode + Ingest (`v0.8.0`) |
| **7B — More sources + multi-source search** | **🚀 this release** | **SoundCloud + Mixcloud + Internet Archive sources; `/search` searches all enabled sources at once, merged + labelled, with per-source health isolation (`v0.9.0`)** |
| 7C–7D — Ingest power tools | ⏳ planned | Monitored entities + Discoveries inbox, per-source rate limits, quality rules + source-upgrade |
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
