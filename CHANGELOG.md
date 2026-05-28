# Changelog

All notable changes to SetVault are documented here. Format adheres to
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0](https://github.com/Bardesss/setvault/compare/v0.1.2...v0.2.0) (2026-05-28)


### Features

* **5c:** admin health page renders /api/admin/health (J11) ([2b2338e](https://github.com/Bardesss/setvault/commit/2b2338e66ef57349db7659c6c70fdfa81c960580))
* **5c:** admin new-version banner (J16) + expand admin nav with new 5C tabs ([625503a](https://github.com/Bardesss/setvault/commit/625503ad21c041a91cfdb9665396ac226558d9a5))
* **5c:** GET /api/admin/backup (J2) streams pg_dump + media-root tar ([2c2e0a9](https://github.com/Bardesss/setvault/commit/2c2e0a999a6d6ee50add81bce243bf7d415ce1e4))
* **5c:** library refresh webhooks (J15) - migration 0014 + model + dispatch worker + admin tab + ready.py fan-out ([546d01e](https://github.com/Bardesss/setvault/commit/546d01ec4a1d53ad20b69b2ae93e6c6282b144ec))
* **5c:** recycle bin admin tab (list / restore / purge-now) ([126ce2a](https://github.com/Bardesss/setvault/commit/126ce2a5990618bf5d7b61ebce5404d0ca8f76f2))
* **5c:** scheduled tasks admin tab + /api/admin/tasks list + run-now ([dde023d](https://github.com/Bardesss/setvault/commit/dde023dfde05e096dc036c7537684329c17542c9))
* **5c:** watch-folders + unmatched-inbox admin tabs (frontends to 5A APIs) ([4d4c0b3](https://github.com/Bardesss/setvault/commit/4d4c0b373bf3919005137527d2b009517b85ee41))
* **5d:** bulk-action job + endpoint (G7) — soft_delete / retag / move_root ([c5eb466](https://github.com/Bardesss/setvault/commit/c5eb46678cfec1da9846e7455a5fadff79c0ef44))
* **5d:** library row checkboxes + BulkActionToolbar (G7) ([8436789](https://github.com/Bardesss/setvault/commit/843678993dcfec0e268261e0501bac8432432f3f))
* **5d:** UserSetState.playback_rate (migration 0015 + state endpoint round-trip) ([0d17a09](https://github.com/Bardesss/setvault/commit/0d17a0960de04ae51bbdf4c9480abc9c4219defb))
* **5d:** variable speed (E4) + A↔B loop (E5) — slider control, [/]/\\ shortcuts, persist rate ([21a2677](https://github.com/Bardesss/setvault/commit/21a26777e634d3d514e7d4853c3c78ab8ba9a615))
* **admin:** /admin/providers — list/upsert/test connection ([800ea76](https://github.com/Bardesss/setvault/commit/800ea7668dc8e8fdbbda3917bfe4653db4129c0d))
* **admin:** users/connectors/storage/jobs/system tabs + API ([6b48907](https://github.com/Bardesss/setvault/commit/6b489078505a5230a1ebbe2df91499394bff7b12))
* **audit:** AuditEvent recorder + wired into invite/connector/media-root/user.disable ([5e3289c](https://github.com/Bardesss/setvault/commit/5e3289c0e318f87f8179b2e4be6092511a7ae808))
* **core:** alembic + async sqlalchemy engine + Base model ([6d8f3a0](https://github.com/Bardesss/setvault/commit/6d8f3a0385fcc0cdad571c2aab34fab592537265))
* **core:** ApiToken model + mint/resolve/revoke helpers ([ec9a62e](https://github.com/Bardesss/setvault/commit/ec9a62e2bdd64f0cceadac827b8eb2b5d645875d))
* **core:** argon2id password hashing + fernet at-rest crypto ([d39cf73](https://github.com/Bardesss/setvault/commit/d39cf73e881378aeb1cd557b98f2d38694626129))
* **core:** audit_retention prune scheduled job (J17) ([3a44ac4](https://github.com/Bardesss/setvault/commit/3a44ac4d31911afe52a1580e1c8295e3c01ec2cf))
* **core:** bundle yt-dlp via packages/core dependency ([207e2fa](https://github.com/Bardesss/setvault/commit/207e2fa8ba339241151ee00c5692a32b0d54c76c))
* **core:** catalog models (Artist/Venue/Series/Party/LiveSet/Tag/MediaRoot) ([6eb338d](https://github.com/Bardesss/setvault/commit/6eb338d76b14e4989202080923053a76df1513de))
* **core:** chromaprint dedup branches - published vs soft-deleted existing (audit + auto-undelete) ([978c2c9](https://github.com/Bardesss/setvault/commit/978c2c9f815631f8b763f46aa8110b6418d1cf8c))
* **core:** comments service — markdown sanitize + [@mention](https://github.com/mention) extraction + nesting rule ([207ebef](https://github.com/Bardesss/setvault/commit/207ebefbd698ed82f0f443100b2e7bd4f1f4533b))
* **core:** engagement + system models (state, favorites, history, connectors, jobs, audit) ([1303be9](https://github.com/Bardesss/setvault/commit/1303be91e92c59d7159c9d0bde4f611e55d474dc))
* **core:** engagement models — comments, bookmarks, notes, in-app notifications ([5ed0e04](https://github.com/Bardesss/setvault/commit/5ed0e046d531a3c5f0b5208bf3e2d15dcec1ef9b))
* **core:** enrichment orchestrator with cache + per-field priority ([44cb683](https://github.com/Bardesss/setvault/commit/44cb683b47b2224b4b77f999a9f72261064d4e44))
* **core:** github_version_poll scheduled job (J16, ETag-aware) ([670d700](https://github.com/Bardesss/setvault/commit/670d700038cb5ad3e3cb7eaae4f81cf3e6f601f0))
* **core:** LiveSet.embed_allowed ORM column ([42c91ea](https://github.com/Bardesss/setvault/commit/42c91ea3d0ab1e9700bf7976d6c22c8488e5a86d))
* **core:** naming-template resolver + reapply worker + admin endpoint ([9c77c01](https://github.com/Bardesss/setvault/commit/9c77c0145bf4826a3aff6d99722bbc8ad21ff16a))
* **core:** place_audio_file - hardlink on same fs, copy+atomic-rename otherwise ([6ac916e](https://github.com/Bardesss/setvault/commit/6ac916e17518ba2b5fc44eedb59506f320cc8035))
* **core:** progress pub/sub + /ws/sets/{id}/progress forwarder ([94c7f7e](https://github.com/Bardesss/setvault/commit/94c7f7e03b11f80f106241d02f457e1de0f32fb2))
* **core:** purge_recycle_bin scheduled job (J8) ([21dfb55](https://github.com/Bardesss/setvault/commit/21dfb557cc01d52452754173b68643c5545f38d8))
* **core:** pydantic schemas for engagement features ([4e09485](https://github.com/Bardesss/setvault/commit/4e09485cebe7a019dd8dcc3819e8ad64257a6cf0))
* **core:** pydantic schemas for URL-rip submit + list ([b99e9f6](https://github.com/Bardesss/setvault/commit/b99e9f6ea7b8016a11ad79e729f3bd765d8a2962))
* **core:** RipJob model + LiveSet.source_external_id ([82f070e](https://github.com/Bardesss/setvault/commit/82f070e1eb615ff9c7ce6c9ca9233727011e7c56))
* **core:** RSS feed builder + schemas (feedgen-based, tracklist in description) ([87375ec](https://github.com/Bardesss/setvault/commit/87375ecdca4456d629d1e73cf3f5a6732999ce61))
* **core:** send_email_job + auto-enqueue from invite/reset endpoints ([37b4237](https://github.com/Bardesss/setvault/commit/37b4237f202daf712ee94f0bb190fa7d854f7cd9))
* **core:** SystemConfig singleton model + get_config helper ([4f61a08](https://github.com/Bardesss/setvault/commit/4f61a084d7f0051ae3e9c5c4544aef26adc3e662))
* **core:** Track DB + TracklistEntry models ([f835dbf](https://github.com/Bardesss/setvault/commit/f835dbf3a93e174179b9d7be1774aaae7b9d0d31))
* **core:** tracklist pydantic schemas ([543b69b](https://github.com/Bardesss/setvault/commit/543b69b7695ebeb9476ef0c8ee58536b5cd6a13e))
* **core:** tracklist service + paste regex parser ([45ece68](https://github.com/Bardesss/setvault/commit/45ece68ba0046763ad2a7fa8b46c6638752ee52b))
* **core:** url_rip service - probe + submit + idempotency ([002fb55](https://github.com/Bardesss/setvault/commit/002fb55e48cd15d856a02cae16fbcbe8ab1a1b4d))
* **core:** URL-rip worker job (RQ entry point + pipeline) ([81ba3a4](https://github.com/Bardesss/setvault/commit/81ba3a4de8a087f2c9071f5edc1638e38ace5f5e))
* **core:** User + EmailToken + NotificationPreference models ([23265b0](https://github.com/Bardesss/setvault/commit/23265b0a9053bf0803dbbe54545b8e6fe5e261b7))
* **core:** watch_folder_ingest job - filename parse + place + pipeline trigger / unmatched ([d31c37c](https://github.com/Bardesss/setvault/commit/d31c37c3991641cae8487de4957eb4a2906eddf3))
* **core:** watcher service - watchdog observer + RQ enqueue per audio file event ([c78b529](https://github.com/Bardesss/setvault/commit/c78b529cb772b97defad445db5a10a316b756260))
* **core:** WatchFolder + UnmatchedFile ORM models ([6f4dfb1](https://github.com/Bardesss/setvault/commit/6f4dfb14418bee528b2262b9f524777dc3525744))
* **core:** wire email delivery into the engagement notification dispatcher ([97b2dfd](https://github.com/Bardesss/setvault/commit/97b2dfd554c79e5f70d7eb7f208e00d71ed720b4))
* **db:** migration 0006 — Track DB + tracklist tables ([e6e7093](https://github.com/Bardesss/setvault/commit/e6e70932c6c136c082833f8d8e5c8d5f74a3e366))
* **db:** migration 0007 — provider configs + response cache + resolve jobs ([fd6d26b](https://github.com/Bardesss/setvault/commit/fd6d26b8741ff1f0519416d96cdbf735656ad897))
* **db:** migration 0008 — comments + bookmarks + private notes + in-app notifications ([1422998](https://github.com/Bardesss/setvault/commit/142299887070c33b3123d4cf4cbd02258912f972))
* **db:** migration 0009 - rip_jobs table + live_sets.source_external_id ([7121b2e](https://github.com/Bardesss/setvault/commit/7121b2ef0ad52512c6ded536390c9bdef9e8e026))
* **db:** migration 0010 - api_tokens (scoped, hashed, per-user) ([7a61866](https://github.com/Bardesss/setvault/commit/7a61866e3293b4bab81218ecb8b6ea7b56b821d9))
* **db:** migration 0011 - live_sets.embed_allowed ([04e28c8](https://github.com/Bardesss/setvault/commit/04e28c843c958011ff041a62861cd6eeeb8f2ccd))
* **db:** migration 0012 - watch_folders + unmatched_files ([1f4a0c7](https://github.com/Bardesss/setvault/commit/1f4a0c7a0202b70420c0838a2d76508938f2f25c))
* **db:** migration 0013 - system_config singleton (release-poll cache + audit retention) ([74b6a4e](https://github.com/Bardesss/setvault/commit/74b6a4e844f8d74b9161cfde88a7d8d29fddd8e4))
* default HTTP port 1970 (year of the first DJ live set) ([ce490ef](https://github.com/Bardesss/setvault/commit/ce490ef939fa52b5d3762626ee33d21f362ffce8))
* default HTTP port 1970 (year of the first DJ live set) ([986c889](https://github.com/Bardesss/setvault/commit/986c8893b408debcb84c98fc92c1904b5e3b3f72))
* **frontend:** /embed/[slug] route - slim chrome embed player ([1b4d0e7](https://github.com/Bardesss/setvault/commit/1b4d0e7bd0dff785ad7b77385a01cf66fdf22f0a))
* **frontend:** /settings — profile + change password ([7b8cca2](https://github.com/Bardesss/setvault/commit/7b8cca2b67f11989720ec9b7f6f482893a7c2ab6))
* **frontend:** admin embed toggle on set detail + Playwright e2e (embed, rss) ([d1d3b0b](https://github.com/Bardesss/setvault/commit/d1d3b0b6c507e78b8d2d47cfdd68df69a3f8f14c))
* **frontend:** api client + session store + nav rail + /login route ([0b2d1f2](https://github.com/Bardesss/setvault/commit/0b2d1f2d7ef9295662e9b66fa929954f6d747ae7))
* **frontend:** bookmark button + B shortcut + /me/bookmarks page ([17dd126](https://github.com/Bardesss/setvault/commit/17dd1265c33791fa514048eb9b986f152e5e1f29))
* **frontend:** collapsible private notes panel per set ([485fa4b](https://github.com/Bardesss/setvault/commit/485fa4bcd4c13612286c4d0f25bcbd9af470713c))
* **frontend:** comment dot markers on waveform ([c75d027](https://github.com/Bardesss/setvault/commit/c75d027f8eb6cd77925c735e8cf92e2dc3ed77e0))
* **frontend:** comment thread + composer with [@mentions](https://github.com/mentions) ([faac534](https://github.com/Bardesss/setvault/commit/faac534b3851553e2355c6fa9ed6872caa0ea55b))
* **frontend:** engagement API clients + notifications store ([11b7cc0](https://github.com/Bardesss/setvault/commit/11b7cc02e6771b55841b1975e4c64dcd6e9b1f80))
* **frontend:** home (continue + recent + activity) + library route ([799137c](https://github.com/Bardesss/setvault/commit/799137ca9d92cb7df89d0bf4db7b565d35fec616))
* **frontend:** invite + reset redemption routes ([c36c015](https://github.com/Bardesss/setvault/commit/c36c0153f4bd261de85bb800f2e3d12f63af9255))
* **frontend:** live Tracklist sidebar with M key + cycle + click-to-seek ([a88a585](https://github.com/Bardesss/setvault/commit/a88a58570127a3a45a37384860442933f9fe6cec))
* **frontend:** mediaSession prev/next jumps to tracklist entries + artwork ([5940949](https://github.com/Bardesss/setvault/commit/59409496a59f3890996b7417e0d98fdc728d8b0d))
* **frontend:** offline audio cache widget (cap presets, usage, clear) ([2583b67](https://github.com/Bardesss/setvault/commit/2583b67ae5fde53c8a560d4d8e123081c26f8747))
* **frontend:** phone bottom-tab NavRail + breakpoint tokens ([cf62fb2](https://github.com/Bardesss/setvault/commit/cf62fb244e89c73fe9669af44b94fcdde374775b))
* **frontend:** poll active URL-rip jobs in Add Set tab ([30d8100](https://github.com/Bardesss/setvault/commit/30d81005287dd995b5b593755fdb4ef2c8b47b3a))
* **frontend:** PWA manifest + maskable icons + theme-color meta ([972cf19](https://github.com/Bardesss/setvault/commit/972cf198f083498d6ba1bbc2769c59b47c93fe41))
* **frontend:** resolve candidates popover + bulk-resolve button ([60184d4](https://github.com/Bardesss/setvault/commit/60184d43670c0dc2dd8d2067145257a9dc555be2))
* **frontend:** service worker scaffold + registration on layout mount ([6d79fae](https://github.com/Bardesss/setvault/commit/6d79fae563e0c9d8f28c94bafb7dc524fa34b968))
* **frontend:** set detail page with wavesurfer player + resume + keyboard ([beb4dd7](https://github.com/Bardesss/setvault/commit/beb4dd75ee7c009cd7eabd6eab2347fd0a2dc58a))
* **frontend:** sveltekit skeleton with phase 1 design tokens ([d5a6149](https://github.com/Bardesss/setvault/commit/d5a6149720e0b11dc612793c58961b8f0155af19))
* **frontend:** SW fetch handler + route-based cache strategies (Vitest 8/8) ([2e672d9](https://github.com/Bardesss/setvault/commit/2e672d9909f3bb35ec5cffb781d8db373cfdf3be))
* **frontend:** tracklist API client + store ([dcdfa3f](https://github.com/Bardesss/setvault/commit/dcdfa3f0e2c72a6482b97503b402dea5db312e64))
* **frontend:** tracklist edit drawer ([b0174f5](https://github.com/Bardesss/setvault/commit/b0174f55869622286e16cd01a691ed448ff274cd))
* **frontend:** tracklist import modal — paste/URL/OCR with diff preview ([ed4f03b](https://github.com/Bardesss/setvault/commit/ed4f03b753afda46a33aba3a67072b85deef466e))
* **frontend:** tracklist time-shift dialog ([be710ee](https://github.com/Bardesss/setvault/commit/be710eee7eb6a96c348d4420c12847e2bc5e89fe))
* **frontend:** tus.io resumable uploader + /sets/new route ([c8043d6](https://github.com/Bardesss/setvault/commit/c8043d655593506d8ae33acd00336789a9929f22))
* **frontend:** URL-rip tab + RipJobRow + recent-rips list ([bc7bb30](https://github.com/Bardesss/setvault/commit/bc7bb3072e747a7521907f13d31d10051db7a227))
* **i18n:** svelte-i18n bootstrap + en locale + crowdin sync workflow ([997d226](https://github.com/Bardesss/setvault/commit/997d226ec147216f61c97e35432951337a98a492))
* **i18n:** tracklist editor strings + drop Phase-2 placeholder ([6a9dc9d](https://github.com/Bardesss/setvault/commit/6a9dc9d53e1f603523b51339fcec1c6083b74d9f))
* **infra:** multi-arch web image with bundled frontend + production compose ([25095dc](https://github.com/Bardesss/setvault/commit/25095dc59a89596aa241a161b96bdfbd83a94611))
* **infra:** watcher compose service runs setvault_core.services.watcher ([f4efb67](https://github.com/Bardesss/setvault/commit/f4efb67c6009d103f6cc551d29622e6bf4547a30))
* **jobs:** chromaprint fingerprint + dedup detection ([d7f5549](https://github.com/Bardesss/setvault/commit/d7f5549b86aabe8286564a3c4521379c79f595aa))
* **jobs:** ffmpeg transcode to Opus 128k streaming copy ([90f75fe](https://github.com/Bardesss/setvault/commit/90f75fe770a946f2e0ac75fb7284d98baaec49cb))
* **jobs:** normalize (EBU R128) + waveform peaks + mark-ready with activity event ([fe8b54f](https://github.com/Bardesss/setvault/commit/fe8b54faddb33f8c77677eb2cd42f8c88ea384c4))
* **jobs:** pipeline orchestrator + ffprobe duration job ([92c3ce0](https://github.com/Bardesss/setvault/commit/92c3ce07df090aeefa54dc729920439b9ee2d3f5))
* **providers:** AcoustID provider (chromaprint fingerprint + lookup) ([668efac](https://github.com/Bardesss/setvault/commit/668efac6ddb099529194f7c0e2cbc18e733dcabe))
* **providers:** Discogs provider (enrich_track via release search) ([a08c119](https://github.com/Bardesss/setvault/commit/a08c1191be6eedc361126eabdf0ebbcce4c2ee90))
* **providers:** MusicBrainz provider (enrich_track + lookup_by_isrc) ([5f014f3](https://github.com/Bardesss/setvault/commit/5f014f382e6a4c25f92249a70736e574e708c956))
* **providers:** new packages/providers workspace + Provider Protocol ([781434a](https://github.com/Bardesss/setvault/commit/781434ac31c81f0ffa55b521dd21e6358788f990))
* **search:** FTS generated tsvector columns + /api/search endpoint + route ([72c85f1](https://github.com/Bardesss/setvault/commit/72c85f12c6b60eb74f4976f50dced0faf6924871))
* **v0.1.1:** single all-in-one container, 3-required-env config ([2c0ff99](https://github.com/Bardesss/setvault/commit/2c0ff995831da070000f56f73217eabe75485def))
* **v0.1.1:** single all-in-one container, 3-required-env config ([cb71ce1](https://github.com/Bardesss/setvault/commit/cb71ce141f4bd6d5e8952b8068b6b9d456162baa))
* **web,frontend:** /api/me/rss-tokens (list/create/revoke) + Settings RSS section ([4707df7](https://github.com/Bardesss/setvault/commit/4707df7170fae84d5bfc2ff85b368303078ddf98))
* **web:** [@mention](https://github.com/mention) + comment-reply notifications (in-app dispatch) ([1781fcc](https://github.com/Bardesss/setvault/commit/1781fcc26d98c9f634d5213f99dddec8a527a6b8))
* **web:** /api/admin/providers CRUD + test-connection ([7e208f2](https://github.com/Bardesss/setvault/commit/7e208f265d9cfb462ee78545ecd74b085183ecc2))
* **web:** /api/admin/watch-folders + /api/admin/unmatched (CRUD + resolve) ([e7923f5](https://github.com/Bardesss/setvault/commit/e7923f5a013248621c8a460160fa2f7a44cb95ba))
* **web:** /api/auth login + logout + me with signed-session cookie ([5eef624](https://github.com/Bardesss/setvault/commit/5eef6248d4939a62ce101d5ac7d470a2ac246c42))
* **web:** /api/feed/{kind}/{token}.xml (favorites/recent/everything) ([d560d83](https://github.com/Bardesss/setvault/commit/d560d83f09a1acec3f97a2189be14faedb49c0df))
* **web:** /api/sets/{slug}/comments + /api/comments/{id} CRUD ([6f34b04](https://github.com/Bardesss/setvault/commit/6f34b0454d312a9e8dd8b8030ec025d189c6bb87))
* **web:** /api/sets/{slug}/embed + admin embed toggle (public stream when allowed) ([2e91634](https://github.com/Bardesss/setvault/commit/2e916344fe18fbd139f2ab16d24d86c7fdd3b8b6))
* **web:** /api/sets/{slug}/tracklist CRUD + reorder ([4ab179a](https://github.com/Bardesss/setvault/commit/4ab179aacc922114bc38b76ce8b2816ee749a110))
* **web:** /api/sets/{slug}/tracklist/entries/{id}/resolve + accept ([04ab3a5](https://github.com/Bardesss/setvault/commit/04ab3a5c09cc8c8f8deca162fce9c5b7c8e5b4d9))
* **web:** /api/sets/url-rip + /api/me/rip-jobs ([6f02ca7](https://github.com/Bardesss/setvault/commit/6f02ca726e48e9024d7f1c58689b66f55aa563d3))
* **web/frontend:** notification bell + preferences + engagement e2e ([68588a3](https://github.com/Bardesss/setvault/commit/68588a35c1b0ffe0bee64ad2ff900fcee63bb051))
* **web:** 1001tracklists scrape import (admin-gated) ([fd0e9e7](https://github.com/Bardesss/setvault/commit/fd0e9e74ea804b6667d19088c083c5d56eb921e7))
* **web:** AcoustID ID-this endpoint ([023e549](https://github.com/Bardesss/setvault/commit/023e549eb3e00fdbd9f6ba895f6ec3c41932cf43))
* **web:** admin invite create + redeem with copy-paste fallback link ([b1b3cc6](https://github.com/Bardesss/setvault/commit/b1b3cc66656abf3a762089077e1ab9216c908bcc))
* **web:** artist/venue/series/party CRUD with slug generation ([0917704](https://github.com/Bardesss/setvault/commit/0917704d0e87cf9fc6e8f99018248657d0c9ecb0))
* **web:** bookmarks + private notes API ([963f901](https://github.com/Bardesss/setvault/commit/963f901a680eab12dcc05856e7ee69e09ed0d141))
* **web:** bulk-resolve endpoint with WS progress ([560384d](https://github.com/Bardesss/setvault/commit/560384df0e11cac82e4c9f063a1fe115a4d92fb6))
* **web:** bundle feedgen for RSS generation ([6f0be38](https://github.com/Bardesss/setvault/commit/6f0be382b71b85b71b45a5d1d4431c3c5a555b34))
* **web:** CSRF + security headers + auth-strict rate limit ([80b108e](https://github.com/Bardesss/setvault/commit/80b108e0a142fa9d59491222f3fb28d05bbf32a9))
* **web:** GET /api/admin/health - consolidated J11 snapshot ([9508d2c](https://github.com/Bardesss/setvault/commit/9508d2c0ee9b819de4f3f46f8c7500e38ad0fbb4))
* **web:** LiveSet list/get/edit/soft-delete + stream + waveform endpoints ([7a28bd0](https://github.com/Bardesss/setvault/commit/7a28bd07ff6c72b90eafc376f07096a206318f8a))
* **web:** MediaRoot admin CRUD + health probe at create ([99c9364](https://github.com/Bardesss/setvault/commit/99c9364f2fd520a723c2428742b13d5ed47222d3))
* **web:** OCR tracklist import via Tesseract ([96fef85](https://github.com/Bardesss/setvault/commit/96fef8520876cb0b7ee9866311d356bec661b1bb))
* **web:** password reset request + admin copy-paste link + redeem ([5f5d3f1](https://github.com/Bardesss/setvault/commit/5f5d3f100a96736b7853b24f1f7cb94f0a1e257c))
* **web:** per-route CSP - allow frame-ancestors on /embed/* and /api/sets/*/embed ([4fdfd15](https://github.com/Bardesss/setvault/commit/4fdfd15c2993acf2cd52ab013bcecdc7b4ebcfa8))
* **web:** rate limits + audit events for enrichment ([641014d](https://github.com/Bardesss/setvault/commit/641014dcf90fcdc4c452288dce6dc9f82578c4d0))
* **web:** rate-limit URL-rip submission to 5/hour 50/day per user ([dc4f716](https://github.com/Bardesss/setvault/commit/dc4f7161db0f16e9ddc9bb3a1fd27cf66c1615ca))
* **web:** SMTP NotificationConnector CRUD + test-send (dry-run) ([7ba9716](https://github.com/Bardesss/setvault/commit/7ba9716f21330e75a24d62e5d4cdf9973f78dbae))
* **web:** stream + waveform accept ?token= for podcast-app access ([89346f1](https://github.com/Bardesss/setvault/commit/89346f1ac88c1c129437496e36b56ffc9f531292))
* **web:** tracklist paste import + accept ([c3c3ec2](https://github.com/Bardesss/setvault/commit/c3c3ec257c532a3802b3fca4d86eb37b4f8f30e5))
* **web:** tracklist time-shift endpoint ([38916ac](https://github.com/Bardesss/setvault/commit/38916ac03e69fc2df5222623b0fa79610b8c24c6))
* **web:** tusd hook handler — creates LiveSet draft, hardlinks file, enqueues pipeline ([fcb61b3](https://github.com/Bardesss/setvault/commit/fcb61b3a1b72917e1fc96e3a4e4704cb4022ed22))
* **worker:** periodic MediaRoot health-check job (5min) ([61a475c](https://github.com/Bardesss/setvault/commit/61a475c4a6f1723c96241708203af5391fc05e4e))
* **worker:** register all 5B scheduled jobs (purge, version-poll, audit-prune) ([38b973f](https://github.com/Bardesss/setvault/commit/38b973f7057959b0eb43a6e726032f1abe89e742))


### Bug Fixes

* /api/admin/health uses real ProviderConfig + NotificationConnector field names ([cc5bc5f](https://github.com/Bardesss/setvault/commit/cc5bc5f23de976d3641a0c3986de220df955e466))
* **5e:** make set-cap enforce immediately + simplify eviction test ([8021abf](https://github.com/Bardesss/setvault/commit/8021abfdf4881a15a42dd64a2b1a0ccf0f9cffc8))
* **auth:** match delete_cookie attrs, guard uuid parse, trim SessionData ([8215f11](https://github.com/Bardesss/setvault/commit/8215f11abd37d785407a9f8ed672cfc2c7089a91))
* **auth:** rate-limit invite redeem + correct deferred-FK migration ref ([d3d4a76](https://github.com/Bardesss/setvault/commit/d3d4a769c9632fe4ddb3aeeef331316b4fdca76f))
* **ci:** remove unused postgresql import from migration 0013_5b ([4f9bc32](https://github.com/Bardesss/setvault/commit/4f9bc32896d08edd4fdcd7861b590c4dfb7655dd))
* **ci:** ruff clean on 4A scope (I001/E501/ASYNC240/S110) ([36e5ae9](https://github.com/Bardesss/setvault/commit/36e5ae950cad662bd5f3fe2a84905854bfe39310))
* **ci:** ruff clean on 4B scope (I001/E402 — me.py imports moved to top) ([8c9860a](https://github.com/Bardesss/setvault/commit/8c9860ad360da882ace4abdedea131bb91d30c22))
* **connectors:** log + sanitize SMTP errors; note deferred D2 import ([aaebe58](https://github.com/Bardesss/setvault/commit/aaebe586aae06465379108f0aa9b5f1e0f56e130))
* **core:** engagement models — ORM server_defaults + __init__ registration ([d3bc193](https://github.com/Bardesss/setvault/commit/d3bc193d6878728f2390940f763cce8fe46250e0))
* **db:** deferrable unique constraint on tracklist_entries (live_set_id, position) ([981f583](https://github.com/Bardesss/setvault/commit/981f583c26f4d68efd5006522a102fa16e7d013f))
* **design/home:** stop "Continue listening" card text from overlapping ([8c4230a](https://github.com/Bardesss/setvault/commit/8c4230ab6a122e4066ae2ee3f67e01b4a284b69a))
* **design:** Home card overlap + responsive layouts for narrow widths ([f769099](https://github.com/Bardesss/setvault/commit/f769099249f4d67b9ecedfb9dd99dc794669cfd2))
* **design:** responsive layouts for set-detail & tracklist-editor ([20af1fa](https://github.com/Bardesss/setvault/commit/20af1fad6d28b8b886d15400ea4901a47a493db4))
* **dev-seed:** pg_advisory_xact_lock to serialize parallel seeders ([7a65f8a](https://github.com/Bardesss/setvault/commit/7a65f8a2d8c41722b1ca4199f59f73637c9abcae))
* **docker:** include packages/providers in workspace builds ([8f4a107](https://github.com/Bardesss/setvault/commit/8f4a1079dce94f28d27405cd7c215cbb2bb5f8d0))
* **docker:** include packages/providers in workspace builds ([79ce4fc](https://github.com/Bardesss/setvault/commit/79ce4fce154fa7d131d7e305a512abebe222c5f4))
* **frontend:** a11y label on comment textarea + i18n the [deleted] placeholder ([d62746f](https://github.com/Bardesss/setvault/commit/d62746f3cb6304faabfbe0685c9bf759143f0dd4))
* **frontend:** stabilize engagement e2e tests ([c308a64](https://github.com/Bardesss/setvault/commit/c308a643109470751060c2241c3f3a645bf4f4ad))
* **frontend:** use cookies API for exact session-cookie match ([cd0ce53](https://github.com/Bardesss/setvault/commit/cd0ce53f56dbabc932b9dd7ece00d9496957419d))
* **infra:** bind postgres host port to 127.0.0.1 only ([9d32e03](https://github.com/Bardesss/setvault/commit/9d32e030f2887a98732f671b9da2c1d3976e8ade))
* **media-roots:** probe OSError catch + dedupe HealthStatus + DELETE tests ([3c9567e](https://github.com/Bardesss/setvault/commit/3c9567ea9a537369e93faf97c71f52907f58aa07))
* **security:** HMAC-signed short-TTL enclosure URLs (narrow RSS token blast radius) ([78b2247](https://github.com/Bardesss/setvault/commit/78b224794acf4e4732c2bf5b47547eaa1c7cec1c))
* **security:** URL-rip SSRF allowlist + sanitized error_text ([1036bb2](https://github.com/Bardesss/setvault/commit/1036bb23c136fa322677047c340d3ce9d22dbf91))
* **test:** dispose SQLAlchemy engine between tests to clear stale pool ([dc6ae7c](https://github.com/Bardesss/setvault/commit/dc6ae7cb19d9e11a02804618ebead486b110dcc8))
* **test:** mark test_full_reset_cycle as flaky (BaseHTTPMiddleware event-loop race) ([3ce0388](https://github.com/Bardesss/setvault/commit/3ce038807cb918e3813a1aecfcee5699ccd7c78c))
* **test:** seed streamable file in stream-auth tests (was failing with 404, expecting 401) ([f025a5b](https://github.com/Bardesss/setvault/commit/f025a5b37f75974029d346be5343eb5c7c2e0ec2))
* **test:** xfail test_full_reset_cycle (reruns insufficient) ([626514b](https://github.com/Bardesss/setvault/commit/626514b5ae4ecc23da00c773f3edcf669b661d51))
* **web/frontend:** accurate comment total + hide delete from non-owners ([7f6befc](https://github.com/Bardesss/setvault/commit/7f6befc4ad9ce0aaef0eb678c51776a2601d22dc))
* **web:** narrow bookmark IntegrityError catch; drop dead notes test ([19286c8](https://github.com/Bardesss/setvault/commit/19286c8792d52f906c8cd075deff13cf74b7120b))
* **web:** rename audit alias and cover admin-delete audit path ([51f79fb](https://github.com/Bardesss/setvault/commit/51f79fb737b07bef5c8299fd53eb030f486fec50))
* **web:** revert apps/web enqueue_email refactor to keep existing tests stable ([9e4bac5](https://github.com/Bardesss/setvault/commit/9e4bac5ce82a2f558bee6fece5066491babd52b5))


### Refactors

* **5e:** pure-ASGI CSRF + SecurityHeaders middleware ([3dfe4f3](https://github.com/Bardesss/setvault/commit/3dfe4f3e00ad18743a4ddeb33c19e9b2ced0fd68))
* **frontend:** static-import tracklist child components ([ce91b30](https://github.com/Bardesss/setvault/commit/ce91b3077fb72876574142ec58322b118a96b743))
* **notifications:** enqueue helper + graceful degradation; Date/Message-ID headers; widen quit catch ([54c3850](https://github.com/Bardesss/setvault/commit/54c385096b9189a1397e36de5c3f9c8cf22bd5b1))


### Documentation

* **5f:** v0.1.0 CHANGELOG, README rewrite, landing page ([e8e232d](https://github.com/Bardesss/setvault/commit/e8e232d21be51d2179fa09263442c2845601b05d))
* add SetVault design spec ([5b57949](https://github.com/Bardesss/setvault/commit/5b5794955e600d3d396fd91950b8f7959cef921b))
* **core/web:** clarify spec-confirmed defaults in engagement code ([558c4a3](https://github.com/Bardesss/setvault/commit/558c4a3860af52e5685b12d68cd1b949fbf191b0))
* **readme:** add AI-assisted disclosure ([4323f29](https://github.com/Bardesss/setvault/commit/4323f298435895eb0ad54d29006ed03a4bfe69ed))
* **readme:** add Phase 5 (pre-v0.1.0 completion), renumber downstream ([910d799](https://github.com/Bardesss/setvault/commit/910d7991a8fbac8a0ea46ca3a7a3824d1e5ed7ea))
* **readme:** add Phase 5 (pre-v0.1.0 completion), renumber later phases ([2317f25](https://github.com/Bardesss/setvault/commit/2317f2556717b52d362d34925ff8065a5f7aa415))
* **readme:** status table + Crowdin translation guide + AI-assisted disclosure ([36000a2](https://github.com/Bardesss/setvault/commit/36000a20174b6ed07d8fd8a4d9b1853fea24b8b0))
* **readme:** status table + translations / Crowdin instructions ([b618bba](https://github.com/Bardesss/setvault/commit/b618bbad00ac4b0cb272d71e7a9d94bcd7530100))

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
