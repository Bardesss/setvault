# SetVault — Phase 1 design package

This is the output of **Phase 1 — Design & visual identity** from the system spec at `docs/superpowers/specs/2026-05-08-setvault-design.md` (§9).

The chosen direction is **C — Underground Terminal**: phosphor-mint accents on a deep blue-black, Bricolage Grotesque + JetBrains Mono, dense modular layouts, keyboard-native interactions. Decided in conversation; alternates A/B/D were rejected.

## How to preview

Open `index.html` in any browser, or:

```
npx serve frontend/design
```

The index page lists every mockup with live previews. Each screen is a complete, standalone HTML file and works offline (no CDN dependencies, all fonts self-hosted).

## What's in here

```
frontend/design/
├── index.html              ← live preview entry point — start here
├── components.html         ← component library reference
├── landing.html            ← marketing site mockup (target: GitHub Pages)
│
├── screens/
│   ├── 01-set-detail.html       ← marquee: player + tracklist + side panel
│   ├── 02-library.html          ← filterable browse view
│   ├── 03-home.html             ← greeting, continue-listening, activity, jobs
│   ├── 04-tracklist-editor.html ← three input modes, inline edit, time-shift
│   └── 05-mobile-player.html    ← mobile / PWA / lockscreen
│
├── assets/
│   ├── tokens.css         ← all CSS variables (color, type, spacing, etc.)
│   ├── fonts.css          ← @font-face declarations (self-hosted)
│   ├── base.css           ← resets, base typography
│   └── components.css     ← shared component patterns
│
├── fonts/                  ← self-hosted woff2 (~170 KB total)
│   ├── BricolageGrotesque-{400,500,600,700,800}.woff2
│   └── JetBrainsMono-Variable.woff2
│
└── README.md               ← this file
```

## Design language summary

**Mood:** club-rooted, deliberate, slightly underground. Not generic-streaming-app-dark. Closer to Resident Advisor / Linear / a Pioneer CDJ than to a SaaS dashboard.

**Type pairing**
- **Bricolage Grotesque** for display + body (geometric grotesque, distinctive, optical-size aware)
- **JetBrains Mono** for technical data (timestamps, BPM, key, IDs) with `tnum` enabled

**Color**
- Dark (default): `#08090c` base → phosphor mint `#00ffb2` accent
- Light (alt): warm-paper `#ebeae3` base → deeper mint `#007a55` accent
- Light is *not* a trivial inversion — different mood, different feel

**Spacing & radius**
- 4 px base unit (`--sp-1 ... --sp-24`)
- 6 px default radius (`--r-md`); occasional pill radius for filter tags

**Motion**
- 100 / 180 / 320 ms · `cubic-bezier(0.2, 0.8, 0.2, 1)` default ease
- `prefers-reduced-motion` honored: durations collapse to 1 ms

**Texture**
- Subtle scanline overlay (`linear-gradient` 1 px / 3 px) reinforces the terminal feel
- Phosphor accent glow on focused / active elements (`var(--accent-glow)`)

## Offline-first notes

Per spec §12:
- All fonts are self-hosted (`fonts/*.woff2`, `assets/fonts.css`). No `https://fonts.googleapis.com`.
- All icons are inline SVG. No icon-font CDN.
- No external script tags.
- The whole `frontend/design/` folder runs offline from `file://` or a local static server.

## How this design package is consumed

**Phase 2 (Core vault, shipped)** consumed only the **foundation** layer:
1. `assets/tokens.css` → `frontend/src/lib/styles/tokens.css` (single source of CSS variables; imported by every app route via `+layout.svelte`).
2. `fonts/` → `frontend/static/fonts/` and `assets/fonts.css` → `frontend/src/lib/styles/fonts.css`.
3. `assets/base.css` and `assets/components.css` copied identically.

The Phase 2 app screens were built using these tokens but with simplified layouts — enough to be functional, not visually faithful to the screen mockups.

**Phase 6 (Mockup Parity)** consumes the **screen layout** layer:
1. Each screen in `screens/*.html` becomes the visual target for the corresponding SvelteKit route. HTML structure in those files is the production target — substituting `{#each}` blocks for repeated rows, etc.
2. Patterns in `components.html` become Svelte components (or additions to `components.css`) with rendered classnames preserved for visual continuity.
3. `landing.html` is ported into `site/index.html` as a plain static HTML page (no SvelteKit static-adapter — the original spec direction was relaxed because a one-page marketing site doesn't warrant a build step). Shared `tokens.css` / `fonts.css` / `base.css` / `components.css` reach the landing via a deploy-time copy step in `pages.yml`. See `docs/superpowers/specs/2026-05-28-phase-6-mockup-parity-design.md` for the full plan.

The contract from Phase 2 — "rendered classnames stay identical for visual continuity" — still holds. Phase 6 extracts more patterns into `components.css` so the static landing can share them with the app.

## Reviewing this package

The design isn't precious. Push back hard on anything that feels wrong before Phase 2 starts:

- **Wrong mood?** We can swap palettes / type pairings while keeping the spatial grammar.
- **Wrong information density?** The tracklist row is the most dense thing — it can shed columns.
- **Wrong navigation?** The left rail can collapse to a top tab strip, or grow to a dual rail.
- **Wrong screen missing?** Artist / Party / Venue / Series detail isn't mocked in this batch (they reuse the library + hero patterns); say so if you want it explicit.
- **Wrong landing tone?** The landing currently leans technical-and-direct. Could swing more editorial/aspirational, or tighter/no-frills.

When the design is approved, we can move to writing the Phase 2 implementation plan.
