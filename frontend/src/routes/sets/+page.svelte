<script lang="ts">
  import SetCard from "$lib/components/SetCard.svelte";
  import FilterSidebar from "$lib/components/FilterSidebar.svelte";
  import type { PageData } from "./$types";

  export let data: PageData;

  $: tagOptions = Array.from(
    new Set(data.sets.flatMap((s) => s.tags)),
  ).sort();
  $: yearOptions = Array.from(
    new Set(
      data.sets
        .map((s) => (s.date ? Number.parseInt(s.date.slice(0, 4), 10) : null))
        .filter((y): y is number => y !== null && !Number.isNaN(y)),
    ),
  ).sort((a, b) => b - a);
</script>

<svelte:head><title>Library - SetVault</title></svelte:head>

<section>
  <h1>Library</h1>
  <div class="layout">
    <FilterSidebar tags={tagOptions} venueKinds={[]} years={yearOptions} />
    <div class="grid">
      {#each data.sets as s (s.slug)}<SetCard set={s} />{/each}
    </div>
  </div>
</section>

<style>
  section { padding: var(--sp-6); display: grid; gap: var(--sp-4); }
  .layout {
    display: grid;
    grid-template-columns: 240px 1fr;
    gap: var(--sp-4);
  }
  @media (max-width: 760px) {
    .layout { grid-template-columns: 1fr; }
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--sp-3);
  }
  @media (max-width: 600px) {
    section { padding: var(--sp-3); }
    .grid { grid-template-columns: 1fr; }
  }
</style>
