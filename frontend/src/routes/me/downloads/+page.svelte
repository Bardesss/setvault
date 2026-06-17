<script lang="ts">
  import { onDestroy, onMount } from "svelte";
  import { _ } from "svelte-i18n";
  import RipJobRow from "$lib/components/RipJobRow.svelte";
  import EmptyState from "$lib/components/EmptyState.svelte";
  import { listMyRipJobs, hasActiveRips, type RipJob } from "$lib/api/url_rip";

  let jobs: RipJob[] = [];
  let loaded = false;
  let pollTimer: ReturnType<typeof setInterval> | null = null;

  async function refresh() {
    try {
      jobs = await listMyRipJobs("all");
    } catch {
      /* best-effort: keep the last good list on a transient error */
    } finally {
      loaded = true;
    }
  }

  onMount(async () => {
    await refresh();
    // Poll while anything is still in flight so progress updates live; idle
    // once every job has reached a terminal state.
    pollTimer = setInterval(() => {
      if (hasActiveRips(jobs)) void refresh();
    }, 4000);
  });

  onDestroy(() => {
    if (pollTimer) clearInterval(pollTimer);
  });

  function onRetried(fresh: RipJob) {
    jobs = [fresh, ...jobs];
  }
</script>

<svelte:head><title>{$_("downloads.title")} — SetVault</title></svelte:head>

<h2>{$_("downloads.title")}</h2>

{#if loaded && jobs.length === 0}
  <EmptyState message={$_("downloads.empty")} />
{:else}
  <ul class="downloads-list">
    {#each jobs as job (job.id)}
      <li><RipJobRow {job} on:retried={(e) => onRetried(e.detail)} /></li>
    {/each}
  </ul>
{/if}

<style>
  .downloads-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    gap: var(--sp-2);
  }
</style>
