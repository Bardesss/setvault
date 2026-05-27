<script lang="ts">
  import Player from "$lib/components/Player.svelte";
  import Tracklist from "$lib/components/Tracklist.svelte";
  import CommentThread from "$lib/components/CommentThread.svelte";
  import BookmarkButton from "$lib/components/BookmarkButton.svelte";
  import PrivateNotesPanel from "$lib/components/PrivateNotesPanel.svelte";
  import type { PageData } from "./$types";

  export let data: PageData;

  $: set = data.set;
  $: artistNames = set.artists.map((a) => a.name).join(", ") || "Unknown artist";
</script>

<svelte:head><title>{set.title} - SetVault</title></svelte:head>

<section class="detail">
  <header class="hero">
    <p class="kicker mono">live set</p>
    <h1>{set.title}</h1>
    <p class="meta">
      <span>{artistNames}</span>
      {#if set.date}<span> - {set.date}</span>{/if}
      {#if set.venue}<span> - {set.venue.name}</span>{/if}
    </p>
    {#if set.tags.length > 0}
      <ul class="tags" aria-label="tags">
        {#each set.tags as tag (tag)}
          <li>{tag}</li>
        {/each}
      </ul>
    {/if}
  </header>

  <BookmarkButton slug={set.slug} />

  <Player {set} />

  {#if set.description}
    <section class="description">
      <h2>About</h2>
      <p>{set.description}</p>
    </section>
  {/if}

  <Tracklist slug={set.slug} />

  <PrivateNotesPanel slug={set.slug} />

  <CommentThread slug={set.slug} />
</section>

<style>
  .detail {
    padding: var(--sp-8) var(--sp-6) calc(var(--shell-mini-player, 64px) + var(--sp-8));
    display: grid;
    gap: var(--sp-6);
    max-width: 1100px;
    margin: 0 auto;
  }
  .hero { display: grid; gap: var(--sp-2); }
  .kicker {
    font-family: var(--font-mono);
    font-size: var(--ts-xs);
    text-transform: uppercase;
    letter-spacing: var(--ls-uppercase);
    color: var(--text-faint);
    margin: 0;
  }
  h1 {
    margin: 0;
    font-size: var(--ts-3xl);
    letter-spacing: var(--ls-tight);
    line-height: var(--lh-tight);
  }
  .meta {
    color: var(--text-muted);
    margin: 0;
  }
  .tags {
    list-style: none;
    padding: 0;
    margin: var(--sp-2) 0 0 0;
    display: flex;
    gap: var(--sp-2);
    flex-wrap: wrap;
  }
  .tags li {
    padding: 2px var(--sp-2);
    border: 1px solid var(--border-default);
    border-radius: var(--r-pill);
    font-family: var(--font-mono);
    font-size: var(--ts-xs);
    color: var(--text-muted);
  }
  .description h2 {
    margin: 0 0 var(--sp-2) 0;
    font-size: var(--ts-xl);
  }
  .description p {
    margin: 0;
    color: var(--text-default);
    line-height: var(--lh-relaxed);
  }
  .mono { font-family: var(--font-mono); }
</style>
