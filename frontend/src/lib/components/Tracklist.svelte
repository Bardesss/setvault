<script lang="ts">
  import { onMount } from "svelte";
  import { _ } from "svelte-i18n";
  import { bulkResolve } from "$lib/api/enrichment";
  import { createEntry, listTracklist, type TracklistEntry } from "$lib/api/tracklist";
  import { player, seekTo } from "$lib/stores/player";
  import { tracklist, setEntries, upsertEntry, removeEntry } from "$lib/stores/tracklist";
  import ResolveCandidatesPopover from "./ResolveCandidatesPopover.svelte";
  import TracklistEditDrawer from "./TracklistEditDrawer.svelte";
  import TracklistImportModal from "./TracklistImportModal.svelte";
  import TimeShiftDialog from "./TimeShiftDialog.svelte";

  export let slug: string;

  let drawerEntry: TracklistEntry | null = null;
  let importModalOpen = false;
  let shiftOpen = false;
  let popoverEntry: TracklistEntry | null = null;
  let bulkBusy = false;
  let bulkStatus: string | null = null;

  onMount(async () => {
    try {
      const entries = await listTracklist(slug);
      setEntries(entries);
    } catch (e) {
      console.error("load tracklist failed", e);
    }
  });

  async function addAtPlayhead() {
    const seconds = Math.floor($player.position ?? 0);
    const tentative: TracklistEntry = {
      id: `pending-${Date.now()}`,
      position: $tracklist.entries.length,
      start_seconds: seconds,
      end_seconds: null,
      raw_label: $_("tracklist.new_entry"),
      edit_notes: null,
      status: "raw",
      confidence: null,
      track_id: null,
      mashup_with: [],
    };
    upsertEntry(tentative);
    try {
      const created = await createEntry(slug, {
        start_seconds: seconds,
        raw_label: $_("tracklist.new_entry"),
      });
      removeEntry(tentative.id);
      upsertEntry(created);
      drawerEntry = created;
    } catch (e) {
      removeEntry(tentative.id);
      console.error("add failed", e);
    }
  }

  function fmtTime(s: number): string {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const ss = s % 60;
    return h > 0
      ? `${h}:${String(m).padStart(2, "0")}:${String(ss).padStart(2, "0")}`
      : `${m}:${String(ss).padStart(2, "0")}`;
  }

  function indexAtPlayhead(): number {
    const entries = $tracklist.entries;
    return entries.findIndex((e, i) => {
      const next = entries[i + 1];
      return (
        e.start_seconds <= $player.position &&
        (!next || next.start_seconds > $player.position)
      );
    });
  }

  function cycle(direction: 1 | -1) {
    const entries = $tracklist.entries;
    if (!entries.length) return;
    const current = indexAtPlayhead();
    const target =
      entries[Math.max(0, Math.min(entries.length - 1, current + direction))];
    if (target) seekTo(target.start_seconds);
  }

  function handleKeydown(ev: KeyboardEvent) {
    if (
      ev.target instanceof HTMLInputElement ||
      ev.target instanceof HTMLTextAreaElement
    )
      return;
    if (ev.key === "m" || ev.key === "M") {
      ev.preventDefault();
      addAtPlayhead();
    } else if (ev.key === "[") {
      cycle(-1);
    } else if (ev.key === "]") {
      cycle(1);
    }
  }

  async function runBulkResolve() {
    bulkBusy = true;
    bulkStatus = null;
    try {
      const results = await bulkResolve(slug);
      const withCands = results.filter((r) => r.candidates.length > 0).length;
      bulkStatus = $_("tracklist.bulk_resolve_done", {
        values: { found: withCands, total: results.length },
      });
    } catch (e) {
      bulkStatus = e instanceof Error ? e.message : "error";
    } finally {
      bulkBusy = false;
    }
  }

  $: currentIdx = indexAtPlayhead();
</script>

<svelte:window on:keydown={handleKeydown} />

