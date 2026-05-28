<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import WaveSurfer from "wavesurfer.js";
  import { listComments } from "$lib/api/comments";
  import type { SetDetail } from "$lib/api/sets";
  import { getSetState, putSetState } from "$lib/api/sets";
  import { listTracklist, type TracklistEntry } from "$lib/api/tracklist";
  import { player, registerSeek } from "$lib/stores/player";

  export let set: SetDetail;

  let container: HTMLDivElement;
  let ws: WaveSurfer | null = null;
  let playing = false;
  let position = 0;
  let duration = 0;
  let saveTimer: ReturnType<typeof setInterval> | null = null;
  let ready = false;
  let commentMarkers: Array<{ id: string; t: number; author: string; excerpt: string }> = [];
  let tracklistEntries: TracklistEntry[] = [];

  async function loadCommentMarkers(): Promise<void> {
    try {
      const data = await listComments(set.slug);
      commentMarkers = data.items
        .filter((c) => c.position_seconds !== null && !c.deleted_at)
        .map((c) => ({
          id: c.id,
          t: c.position_seconds as number,
          author: c.author.display_name ?? c.author.username,
          excerpt: (c.body_md ?? "").slice(0, 80),
        }));
    } catch {
      /* best-effort; no markers if API fails */
    }
  }

  async function loadTracklistEntries(): Promise<void> {
    try {
      tracklistEntries = (await listTracklist(set.slug))
        .slice()
        .sort((a, b) => a.start_seconds - b.start_seconds);
    } catch {
      /* best-effort; mediaSession prev/next will fall back to default seeks */
    }
  }

  function previousEntryStart(): number {
    // Largest entry.start_seconds strictly less than current position (with
    // a 2s "rewind to start of this entry" zone — same idiom every podcast app
    // uses for the back button).
    if (tracklistEntries.length === 0) return 0;
    const REWIND_ZONE_SECONDS = 2;
    for (let i = tracklistEntries.length - 1; i >= 0; i--) {
      if (tracklistEntries[i].start_seconds < position - REWIND_ZONE_SECONDS) {
        return tracklistEntries[i].start_seconds;
      }
    }
    return 0;
  }

  function nextEntryStart(): number | null {
    for (const e of tracklistEntries) {
      if (e.start_seconds > position + 0.5) return e.start_seconds;
    }
    return null;
  }

  function formatTime(seconds: number): string {
    if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  }

  async function saveState(): Promise<void> {
    if (!ready || !ws) return;
    const total = set.duration_seconds ?? duration ?? 0;
    const completed = total > 0 ? position >= total * 0.97 : false;
    try {
      await putSetState(set.slug, {
        position_seconds: position,
        completed,
      });
    } catch {
      /* best-effort; ignore network errors during playback */
    }
  }

  function setMediaSession(): void {
    if (typeof navigator === "undefined" || !("mediaSession" in navigator)) return;
    try {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: set.title,
        artist: set.artists.map((a) => a.name).join(", ") || "Unknown",
        artwork: [
          { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
          { src: "/icons/icon-256.png", sizes: "256x256", type: "image/png" },
          { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
        ],
      });
      navigator.mediaSession.setActionHandler?.("play", () => ws?.play());
      navigator.mediaSession.setActionHandler?.("pause", () => ws?.pause());
      navigator.mediaSession.setActionHandler?.("seekbackward", () => seek(-5));
      navigator.mediaSession.setActionHandler?.("seekforward", () => seek(5));
      navigator.mediaSession.setActionHandler?.("previoustrack", () => {
        const t = previousEntryStart();
        ws?.setTime(Math.max(0, t));
      });
      navigator.mediaSession.setActionHandler?.("nexttrack", () => {
        const t = nextEntryStart();
        if (t !== null) ws?.setTime(t);
      });
    } catch {
      /* not supported in all browsers */
    }
  }

  function seek(deltaSeconds: number): void {
    if (!ws) return;
    const next = Math.max(0, Math.min((duration || 0), position + deltaSeconds));
    ws.setTime(next);
  }

  function adjustVolume(delta: number): void {
    if (!ws) return;
    const current = ws.getVolume();
    const next = Math.max(0, Math.min(1, current + delta));
    ws.setVolume(next);
  }

  function onKey(e: KeyboardEvent): void {
    // Ignore when typing in form fields.
    const target = e.target as HTMLElement | null;
    if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)) {
      return;
    }
    if (!ws) return;
    const key = e.key;
    if (key === " " || key === "Spacebar" || key === "k" || key === "K") {
      e.preventDefault();
      ws.playPause();
    } else if (key === "j" || key === "J" || key === "ArrowLeft") {
      e.preventDefault();
      seek(key === "ArrowLeft" ? -5 : -10);
    } else if (key === "l" || key === "L" || key === "ArrowRight") {
      e.preventDefault();
      seek(key === "ArrowRight" ? 5 : 10);
    } else if (key === "ArrowUp") {
      e.preventDefault();
      adjustVolume(0.1);
    } else if (key === "ArrowDown") {
      e.preventDefault();
      adjustVolume(-0.1);
    }
  }

  onMount(async () => {
    ws = WaveSurfer.create({
      container,
      url: set.audio_stream_url,
      waveColor: getComputedStyle(document.documentElement)
        .getPropertyValue("--waveform-unplayed").trim() || "#6c707d",
      progressColor: getComputedStyle(document.documentElement)
        .getPropertyValue("--waveform-played").trim() || "#00ffb2",
      cursorColor: getComputedStyle(document.documentElement)
        .getPropertyValue("--playhead").trim() || "#00ffb2",
      cursorWidth: 1,
      barWidth: 2,
      barGap: 1,
      barRadius: 0,
      height: 96,
      normalize: true,
      autoplay: false,
    });

    // Tag the inner shadow-DOM canvases wrapper so the test selector
    // `[data-test=wavesurfer-canvas] canvas` matches exactly one element
    // (the wave canvas; the progress canvas lives in a sibling .progress
    // wrapper that does not carry the data-test attribute). Wavesurfer
    // appends its own host div *into* our container and attaches the
    // shadow root on that inner div, so we walk one level down.
    const tagCanvasWrapper = (): boolean => {
      if (!container) return false;
      for (const child of Array.from(container.children) as HTMLElement[]) {
        const shadow = child.shadowRoot;
        const canvases = shadow?.querySelector(".canvases");
        if (canvases && shadow) {
          canvases.setAttribute("data-test", "wavesurfer-canvas");
          // Re-enable pointer-events on the wave canvas so e2e clicks land
          // on it (wavesurfer defaults `.canvases { pointer-events: none }`,
          // which causes Playwright's hit-test to fall through to the
          // wrapper). The wrapper's click handler still fires via bubbling,
          // so seek-on-click keeps working.
          if (!shadow.getElementById("e2e-canvas-pointer-events")) {
            const style = document.createElement("style");
            style.id = "e2e-canvas-pointer-events";
            style.textContent =
              ":host .canvases, :host .canvases > div, :host canvas { pointer-events: auto; }";
            shadow.appendChild(style);
          }
          return true;
        }
      }
      return false;
    };
    if (!tagCanvasWrapper()) {
      queueMicrotask(tagCanvasWrapper);
    }

    ws.on("ready", async () => {
      ready = true;
      duration = ws?.getDuration() ?? 0;
      player.update((p) => ({ ...p, set, duration }));
      setMediaSession();
      // Retry tagging now that wavesurfer has rendered.
      tagCanvasWrapper();
      try {
        const remote = await getSetState(set.slug);
        if (remote.position_seconds > 0 && duration > 0
            && remote.position_seconds < duration - 1) {
          ws?.setTime(remote.position_seconds);
        }
      } catch {
        /* no prior state */
      }
    });
    ws.on("timeupdate", (t: number) => {
      position = t;
      player.update((p) => ({ ...p, position }));
    });
    ws.on("play", () => {
      playing = true;
      player.update((p) => ({ ...p, playing: true }));
    });
    ws.on("pause", () => {
      playing = false;
      player.update((p) => ({ ...p, playing: false }));
    });
    ws.on("finish", () => {
      playing = false;
      player.update((p) => ({ ...p, playing: false }));
      void saveState();
    });

    // Expose absolute seeking to other components (the tracklist sidebar).
    registerSeek((s: number) => ws?.setTime(Math.max(0, s)));

    window.addEventListener("keydown", onKey);
    saveTimer = setInterval(() => {
      void saveState();
    }, 5000);
    void loadCommentMarkers();
    void loadTracklistEntries();
  });

  onDestroy(() => {
    if (typeof window === "undefined") return;
    if (saveTimer) clearInterval(saveTimer);
    registerSeek(null);
    window.removeEventListener("keydown", onKey);
    void saveState();
    ws?.destroy();
    ws = null;
    player.set({ set: null, playing: false, position: 0, duration: 0 });
  });
