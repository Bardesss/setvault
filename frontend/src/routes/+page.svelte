<script lang="ts">
  import SetCard from "$lib/components/SetCard.svelte";
  import type { PageData } from "./$types";

  export let data: PageData;
</script>

{#if !data.user}
  <section class="hero">
    <h1>SetVault</h1>
    <p><a href="/login">Sign in</a> to access the library.</p>
  </section>
{:else}
  {#if data.continueListening.length}
    <section>
      <h2>Continue listening</h2>
      <div class="grid">
        {#each data.continueListening as item (item.slug)}
          <a class="continue-card" href={`/sets/${item.slug}`}>
            <div class="ttl">{item.title}</div>
            <div class="progress">
              {Math.floor(item.position_seconds)}s / {item.duration_seconds ?? "?"}s
            </div>
          </a>
        {/each}
      </div>
    </section>
  {/if}
  <section>
    <h2>Recently added</h2>
    <div class="grid">
      {#each data.recent as s (s.slug)}<SetCard set={s} />{/each}
    </div>
  </section>
{/if}

<style>
  section { padding: var(--sp-6); }
  .hero { padding: var(--sp-8) var(--sp-6); display: grid; gap: var(--sp-3); }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: var(--sp-3);
  }
  .continue-card {
    display: grid;
    gap: var(--sp-1);
    padding: var(--sp-3);
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--r-md);
    text-decoration: none;
    color: inherit;
  }
  .ttl { font-weight: 700; }
  .progress {
    font-family: var(--font-mono);
    font-size: var(--ts-sm);
    color: var(--text-faint);
  }
  @media (max-width: 600px) {
    section { padding: var(--sp-3); }
    .hero { padding: var(--sp-6) var(--sp-3); }
    /* Continue-listening becomes a horizontal scroll strip */
    section:first-of-type .grid {
      display: flex;
      flex-direction: row;
      overflow-x: auto;
      scroll-snap-type: x mandatory;
      gap: var(--sp-2);
      padding-bottom: var(--sp-2);
      -webkit-overflow-scrolling: touch;
    }
    section:first-of-type .grid > * {
      flex: 0 0 80%;
      scroll-snap-align: start;
    }
    /* Recently-added stays in a grid but collapses to one column */
    .grid { grid-template-columns: 1fr; }
  }
</style>
