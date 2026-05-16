<script lang="ts">
  // Phase 2: no parsed tracks yet. Cue-point parsing + chapter markers land
  // in Phase 3 alongside fingerprint-driven track detection.
  import { _ } from "svelte-i18n";
</script>

<aside class="tracklist-empty" aria-label="tracklist">
  <h2>{$_("set_detail.tracklist")}</h2>
  <p>{$_("set_detail.tracklist_empty")}</p>
</aside>

<style>
  .tracklist-empty {
    padding: var(--sp-4);
    background: var(--bg-surface);
    border: 1px dashed var(--border-default);
    border-radius: var(--r-md);
    color: var(--text-muted);
  }
  .tracklist-empty h2 {
    margin: 0 0 var(--sp-2) 0;
    font-family: var(--font-mono);
    font-size: var(--ts-sm);
    text-transform: uppercase;
    letter-spacing: var(--ls-uppercase);
    color: var(--text-faint);
  }
  .tracklist-empty p {
    margin: 0;
    font-size: var(--ts-md);
  }
</style>
