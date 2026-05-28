<script lang="ts">
  import { _ } from "svelte-i18n";
  import type { PageData } from "./$types";

  export let data: PageData;
  $: set = data.set;

  function fmt(s: number | null): string {
    if (s === null) return "";
    const m = Math.floor(s / 60);
    const ss = Math.floor(s % 60);
    return `${m}:${String(ss).padStart(2, "0")}`;
  }
</script>

<svelte:head>
  <title>{set.title} - SetVault</title>
</svelte:head>

<div class="embed">
  <header>
    <h1>{set.title}</h1>
    <a href={`/sets/${set.slug}`} target="_blank" rel="noopener">
      {$_("embed.open_in_setvault")}
    </a>
  </header>

  <audio controls preload="metadata" src={set.audio_url}></audio>

  {#if set.tracklist.length > 0}
    <ol class="tracklist">
      {#each set.tracklist as t (t.position)}
        <li>
          <span class="ts">{fmt(t.start_seconds)}</span>
          {t.label ?? `Track ${t.position}`}
        </li>
      {/each}
    </ol>
  {/if}
</div>

<style>
  .embed {
    max-width: 720px;
    margin: 0 auto;
    padding: var(--sp-4);
    color: var(--text-default);
  }
  header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: var(--sp-2);
    margin-bottom: var(--sp-3);
  }
  h1 { margin: 0; font-size: var(--ts-lg); }
  header a { color: var(--accent); font-size: var(--ts-sm); }
  audio { width: 100%; }
  .tracklist {
    list-style: none;
    padding: 0;
    margin: var(--sp-3) 0;
    display: grid;
    gap: 4px;
    font-size: var(--ts-sm);
  }
  .ts {
    font-family: var(--font-mono);
    color: var(--text-faint);
    margin-right: var(--sp-2);
  }
</style>
