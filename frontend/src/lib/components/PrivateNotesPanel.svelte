<script lang="ts">
  import { onMount } from "svelte";
  import { _ } from "svelte-i18n";
  import { getNote, saveNote, type PrivateNote } from "$lib/api/notes";

  export let slug: string;

  let collapsed = true;
  let note: PrivateNote = { body_md: "", body_html: "", updated_at: null };
  let dirty = false;
  let saveTimer: ReturnType<typeof setTimeout> | null = null;
  let editing = false;

  onMount(async () => {
    try {
      note = await getNote(slug);
    } catch {
      /* best-effort */
    }
  });

  function onInput(e: Event) {
    note.body_md = (e.target as HTMLTextAreaElement).value;
    dirty = true;
    if (saveTimer) clearTimeout(saveTimer);
    saveTimer = setTimeout(async () => {
      try {
        const out = await saveNote(slug, note.body_md);
        note = out;
        dirty = false;
      } catch {
        /* keep dirty=true so user sees it didn't save */
      }
    }, 1000);
  }
</script>

<section class="notes">
  <header>
    <button on:click={() => (collapsed = !collapsed)} aria-expanded={!collapsed}>
      {collapsed ? "▶" : "▼"} {$_("notes.heading")}
    </button>
    {#if dirty}<span class="status">{$_("notes.saving")}</span>{/if}
  </header>
  {#if !collapsed}
    <div class="body">
      {#if editing}
        <textarea
          bind:value={note.body_md}
          on:input={onInput}
          rows="8"
          placeholder={$_("notes.placeholder")}
          aria-label={$_("notes.heading")}
        ></textarea>
        <button class="done" on:click={() => (editing = false)}>{$_("notes.done")}</button>
      {:else}
        <button class="preview-toggle" on:click={() => (editing = true)}>{$_("notes.edit")}</button>
        {#if note.body_md}
          {@html note.body_html}
        {:else}
          <p class="empty">{$_("notes.empty")}</p>
        {/if}
      {/if}
    </div>
  {/if}
</section>

<style>
  .notes {
    padding: var(--sp-4);
    border: 1px solid var(--border-default);
    border-radius: var(--r-md);
  }
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  header button {
    background: none;
    border: none;
    color: var(--text-default);
    cursor: pointer;
    font: inherit;
    text-align: left;
  }
  .body {
    margin-top: var(--sp-3);
    display: grid;
    gap: var(--sp-2);
  }
  textarea {
    width: 100%;
    box-sizing: border-box;
    padding: var(--sp-2);
    font: inherit;
    background: var(--surface-0);
    border: 1px solid var(--border-default);
    border-radius: var(--r-sm);
    color: var(--text-default);
    resize: vertical;
  }
  .done,
  .preview-toggle {
    justify-self: start;
    padding: var(--sp-1) var(--sp-3);
    border: 1px solid var(--border-default);
    border-radius: var(--r-sm);
    background: var(--surface-1);
    color: var(--text-default);
    cursor: pointer;
    font: inherit;
  }
  .status {
    color: var(--text-muted);
    font-size: var(--ts-sm);
  }
  .empty {
    color: var(--text-faint);
    font-style: italic;
  }
</style>
