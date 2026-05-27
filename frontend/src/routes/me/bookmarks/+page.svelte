<script lang="ts">
  import { onMount } from "svelte";
  import { _ } from "svelte-i18n";
  import { listMyBookmarks, type Bookmark } from "$lib/api/bookmarks";

  let items: Bookmark[] = [];
  let loaded = false;

  onMount(async () => {
    try {
      items = await listMyBookmarks();
    } finally {
      loaded = true;
    }
  });

  function fmt(s: number): string {
    const m = Math.floor(s / 60);
    const ss = s % 60;
    return `${m}:${String(ss).padStart(2, "0")}`;
  }

  $: bySet = items.reduce<Record<string, Bookmark[]>>((acc, b) => {
    const key = b.live_set_slug ?? "(unknown)";
    (acc[key] ??= []).push(b);
    return acc;
  }, {});
</script>

<svelte:head><title>{$_("bookmarks.my_title")} - SetVault</title></svelte:head>

<section>
  <h1>{$_("bookmarks.my_title")}</h1>
  {#if loaded && items.length === 0}
    <p class="empty">{$_("bookmarks.empty")}</p>
  {/if}
  {#each Object.entries(bySet) as [slug, list] (slug)}
    <article>
      <h2><a href="/sets/{slug}">{list[0].live_set_title ?? slug}</a></h2>
      <ul>
        {#each list as b (b.id)}
          <li>
            <a href="/sets/{slug}{b.position_seconds !== null ? `?t=${b.position_seconds}` : ''}">
              {b.position_seconds === null ? $_("bookmarks.entire_set") : fmt(b.position_seconds)}
            </a>
            {#if b.label}<span class="label">{b.label}</span>{/if}
          </li>
        {/each}
      </ul>
    </article>
  {/each}
</section>

<style>
  section {
    padding: var(--sp-6);
    display: grid;
    gap: var(--sp-4);
    max-width: 800px;
    margin: 0 auto;
  }
  article { display: grid; gap: var(--sp-2); }
  h2 { margin: 0; font-size: var(--ts-lg); }
  ul { list-style: none; padding: 0; margin: 0; display: grid; gap: var(--sp-1); }
  .label { color: var(--text-muted); font-style: italic; margin-left: var(--sp-2); }
  .empty { color: var(--text-muted); font-style: italic; }
</style>
