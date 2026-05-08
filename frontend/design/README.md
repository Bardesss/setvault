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

## How Phase 2 consumes this

The Phase 2 (Core vault) implementation plan should:

1. Copy `assets/tokens.css` into the SvelteKit app's `src/lib/styles/tokens.css`. Don't redefine tokens — import or `@import` this single source.
2. Copy `fonts/` into the SvelteKit app's `static/fonts/` and `assets/fonts.css` into `src/lib/styles/fonts.css`.
3. Each component pattern in `components.html` becomes one Svelte component with the same class names. The CSS in `assets/components.css` is the starting point — refactor into Svelte's scoped CSS pattern but keep the rendered classnames identical for visual continuity.
4. Each screen in `screens/*.html` becomes a SvelteKit route under `frontend/src/routes/`. The HTML structure in those files is the production target — substituting `{#each}` blocks for repeated rows, etc.
5. The landing page becomes a separate SvelteKit static-adapter build under `site/` per the spec.

## Reviewing this package

The design isn't precious. Push back hard on anything that feels wrong before Phase 2 starts:

- **Wrong mood?** We can swap palettes / type pairings while keeping the spatial grammar.
- **Wrong information density?** The tracklist row is the most dense thing — it can shed columns.
- **Wrong navigation?** The left rail can collapse to a top tab strip, or grow to a dual rail.
- **Wrong screen missing?** Artist / Party / Venue / Series detail isn't mocked in this batch (they reuse the library + hero patterns); say so if you want it explicit.
- **Wrong landing tone?** The landing currently leans technical-and-direct. Could swing more editorial/aspirational, or tighter/no-frills.

When the design is approved, we can move to writing the Phase 2 implementation plan.
