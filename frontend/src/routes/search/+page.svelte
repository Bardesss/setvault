<script lang="ts">
  import { page } from "$app/stores";

  type SearchResults = {
    sets: { slug: string; title: string }[];
    artists: { slug: string; name: string }[];
  };

  $: q = $page.url.searchParams.get("q") ?? "";
  $: resultsP = q
    ? fetch(`/api/search?q=${encodeURIComponent(q)}`).then(
        (r) => r.json() as Promise<SearchResults>,
      )
    : null;
</script>

<section>
  <h1>Search</h1>
  <form>
    <input name="q" type="search" placeholder="search sets, artists, parties, venues" value={q} />
    <button type="submit">Go</button>
  </form>
  {#if resultsP}
    {#await resultsP}
      <p>Searching…</p>
    {:then r}
      <h2>Sets</h2>
      <ul>{#each r.sets as s}<li><a href={`/sets/${s.slug}`}>{s.title}</a></li>{/each}</ul>
      <h2>Artists</h2>
      <ul>{#each r.artists as a}<li><a href={`/artists/${a.slug}`}>{a.name}</a></li>{/each}</ul>
    {/await}
  {/if}
</section>

<style>
  section { padding: var(--sp-6); display: grid; gap: var(--sp-3); }
  form { display: flex; gap: var(--sp-2); }
  input { flex: 1; padding: var(--sp-2); background: var(--bg-surface);
          border: 1px solid var(--border-default); border-radius: var(--r-md); color: inherit; }
</style>
