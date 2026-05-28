<script lang="ts">
  import { onMount } from "svelte";
  import { api, ApiError } from "$lib/api/client";

  interface HealthPayload {
    version: {
      current: string;
      latest_known: string | null;
      latest_release_url: string | null;
      latest_checked_at: string | null;
      is_outdated: boolean;
    };
    audit_retention_days: number;
    storage_roots: Array<{
      id: string;
      name: string;
      host_path: string;
      last_health_check_at: string | null;
      last_health_status: string;
      default_for_ingest: boolean;
      free_bytes?: number;
      used_bytes?: number;
      total_bytes?: number;
    }>;
    connectors: Array<{
      id: string;
      name: string;
      kind: string;
      enabled: boolean;
      last_used_at: string | null;
      last_status: string | null;
    }>;
    providers: Array<{
      kind: string;
      name: string;
      enabled: boolean;
      priority: number;
    }>;
    tokens: { total: number; active: number; revoked: number };
  }

  let data: HealthPayload | null = null;
  let loading = true;
  let error: string | null = null;

  async function load() {
    loading = true;
    try {
      data = await api<HealthPayload>("/api/admin/health");
    } catch (e) {
      error = e instanceof ApiError ? e.detail : "load failed";
    } finally {
      loading = false;
    }
  }

  function fmtBytes(n: number | undefined): string {
    if (!n) return "—";
    const gb = n / (1024 ** 3);
    if (gb >= 1) return `${gb.toFixed(1)} GB`;
    const mb = n / (1024 ** 2);
    return `${mb.toFixed(1)} MB`;
  }

  function fmtPct(used: number | undefined, total: number | undefined): string {
    if (!used || !total) return "";
    return `${((used / total) * 100).toFixed(0)}%`;
  }

  function statusClass(s: string): string {
    if (s === "ok") return "ok";
    if (s === "near_full") return "warn";
    return "bad";
  }

  function fmtDate(iso: string | null): string {
    if (!iso) return "—";
    return iso.slice(0, 16).replace("T", " ");
  }

  onMount(load);
</script>

<section class="health">
  <header><h2>Health</h2></header>

  {#if error}<p class="error" role="alert">{error}</p>{/if}

  {#if loading}
    <p>Loading…</p>
  {:else if data}
    <article class="card">
      <h3>Version</h3>
      <dl>
        <dt>Running</dt>
        <dd class="mono">{data.version.current}</dd>
        <dt>Latest known</dt>
        <dd class="mono">
          {data.version.latest_known ?? "—"}
          {#if data.version.is_outdated && data.version.latest_release_url}
            — <a href={data.version.latest_release_url} target="_blank" rel="noopener">release notes →</a>
          {/if}
        </dd>
        <dt>Last checked</dt>
        <dd class="mono">{fmtDate(data.version.latest_checked_at)}</dd>
        <dt>Audit retention</dt>
        <dd class="mono">{data.audit_retention_days} days</dd>
      </dl>
    </article>

    <article class="card">
      <h3>Storage roots</h3>
      <table>
        <thead><tr>
          <th>Name</th><th>Path</th><th>Status</th>
          <th>Free</th><th>Used</th><th>Capacity</th>
        </tr></thead>
        <tbody>
          {#each data.storage_roots as r (r.id)}
            <tr>
              <td>{r.name}{r.default_for_ingest ? " ★" : ""}</td>
              <td class="mono">{r.host_path}</td>
              <td class={statusClass(r.last_health_status)}>{r.last_health_status}</td>
              <td class="mono">{fmtBytes(r.free_bytes)}</td>
              <td class="mono">{fmtBytes(r.used_bytes)} {fmtPct(r.used_bytes, r.total_bytes)}</td>
              <td class="mono">{fmtBytes(r.total_bytes)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </article>

    <article class="card">
      <h3>Connectors</h3>
      {#if data.connectors.length === 0}
        <p class="muted">No connectors configured.</p>
      {:else}
        <table>
          <thead><tr>
            <th>Name</th><th>Kind</th><th>Enabled</th>
            <th>Last used</th><th>Status</th>
          </tr></thead>
          <tbody>
            {#each data.connectors as c (c.id)}
              <tr>
                <td>{c.name}</td>
                <td class="mono">{c.kind}</td>
                <td>{c.enabled ? "✓" : "—"}</td>
                <td class="mono">{fmtDate(c.last_used_at)}</td>
                <td class="mono">{c.last_status ?? "—"}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    </article>

    <article class="card">
      <h3>Providers</h3>
      {#if data.providers.length === 0}
        <p class="muted">No providers configured.</p>
      {:else}
        <table>
          <thead><tr>
            <th>Kind</th><th>Name</th><th>Enabled</th><th>Priority</th>
          </tr></thead>
          <tbody>
            {#each data.providers as p (p.kind)}
              <tr>
                <td class="mono">{p.kind}</td>
                <td>{p.name}</td>
                <td>{p.enabled ? "✓" : "—"}</td>
                <td class="mono">{p.priority}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    </article>

    <article class="card">
      <h3>API tokens</h3>
      <dl>
        <dt>Total</dt><dd class="mono">{data.tokens.total}</dd>
        <dt>Active</dt><dd class="mono">{data.tokens.active}</dd>
        <dt>Revoked</dt><dd class="mono">{data.tokens.revoked}</dd>
      </dl>
    </article>
  {/if}
</section>

<style>
  .health { display: grid; gap: var(--sp-3); }
  .card {
    padding: var(--sp-3);
    border: 1px solid var(--border-default);
    border-radius: var(--r-md);
    background: var(--bg-surface);
    display: grid;
    gap: var(--sp-2);
  }
  .card h3 { margin: 0; font-size: var(--ts-md); }
  dl { display: grid; grid-template-columns: max-content 1fr;
       gap: var(--sp-1) var(--sp-3); margin: 0; }
  dt { color: var(--text-faint); }
  dd { margin: 0; }
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: var(--sp-1) var(--sp-2); border-bottom: 1px solid var(--border-default);
           text-align: left; }
  th { color: var(--text-faint); font-size: var(--ts-sm); font-weight: 600; }
  .mono { font-family: var(--font-mono); font-size: var(--ts-sm); }
  .ok { color: var(--accent); }
  .warn { color: #d97706; }
  .bad { color: #c33; }
  .muted { color: var(--text-faint); font-style: italic; margin: 0; }
  .error { color: #c33; }
</style>