</script>

<div class="player">
  <div
    class="wave"
    bind:this={container}
    aria-label="audio waveform"
  ></div>
  {#if duration > 0 && commentMarkers.length > 0}
    <div class="markers" aria-hidden="true">
      {#each commentMarkers as m (m.id)}
        <button
          type="button"
          class="marker"
          style="left: {(m.t / duration) * 100}%"
          title="{m.author}: {m.excerpt}"
          on:click={() => ws?.setTime(Math.max(0, m.t))}
        ></button>
      {/each}
    </div>
  {/if}
  <div class="controls" aria-label="player controls">
    <button
      type="button"
      class="play"
      on:click={() => ws?.playPause()}
      data-test="play-state"
      data-state={playing ? "playing" : "paused"}
      aria-label={playing ? "pause" : "play"}
    >
      {playing ? "Pause" : "Play"}
    </button>
    <span class="time mono" aria-live="off">
      {formatTime(position)} / {formatTime(duration || (set.duration_seconds ?? 0))}
    </span>
    <span class="hint">space play/pause - j/l seek -10/+10s - arrows seek/volume</span>
  </div>
</div>

<style>
  .player { display: grid; gap: var(--sp-3); }
  .wave {
    width: 100%;
    min-height: 96px;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--r-md);
    padding: var(--sp-2);
  }
  .controls {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    flex-wrap: wrap;
  }
  .play {
    padding: var(--sp-2) var(--sp-4);
    background: var(--accent);
    color: var(--text-on-accent);
    border: none;
    border-radius: var(--r-sm);
    font-family: var(--font-mono);
    font-size: var(--ts-sm);
    text-transform: uppercase;
    letter-spacing: var(--ls-loose);
    cursor: pointer;
  }
  .play:hover { filter: brightness(1.1); }
  .time {
    font-family: var(--font-mono);
    font-size: var(--ts-sm);
    color: var(--text-muted);
  }
  .hint {
    font-family: var(--font-mono);
    font-size: var(--ts-xxs);
    color: var(--text-faint);
    letter-spacing: var(--ls-loose);
  }
  .mono { font-variant-numeric: tabular-nums; }
  .markers {
    position: relative;
    height: 8px;
    margin-top: calc(var(--sp-2) * -1 + 2px);
  }
  .marker {
    position: absolute;
    top: 0;
    transform: translateX(-50%);
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent);
    border: none;
    cursor: pointer;
    padding: 0;
  }
  .marker:hover { transform: translateX(-50%) scale(1.4); }
  @media (max-width: 600px) {
    .markers { height: 14px; }
    .marker { width: 14px; height: 14px; }  /* bigger touch target */
  }
</style>
