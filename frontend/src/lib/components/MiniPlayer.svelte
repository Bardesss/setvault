<script lang="ts">
  import { player } from "$lib/stores/player";

  function fmt(seconds: number): string {
    if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  }
</script>

{#if $player.set}
  <div class="mini" role="status" aria-label="now playing">
    <a class="title" href={`/sets/${$player.set.slug}`}>{$player.set.title}</a>
    <span class="state mono" data-state={$player.playing ? "playing" : "paused"}>
      {$player.playing ? "playing" : "paused"}
    </span>
    <span class="time mono">{fmt($player.position)} / {fmt($player.duration)}</span>
  </div>
{/if}

<style>
  .mini {
    position: fixed;
    left: 0; right: 0; bottom: 0;
    height: var(--shell-mini-player, 64px);
    background: var(--bg-elevated);
    border-top: 1px solid var(--border-default);
    display: flex;
    align-items: center;
    gap: var(--sp-4);
    padding: 0 var(--sp-6);
    z-index: var(--z-sticky);
  }
  .title {
    color: var(--text-default);
    font-weight: 600;
    text-decoration: none;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 40ch;
  }
  .title:hover { color: var(--accent); }
  .state {
    font-family: var(--font-mono);
    font-size: var(--ts-xs);
    text-transform: uppercase;
    letter-spacing: var(--ls-loose);
    color: var(--text-muted);
  }
  .state[data-state="playing"] { color: var(--accent); }
  .time {
    font-family: var(--font-mono);
    font-size: var(--ts-sm);
    color: var(--text-muted);
    margin-left: auto;
    font-variant-numeric: tabular-nums;
  }
</style>
