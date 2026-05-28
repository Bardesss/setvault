<script lang="ts">
  import { onMount } from "svelte";
  import { api, ApiError } from "$lib/api/client";

  interface Webhook {
    id: string;
    name: string;
    target_url: string;
    events: string[];
    body_template: Record<string, unknown> | null;
    headers: Record<string, string>;
    enabled: boolean;
    last_call_at: string | null;
    last_status_code: number | null;
    last_error: string | null;
  }

  const KNOWN_EVENTS = ["set.published", "set.updated", "set.deleted", "set.purged"];

  const RECIPES: { label: string; preset: Partial<Webhook> }[] = [
    {
      label: "Plex library refresh",
      preset: {
        name: "Plex refresh",
        target_url: "http://plex.local:32400/library/sections/1/refresh?X-Plex-Token=YOUR_TOKEN",
        events: ["set.published", "set.purged"],
        body_template: null,
      },
    },
    {
      label: "Jellyfin library refresh",
      preset: {
        name: "Jellyfin refresh",
        target_url: "http://jellyfin.local:8096/Library/Refresh",
        events: ["set.published", "set.purged"],
        body_template: null,
      },
    },
    {
      label: "Generic JSON POST",
      preset: {
        name: "Generic",
        target_url: "https://example.com/setvault-hook",
        events: ["set.published"],
        body_template: {
          event: "{{event}}",
          slug: "{{slug}}",
          title: "{{title}}",
        },
      },
    },
  ];

  // Placeholder string kept in JS to avoid Svelte parsing `{{event}}` as a
  // template expression.
  const BODY_PLACEHOLDER =
    "{\n  \"event\": \"{{event}}\",\n  \"slug\": \"{{slug}}\",\n  \"title\": \"{{title}}\"\n}";

  let items: Webhook[] = [];
  let loading = true;
  let error: string | null = null;
  let busy: Record<string, boolean> = {};

  let creating = false;
  let draft = newDraft();

  function newDraft(): Partial<Webhook> {
    return {
      name: "",
      target_url: "",
      events: [],
      body_template: null,
      headers: {},
      enabled: true,
    };
  }

  async function load() {
    loading = true;
    try {
      const r = await api<{ items: Webhook[] }>("/api/admin/webhooks");
      items = r.items;
    } catch (e) {
      error = e instanceof ApiError ? e.detail : "load failed";
    } finally {
      loading = false;
    }
  }

  async function save() {
    error = null;
    try {
      await api("/api/admin/webhooks", {
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

  async function toggleEnabled(wh: Webhook) {
    busy[wh.id] = true;
    busy = busy;
    try {
      await api(`/api/admin/webhooks/${wh.id}`, {
        method: "PATCH",
        body: JSON.stringify({ enabled: !wh.enabled }),
      });
      await load();
    } catch (e) {
      error = e instanceof ApiError ? e.detail : "toggle failed";
    } finally {
      busy[wh.id] = false;
      busy = busy;
    }
  }

  async function remove(wh: Webhook) {
    if (!confirm(`Delete webhook "${wh.name}"?`)) return;
    busy[wh.id] = true;
    busy = busy;
    try {
      await api(`/api/admin/webhooks/${wh.id}`, { method: "DELETE" });
      items = items.filter((i) => i.id !== wh.id);
    } catch (e) {
      error = e instanceof ApiError ? e.detail : "delete failed";
    } finally {
      busy[wh.id] = false;
      busy = busy;
    }
  }

  async function test(wh: Webhook) {
    busy[wh.id] = true;
    busy = busy;
    try {
      await api(`/api/admin/webhooks/${wh.id}/test`, { method: "POST" });
    } catch (e) {
      error = e instanceof ApiError ? e.detail : "test failed";
    } finally {
      busy[wh.id] = false;
      busy = busy;
    }
  }

  function applyRecipe(preset: Partial<Webhook>) {
    draft = { ...newDraft(), ...preset };
    creating = true;
  }

  function fmtDate(iso: string | null): string {
    if (!iso) return "—";
    return iso.slice(0, 16).replace("T", " ");
  }

  function toggleEvent(ev: string) {
    const events = draft.events ?? [];
    draft = {
      ...draft,
      events: events.includes(ev) ? events.filter((e) => e !== ev) : [...events, ev],
    };
  }

  function onBodyTemplateInput(ev: Event) {
    const raw = (ev.target as HTMLTextAreaElement).value;
    try {
      draft = { ...draft, body_template: raw ? JSON.parse(raw) : null };
    } catch {
      // keep typing; validated on save
    }
  }

  onMount(load);
</script>

<section class="webhooks">
  <header>
    <h2>Library refresh webhooks</h2>
    <p class="muted">
      Fires an HTTP POST to a configured URL whenever a matching audit event
      occurs (set publish / purge etc.). Plex / Jellyfin / Emby use this to
      refresh their library after SetVault publishes new content.
    </p>
  </header>

  {#if error}<p class="error" role="alert">{error}</p>{/if}

  <div class="recipes">
    {#each RECIPES as recipe (recipe.label)}
      <button type="button" on:click={() => applyRecipe(recipe.preset)}>
        + {recipe.label}
      </button>
    {/each}
    <button type="button" on:click={() => { draft = newDraft(); creating = true; }}>
      + Empty
    </button>
  </div>

  {#if creating}
    <form class="card" on:submit|preventDefault={save}>
      <label>
        Name
        <input type="text" bind:value={draft.name} required />
      </label>
      <label>
        Target URL
        <input type="url" bind:value={draft.target_url} required />
      </label>
      <fieldset>
        <legend>Events</legend>
        {#each KNOWN_EVENTS as ev (ev)}
          <label class="inline">
            <input
              type="checkbox"
              checked={draft.events?.includes(ev)}
              on:change={() => toggleEvent(ev)}
            />
            <code>{ev}</code>
          </label>
        {/each}
      </fieldset>
      <details>
        <summary>Advanced: body template (JSON)</summary>
        <textarea
          rows="6"
          placeholder={BODY_PLACEHOLDER}
          on:input={onBodyTemplateInput}
        >{draft.body_template ? JSON.stringify(draft.body_template, null, 2) : ""}</textarea>
      </details>
      <div class="form-actions">
        <button type="submit" class="primary">Save</button>
        <button type="button" on:click={() => { creating = false; }}>Cancel</button>
      </div>
    </form>
  {/if}

  {#if loading}
    <p>Loading…</p>
  {:else if items.length === 0}
    <p class="empty">No webhooks configured yet.</p>
  {:else}
    <table>
      <thead><tr>
        <th>Name</th><th>URL</th><th>Events</th><th>Enabled</th>
        <th>Last call</th><th>Status</th><th>Actions</th>
      </tr></thead>
      <tbody>
        {#each items as wh (wh.id)}
          <tr class:disabled={!wh.enabled}>
            <td>{wh.name}</td>
            <td class="mono ellipsis" title={wh.target_url}>{wh.target_url}</td>
            <td class="mono">{wh.events.join(", ")}</td>
            <td>{wh.enabled ? "✓" : "—"}</td>
            <td class="mono">{fmtDate(wh.last_call_at)}</td>
            <td class="mono">
              {wh.last_status_code ?? "—"}
              {#if wh.last_error}<span class="err" title={wh.last_error}>!</span>{/if}
            </td>
            <td class="actions">
              <button type="button" disabled={busy[wh.id]} on:click={() => test(wh)}>Test</button>
              <button type="button" disabled={busy[wh.id]} on:click={() => toggleEnabled(wh)}>
                {wh.enabled ? "Disable" : "Enable"}
              </button>
              <button type="button" class="danger" disabled={busy[wh.id]} on:click={() => remove(wh)}>Delete</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</section>

<style>
  .webhooks { display: grid; gap: var(--sp-3); }
  header { display: grid; gap: var(--sp-1); }
  .muted { color: var(--text-faint); font-size: var(--ts-sm); margin: 0; }
  .error { color: #c33; }
  .empty { color: var(--text-faint); font-style: italic; }
  .recipes { display: flex; gap: var(--sp-2); flex-wrap: wrap; }
  .recipes button {
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
  .card label.inline { display: inline-flex; align-items: center; gap: var(--sp-1); }
  .card input, .card textarea {
    padding: var(--sp-1);
    background: var(--bg-base);
    border: 1px solid var(--border-default);
    border-radius: var(--r-sm);
    color: inherit;
    font: inherit;
  }
  fieldset { border: 1px solid var(--border-default); border-radius: var(--r-sm);
             padding: var(--sp-2); display: flex; gap: var(--sp-2); flex-wrap: wrap; }
  fieldset legend { padding: 0 var(--sp-1); color: var(--text-faint); font-size: var(--ts-sm); }
  .form-actions { display: flex; gap: var(--sp-2); }
  .primary { background: var(--accent); color: var(--text-on-accent, var(--bg-base)); border: 0; }
  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: var(--sp-1) var(--sp-2);
           border-bottom: 1px solid var(--border-default); }
  th { color: var(--text-faint); font-weight: 600; font-size: var(--ts-sm); }
  .mono { font-family: var(--font-mono); font-size: var(--ts-sm); }
  .ellipsis { max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .disabled td { opacity: 0.5; }
  .err { color: #c33; font-weight: 700; margin-left: var(--sp-1); }
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
