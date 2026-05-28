<script lang="ts">
  import { createEventDispatcher } from "svelte";

  export let query: string = "";
  export let sort: string = "recent";
  export let sortOptions: { value: string; label: string }[] = [
    { value: "recent", label: "Recently added" },
    { value: "title", label: "Title A→Z" },
    { value: "duration", label: "Duration" },
  ];
  export let view: "list" | "grid" = "list";

  const dispatch = createEventDispatcher<{
    query: string;
    sort: string;
    view: "list" | "grid";
  }>();

  function onInput(e: Event) {
    query = (e.target as HTMLInputElement).value;
    dispatch("query", query);
  }
  function onSort(e: Event) {
    sort = (e.target as HTMLSelectElement).value;
    dispatch("sort", sort);
  }
  function toggleView(next: "list" | "grid") {
    view = next;
    dispatch("view", view);
  }
</script>

<div class="filter-bar">
  <input
    type="search"
    bind:value={query}
    on:input={onInput}
    placeholder="Filter sets…"
    aria-label="Filter sets"
  />
  <select bind:value={sort} on:change={onSort} aria-label="Sort by">
    {#each sortOptions as opt (opt.value)}
      <option value={opt.value}>{opt.label}</option>
    {/each}
  </select>
  <div class="view-toggle" role="group" aria-label="View toggle">
    <button
      type="button"
      class:active={view === "list"}
      on:click={() => toggleView("list")}
      aria-pressed={view === "list"}
    >List</button>
    <button
      type="button"
      class:active={view === "grid"}
      on:click={() => toggleView("grid")}
      aria-pressed={view === "grid"}
    >Grid</button>
  </div>
  <slot name="extra" />
</div>
