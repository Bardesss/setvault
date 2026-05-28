<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import FilterBar from "$lib/components/FilterBar.svelte";

  type SearchResults = {
    sets: { slug: string; title: string }[];
    artists: { slug: string; name: string }[];
  };

  let query = "";
  let loading = false;
  let results: SearchResults | null = null;
  let initialized = false;

  onMount(() => {
    const q = $page.url.searchParams.get("q") ?? "";
    query = q;
    initialized = true;
    if (q) runSearch(q);
  });

  let timer: ReturnType<typeof setTimeout> | null = null;
  function onQueryEvent(e: CustomEvent<string>) {
    const next = e.detail;
    query = next;
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => runSearch(next), 200);
  }

  async function runSearch(q: string) {
    goto(`/search?q=${encodeURIComponent(q)}`, {
      keepFocus: true,
      noScroll: true,
      replaceState: true,
    });
    if (!q) {
      results = null;
      return;
    }
    loading = true;
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`, {
        credentials: "include",
      });
      if (!res.ok) {
        results = null;
        return;
      }
      results = (await res.json()) as SearchResults;
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head><title>Search — SetVault</title></svelte:head>

<FilterBar
  bind:query
  on:query={onQueryEvent}
  sortOptions={[{ value: "relevance", label: "Relevance" }]}
  sort="relevance"
  view="list"
/>

<section class="search-body">
  {#if !initialized}
    <p class="hint">Loading…</p>
  {:else if !query}
    <p class="hint">Type to search artists, sets, parties…</p>
  {:else if loading}
    <p class="hint">Searching…</p>
  {:else if !results || (results.sets.length === 0 && results.artists.length === 0)}
    <p class="hint">No matches for "{query}".</p>
  {:else}
    {#if results.sets.length}
      <h2 class="group">Sets</h2>
      <ul class="result-list">
        {#each results.sets as s (s.slug)}
          <li><a href={`/sets/${s.slug}`}>{s.title}</a></li>
        {/each}
      </ul>
    {/if}
    {#if results.artists.length}
      <h2 class="group">Artists</h2>
      <ul class="result-list">
        {#each results.artists as a (a.slug)}
          <li><a href={`/artists/${a.slug}`}>{a.name}</a></li>
        {/each}
      </ul>
    {/if}
  {/if}
</section>

<style>
  .search-body { padding: var(--sp-4) var(--sp-8) var(--sp-8); }
  .hint {
    padding: var(--sp-8);
    text-align: center;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: var(--ts-md);
  }
  .group {
    font-size: var(--ts-md);
    font-family: var(--font-mono);
    text-transform: uppercase;
    letter-spacing: var(--ls-uppercase);
    color: var(--text-faint);
    margin: var(--sp-5) 0 var(--sp-2);
  }
  .group:first-of-type { margin-top: 0; }
  .result-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    gap: var(--sp-2);
  }
  .result-list a {
    color: var(--text-default);
    text-decoration: none;
    padding: var(--sp-2) var(--sp-3);
    border-radius: var(--r-sm);
    display: block;
  }
  .result-list a:hover { background: var(--bg-surface); color: var(--accent); }
</style>
