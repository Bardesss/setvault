<script lang="ts">
  import { _ } from "svelte-i18n";
  import {
    testProvider,
    upsertProvider,
    type ProviderConfig,
    type ProviderKind,
  } from "$lib/api/providers";
  import type { PageData } from "./$types";

  export let data: PageData;
  let providers: ProviderConfig[] = data.providers;
  let kind: ProviderKind = "musicbrainz";
  let configFields: Record<string, string> = {};
  let saving = false;
  let testResult: string | null = null;

  const SCHEMAS: Record<ProviderKind, { key: string; label: string }[]> = {
    musicbrainz: [{ key: "user_agent", label: "User-Agent (per MB ToS)" }],
    discogs: [{ key: "token", label: "Personal access token" }],
    acoustid: [{ key: "api_key", label: "Application API key" }],
  };
  $: configSchema = SCHEMAS[kind];

  async function save() {
    saving = true;
    try {
      const out = await upsertProvider(kind, { config: configFields, enabled: true });
      providers = [...providers.filter((p) => p.provider_kind !== kind), out];
    } finally {
      saving = false;
    }
  }

  async function runTest(k: ProviderKind) {
    const r = await testProvider(k);
    testResult = r.ok ? "ok" : (r.error ?? "failed");
  }
</script>

<svelte:head><title>{$_("admin.providers.title")} - SetVault</title></svelte:head>

<section>
  <h1>{$_("admin.providers.title")}</h1>

  <table>
    <thead><tr>
      <th>{$_("admin.providers.kind")}</th>
      <th>{$_("admin.providers.enabled")}</th>
      <th>{$_("admin.providers.priority")}</th>
      <th>{$_("admin.providers.actions")}</th>
    </tr></thead>
    <tbody>
      {#each providers as p (p.id)}
        <tr>
          <td>{p.provider_kind}</td>
          <td>{p.enabled ? "OK" : "off"}</td>
          <td>{p.priority}</td>
          <td>
            <button on:click={() => runTest(p.provider_kind)}>
              {$_("admin.providers.test")}
            </button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>

  <h2>{$_("admin.providers.add_or_update")}</h2>
  <label>
    {$_("admin.providers.kind")}
    <select bind:value={kind}>
      <option value="musicbrainz">MusicBrainz</option>
      <option value="discogs">Discogs</option>
      <option value="acoustid">AcoustID</option>
    </select>
  </label>
  {#each configSchema as f (f.key)}
    <label>
      {f.label}
      <input type="text" bind:value={configFields[f.key]} />
    </label>
  {/each}
  <button class="primary" on:click={save} disabled={saving}>
    {$_("admin.providers.save")}
  </button>
  {#if testResult}<p>Test: {testResult}</p>{/if}
</section>

<style>
  section { display: grid; gap: var(--sp-4); }
  table { width: 100%; border-collapse: collapse; }
  th, td {
    text-align: left;
    padding: var(--sp-2);
    border-bottom: 1px solid var(--border-default);
  }
  label { display: grid; gap: var(--sp-1); max-width: 480px; }
  input, select {
    padding: var(--sp-2);
    border: 1px solid var(--border-default);
    border-radius: var(--r-sm);
    background: var(--bg-input);
    color: var(--text-default);
    font: inherit;
  }
  button {
    background: none;
    border: 1px solid var(--border-default);
    border-radius: var(--r-sm);
    padding: var(--sp-1) var(--sp-3);
    color: var(--text-muted);
    cursor: pointer;
  }
  .primary {
    background: var(--accent);
    color: var(--text-on-accent);
    border: none;
    padding: var(--sp-2) var(--sp-3);
    justify-self: start;
  }
</style>
