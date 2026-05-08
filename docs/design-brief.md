# SetVault — Design Brief

> Paste this prompt into a fresh Claude session (Claude Code or claude.ai) when you want help with the visual/UI design of SetVault. It is self-contained: the receiving Claude needs no other context.

---

## The prompt

Hi — I'd like help with the **visual and UI design** of a self-hosted web app called **SetVault**. Please use the `frontend-design` skill for this conversation.

### What SetVault is

SetVault is a self-hosted live-set manager for a small private group of DJ-music enthusiasts (≤10 users). Members upload or rip recorded DJ sets (from YouTube/SoundCloud/Mixcloud via `yt-dlp`), manage the catalog (artists, parties, venues, time-coded tracklists), and play sets back in-app or stream them to other clients (Sonos, Chromecast, DLNA, Subsonic apps, podcast apps via RSS).

Think of it as the love child of Mixcloud, 1001tracklists, and a Plex-style self-hosted media server — but for **DJ live sets specifically**, not for individual tracks.

### Audience & emotional tone

- **Users:** crew of friends — producers, DJs, club regulars. They care about provenance, tracklists, mashup notes, label info. They want to find that one ID-rolling moment from "Awakenings 2024 closing set."
- **Use context:** late evenings, headphones, sometimes booming on a Sonos, sometimes phone in pocket on a train. Lock-screen / mobile / casting matters.
- **Brand mood** — open to direction, but it should feel **club-rooted, deliberate, slightly underground**, not generic-streaming-app-dark. Not Spotify-clone-green-on-black, not corporate. Closer to vinyl-store website / Resident Advisor / a well-designed boutique label site than to a SaaS dashboard.
- **The product respects density.** Tracklists are inherently information-rich (timestamps, artists, mixes, mashups, label, BPM, key, status badges). The design should make that density readable, not strip it back.

### Key screens (in priority order)

1. **Set detail / player view** — the marquee screen. Sticky audio player with waveform (wavesurfer.js), tracklist sidebar that highlights the currently-playing entry, time-stamped comments as markers on the waveform, keyboard-driven editing UI, mini-player when scrolled. This is where most user-time is spent. Get this right and the rest follows.
2. **Tracklist editor** — three input modes (live "mark playhead" while listening, paste-and-parse messy text, import from URL). Each entry has a status badge (raw / resolved / acoustid_confirmed). Bulk-resolve flow. Time-shift dialog. Drag-to-reorder.
3. **Library list / browse** — filterable grid + dense-row toggle. Filter sidebar (artist/party/venue/venue-kind/year/duration/genre/source). Cover art, duration, party/venue line.
4. **Home / activity feed** — "Continue listening," "Recently added," activity feed of crew uploads/edits/comments.
5. **Artist / Party / Venue / Series detail** — entity hub pages. Hero image, metadata, sets-by-this-entity grid.
6. **Search results** — global FTS with type-segmented results (Artists, Sets, Parties, Tracks).
7. **Admin** — Users, Providers, OIDC, Email, Jobs, Storage, Backup, System tabs. Functional/dense; doesn't need to be pretty, but should not feel like 2010 phpMyAdmin.
8. **Settings / account** — scrobbling, RSS token, API tokens, notification preferences.
9. **Embeddable player** (`/embed/<set>`) — minimal, iframe-friendly, no chrome.
10. **Mobile / PWA** views — bottom-sheet mini-player, drawer-style sidebar, swipe gestures on tracklist rows.

### Constraints & non-negotiables

- **Stack:** SvelteKit + TypeScript. Open to your CSS recommendation (Tailwind, vanilla CSS modules, UnoCSS, etc.) — pick what fits.
- **Audio:** wavesurfer.js v7 for waveform rendering. Web Audio API for playback. MediaSession API for lockscreen.
- **Real-time:** WebSocket for job progress, listen-together sync, live-updating activity feed and now-playing.
- **Responsive:** must work cleanly from 360 px phone up to 4K monitor. PWA-installable.
- **Themes:** dark by default; light mode required. System-preference aware. Color palettes should not feel like trivial inversions of each other.
- **Accessibility:** WCAG AA contrast, keyboard navigation throughout (the player especially), `prefers-reduced-motion` honored, focus visible, ARIA where needed.
- **i18n-ready:** assume the strings will live in a translation layer. Designs should accommodate longer text in DE/NL/FR.
- **Performance:** SSR-first, lean bundles, no heavy chart/illustration libraries unless necessary. Prefer SVG icon set over icon fonts.
- **Customizability:** small group of crews may want to swap accents / wordmark. Bake in a few CSS variables for theming.

### What I'd like out of this conversation

Use `frontend-design` to drive the conversation. I'd like:

1. **A short discovery pass** — clarify visual direction with me using the visual companion (mockups in browser). Show 2–4 distinct directions for the set-detail player view first; once we pick a direction, build out from there.
2. **A design language** — type stack, color palette (dark + light), spacing scale, radius system, motion principles, a small icon vocabulary. Concrete CSS variables.
3. **High-fidelity mockups for the top 5 screens** above. Real content, not Lorem Ipsum — use real-looking artist/party names and a representative tracklist. Show both desktop and mobile breakpoints for the player view.
4. **A reusable component sketch list** — buttons, inputs, dialogs, tabs, cards, status badges, the tracklist row, the entity hero header, the filter sidebar. Just the patterns; production code comes later in implementation phases.
5. **A landing-page mockup** — shares design tokens and component primitives with the app (same color palette, typography, buttons, badges) but uses editorial composition (big hero, scroll-driven feature sections, screenshot/video demos, generous whitespace) — distinct from the app's dense utility layouts. Same brand vocabulary, different sentences. Think Linear's marketing site vs. Linear the app. Sections: hero, what-is, feature gallery, system requirements, quickstart, footer. Will live on GitHub Pages.
6. **Accessibility & responsive notes** baked into each mockup, not bolted on after.
7. **A live preview index** at `frontend/design/index.html` — lists every mockup and component page with thumbnail and link, so I (and the crew) can browse the whole design at any time by running `npx serve frontend/design` or equivalent. This is the artifact that survives the design session and lets implementation phases reference real rendered HTML, not screenshots.

### Reference material

- The full system spec is at `docs/superpowers/specs/2026-05-08-setvault-design.md` in the repo. Read sections **§2 (feature catalog)**, **§4 (data model)**, **§6 (catalog management UX)**, **§7 (playback)**, and **§8 (frontend routes)** for the screens and data shapes you'll be designing around.
- Phasing in **§9** — **this work IS Phase 1.** No backend/app code yet; this phase produces the design language, the top-5 mockups, and the landing-page direction that subsequent phases (Core vault, Tracklist & enrichment, etc.) build against. Output should land in `frontend/design/` as committed HTML/CSS prototypes that can be referenced from implementation phases.

### Inspiration starting points (not requirements — push back if they're wrong)

- **Resident Advisor** — restrained, editorial, content-first, dense without feeling cramped.
- **Bandcamp / Boomkat** — physical-product-feel, generous covers, type-driven hierarchy.
- **Linear / Raycast** — keyboard-native interactions, command palette as a serious primitive (Cmd-K for global search and navigation would be welcome).
- **Mixcloud's player** — but with a tracklist sidebar that's first-class, not an afterthought.

Push back hard on any of this if your design instincts go a different way. I'd rather end up somewhere unexpected than somewhere generic.

Start by asking me whatever you need, then show me 2–4 directions for the **set-detail / player view** in the visual companion.
