<script lang="ts">
  import { _ } from "svelte-i18n";
  import type { RipJob } from "$lib/api/url_rip";
  export let job: RipJob;
  $: title = (job.probed_metadata?.title as string) ?? job.source_url;
</script>

<article class="rip-row" data-status={job.status}>
  <div class="title">{title}</div>
  <div class="meta">
    <span class="status">{$_(`url_rip.status.${job.status}`)}</span>
    {#if job.message}<span class="message">{job.message}</span>{/if}
  </div>
  <progress max="100" value={job.progress_pct}></progress>
  {#if job.status === "ready" && job.live_set_slug}
    <a href={`/sets/${job.live_set_slug}`}>{$_("url_rip.open_set")}</a>
  {/if}
  {#if job.status === "failed" && job.error_text}
    <p class="error">{job.error_text}</p>
  {/if}
</article>

<style>
  .rip-row {
    display: grid;
    gap: var(--sp-1);
    padding: var(--sp-2);
    border: 1px solid var(--border-default);
    border-radius: var(--r-sm);
  }
  .title { font-weight: 600; }
  .meta {
    display: flex;
    gap: var(--sp-2);
    font-size: var(--ts-sm);
    color: var(--text-faint);
  }
  progress { width: 100%; }
  .error { color: #c33; font-size: var(--ts-sm); }
</style>
