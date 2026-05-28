<script lang="ts">
  import { onMount } from "svelte";
  import { api, ApiError } from "$lib/api/client";

  interface WatchFolder {
    id: string;
    name: string;
    host_path: string;
    target_media_root_id: string;
    enabled: boolean;
    last_event_at: string | null;
    last_health_check_at: string | null;
    last_health_status: string;
    created_at: string;
  }

  interface MediaRoot {
    id: string;
    name: string;
  }

  let items: WatchFolder[] = [];
  let roots: MediaRoot[] = [];
  let loading = true;
  let error: string | null = null;
  let busy: Record<string, boolean> = {};

  let creating = false;
  let draft = newDraft();

  function newDraft() {
    return {
      name: "",
      host_path: "",
      target_media_root_id: "",
      enabled: true,
    };
  }

  async function load() {
    loading = true;
    try {
      const [list, mrList] = await Promise.all([
        api<{ items: WatchFolder[] }>("/api/admin/watch-folders"),
        api<{ items: MediaRoot[] }>("/api/media-roots"),
      ]);
      items = list.items;
      roots = mrList.items;
      if (!draft.target_media_root_id && roots[0]) {
        draft.target_media_root_id = roots[0].id;
      }
    } catch (e) {
      error = e instanceof ApiError ? e.detail : "load failed";
    } finally {
      loading = false;
    }
  }

  async function save() {
    error = null;
    try {
      await api("/api/admin/watch-folders", {
        method: "POST",
        body: JSON.stringify(draft),
      });
      creating = false;
      draft = newDraft();
      await load();
    } catch (e) {
      error = e instanceof ApiError ? e.detail : "save failed";
    }
  }

  async function toggle(wf: WatchFolder) {
    busy[wf.id] = true;
    busy = busy;
    try {
      await api(`/api/admin/watch-folders/${wf.id}`, {
        method: "PATCH",
        body: JSON.stringify({ enabled: !wf.enabled }),
      });
      await load();
    } catch (e) {
      error = e instanceof ApiError ? e.detail : "toggle failed";
    } finally {
      busy[wf.id] = false;
      busy = busy;
    }
  }

  async function healthCheck(wf: WatchFolder) {
    busy[wf.id] = true;
    busy = busy;
    try {
      await api(`/api/admin/watch-folders/${wf.id}/health-check`, {
        method: "POST",
      });
      await load();
    } catch (e) {
      error = e instanceof ApiError ? e.detail : "health-check failed";
    } finally {
      busy[wf.id] = false;
      busy = busy;
    }
  }

  async function remove(wf: WatchFolder) {
    if (!confirm(`Delete watch folder "${wf.name}"?`)) return;
    busy[wf.id] = true;
    busy = busy;
    try {
      await api(`/api/admin/watch-folders/${wf.id}`, { method: "DELETE" });
      items = items.filter((i) => i.id !== wf.id);
    } catch (e) {
      error = e instanceof ApiError ? e.detail : "delete failed";
    } finally {
      busy[wf.id] = false;
      busy = busy;
    }
  }

  function rootName(id: string): string {
    return roots.find((r) => r.id === id)?.name ?? id.slice(0, 8);
  }

  function fmtDate(iso: string | null): string {
    if (!iso) return "—";
    return iso.slice(0, 16).replace("T", " ");
  }

  onMount(load);
</script>