<aside class="tracklist" aria-label={$_("tracklist.heading")}>
  <header>
    <h3>{$_("tracklist.heading")}</h3>
    <div class="actions">
      <button on:click={addAtPlayhead} title={$_("tracklist.add_at_playhead")}>+ M</button>
      <button on:click={() => (importModalOpen = true)}>{$_("tracklist.import")}</button>
      <button on:click={() => (shiftOpen = true)}>{$_("tracklist.time_shift")}</button>
      <button on:click={runBulkResolve} disabled={bulkBusy}>
        {$_("tracklist.bulk_resolve")}
      </button>
    </div>
  </header>

  {#if bulkStatus}<p class="bulk-status">{bulkStatus}</p>{/if}

  {#if $tracklist.entries.length === 0}
    <p class="empty">{$_("tracklist.empty")}</p>
  {:else}
    <ol>
      {#each $tracklist.entries as entry, idx (entry.id)}
        <li
          class:current={idx === currentIdx}
          class:status-raw={entry.status === "raw"}
          class:status-resolved={entry.status === "resolved"}
          class:status-acoustid={entry.status === "acoustid_confirmed"}
        >
          <button class="seek" on:click={() => seekTo(entry.start_seconds)}>
            <span class="t mono">{fmtTime(entry.start_seconds)}</span>
            <span class="label">{entry.raw_label}</span>
          </button>
          {#if entry.status === "raw"}
            <button class="resolve" on:click={() => (popoverEntry = entry)}>
              {$_("tracklist.resolve")}
            </button>
          {/if}
          <span class="badge" data-status={entry.status}>{entry.status}</span>
          <button
            class="edit"
            on:click={() => (drawerEntry = entry)}
            aria-label={$_("tracklist.edit_entry")}>✎</button
          >
        </li>
      {/each}
    </ol>
  {/if}
</aside>

{#if drawerEntry}
  <TracklistEditDrawer {slug} entry={drawerEntry} on:close={() => (drawerEntry = null)} />
{/if}

{#if importModalOpen}
  <TracklistImportModal {slug} on:close={() => (importModalOpen = false)} />
{/if}

{#if shiftOpen}
  <TimeShiftDialog {slug} on:close={() => (shiftOpen = false)} />
{/if}

{#if popoverEntry}
  <ResolveCandidatesPopover
    {slug}
    entry={popoverEntry}
    on:close={() => (popoverEntry = null)}
  />
{/if}

<style>
  .tracklist {
    border: 1px solid var(--border-default);
    border-radius: var(--r-md);
    padding: var(--sp-4);
    background: var(--bg-surface);
  }
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--sp-3);
  }
  h3 { margin: 0; font-size: var(--ts-lg); }
  .actions { display: flex; gap: var(--sp-2); }
  .actions button {
    background: none;
    border: 1px solid var(--border-default);
    border-radius: var(--r-sm);
    padding: var(--sp-1) var(--sp-2);
    color: var(--text-muted);
    cursor: pointer;
    font-family: var(--font-mono);
    font-size: var(--ts-xs);
  }
  .actions button:hover { color: var(--text-default); }
  ol { list-style: none; padding: 0; margin: 0; display: grid; gap: 2px; }
  li {
    display: grid;
    grid-template-columns: 1fr auto auto auto;
    gap: var(--sp-2);
    align-items: center;
    padding: var(--sp-2);
    border-radius: var(--r-sm);
  }
  li.current { background: var(--bg-now); }
  button.seek {
    display: flex;
    gap: var(--sp-2);
    align-items: baseline;
    min-width: 0;
    background: none;
    border: none;
    cursor: pointer;
    color: inherit;
    text-align: left;
    padding: 0;
  }
  .t { font-family: var(--font-mono); color: var(--text-muted); min-width: 5ch; }
  .label { color: var(--text-default); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .resolve {
    background: none;
    border: 1px solid var(--accent-warning);
    border-radius: var(--r-sm);
    padding: 2px var(--sp-2);
    color: var(--accent-warning);
    cursor: pointer;
    font-family: var(--font-mono);
    font-size: var(--ts-xs);
  }
  .bulk-status {
    margin: 0 0 var(--sp-2);
    color: var(--text-muted);
    font-size: var(--ts-sm);
  }
  .badge {
    font-family: var(--font-mono);
    font-size: var(--ts-xs);
    padding: 2px 6px;
    border: 1px solid var(--border-default);
    border-radius: var(--r-pill);
    color: var(--text-muted);
  }
  .badge[data-status="raw"] {
    color: var(--accent-warning);
    border-color: var(--accent-warning);
  }
  .badge[data-status="resolved"] { color: var(--accent); border-color: var(--accent); }
  .badge[data-status="acoustid_confirmed"] {
    color: var(--accent);
    border-color: var(--accent);
  }
  .edit { background: none; border: none; cursor: pointer; color: var(--text-muted); }
  .edit:hover { color: var(--text-default); }
  .empty { color: var(--text-muted); font-style: italic; }
</style>