<section class="watch-folders">
  <header>
    <h2>Watch folders</h2>
    <p class="muted">
      Filesystem paths the watcher subscribes to. New audio files appearing
      in a watched folder enter the ingest pipeline automatically (filename
      patterns become drafts; ambiguous files land in the Unmatched inbox).
    </p>
  </header>

  {#if error}<p class="error" role="alert">{error}</p>{/if}

  <button
    type="button"
    class="add"
    on:click={() => { draft = newDraft(); if (roots[0]) draft.target_media_root_id = roots[0].id; creating = true; }}
  >+ New watch folder</button>

  {#if creating}
    <form class="card" on:submit|preventDefault={save}>
      <label>
        Name
        <input type="text" bind:value={draft.name} required />
      </label>
      <label>
        Host path
        <input type="text" bind:value={draft.host_path} required placeholder="/srv/watch/incoming" />
      </label>
      <label>
        Target media root
        <select bind:value={draft.target_media_root_id} required>
          {#each roots as r (r.id)}
            <option value={r.id}>{r.name}</option>
          {/each}
        </select>
      </label>
      <div class="form-actions">
        <button type="submit" class="primary">Save</button>
        <button type="button" on:click={() => { creating = false; }}>Cancel</button>
      </div>
    </form>
  {/if}

  {#if loading}
    <p>Loading…</p>
  {:else if items.length === 0}
    <p class="empty">No watch folders configured yet.</p>
  {:else}
    <table>
      <thead><tr>
        <th>Name</th><th>Host path</th><th>Target root</th><th>Enabled</th>
        <th>Health</th><th>Last event</th><th>Actions</th>
      </tr></thead>
      <tbody>
        {#each items as wf (wf.id)}
          <tr class:disabled={!wf.enabled}>
            <td>{wf.name}</td>
            <td class="mono">{wf.host_path}</td>
            <td>{rootName(wf.target_media_root_id)}</td>
            <td>{wf.enabled ? "✓" : "—"}</td>
            <td class="mono">{wf.last_health_status}</td>
            <td class="mono">{fmtDate(wf.last_event_at)}</td>
            <td class="actions">
              <button type="button" disabled={busy[wf.id]} on:click={() => healthCheck(wf)}>Probe</button>
              <button type="button" disabled={busy[wf.id]} on:click={() => toggle(wf)}>
                {wf.enabled ? "Disable" : "Enable"}
              </button>
              <button type="button" class="danger" disabled={busy[wf.id]} on:click={() => remove(wf)}>Delete</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</section>

<style>
  .watch-folders { display: grid; gap: var(--sp-3); }
  header { display: grid; gap: var(--sp-1); }
  .muted { color: var(--text-faint); font-size: var(--ts-sm); margin: 0; }
  .error { color: #c33; }
  .empty { color: var(--text-faint); font-style: italic; }
  .add {
    justify-self: start;
    padding: var(--sp-1) var(--sp-2);
    border: 1px dashed var(--border-default);
    background: transparent;
    color: inherit;
    border-radius: var(--r-sm);
    cursor: pointer;
  }
  .card {
    padding: var(--sp-3);
    border: 1px solid var(--border-default);
    border-radius: var(--r-md);
    background: var(--bg-surface);
    display: grid;
    gap: var(--sp-2);
  }
  .card label { display: grid; gap: var(--sp-1); font-size: var(--ts-sm); }
  .card input, .card select {
    padding: var(--sp-1);
    background: var(--bg-base);
    border: 1px solid var(--border-default);
    border-radius: var(--r-sm);
    color: inherit;
    font: inherit;
  }
  .form-actions { display: flex; gap: var(--sp-2); }
  .primary { background: var(--accent); color: var(--text-on-accent, var(--bg-base)); border: 0; }
  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: var(--sp-1) var(--sp-2);
           border-bottom: 1px solid var(--border-default); }
  th { color: var(--text-faint); font-weight: 600; font-size: var(--ts-sm); }
  .mono { font-family: var(--font-mono); font-size: var(--ts-sm); }
  .disabled td { opacity: 0.5; }
  .actions { display: flex; gap: var(--sp-1); }
  .actions button {
    padding: var(--sp-1) var(--sp-2);
    border: 1px solid var(--border-default);
    background: transparent;
    color: inherit;
    border-radius: var(--r-sm);
    cursor: pointer;
  }
  .actions button:disabled { opacity: 0.5; cursor: not-allowed; }
  .actions button.danger { border-color: #c33; color: #c33; }
</style>
