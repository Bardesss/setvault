<script lang="ts">
  import type { PageData } from "./$types";
  export let data: PageData;

  $: envEntries = Object.entries(data.info.env).sort(([a], [b]) =>
    a.localeCompare(b),
  );
</script>

<h2>System</h2>

<div class="card">
  <h3>Build</h3>
  <dl>
    <dt>Version</dt><dd>{data.info.version}</dd>
    <dt>Users</dt><dd>{data.info.user_count}</dd>
    <dt>Sets</dt><dd>{data.info.set_count}</dd>
  </dl>
</div>

<div class="card">
  <h3>Backup</h3>
  <p class="hint">
    Downloads a <code>.tar</code> archive containing a Postgres dump and
    every file under each configured media root. Streaming starts as soon as
    <code>pg_dump</code> begins producing output. Scheduled backups + restore
    are tracked for v0.1.1.
  </p>
  <a class="primary" href="/api/admin/backup" download>Download backup</a>
</div>

<div class="card">
  <h3>Environment</h3>
  <p class="hint">Secrets ending in <code>_KEY</code>, <code>_SECRET</code>, <code>_TOKEN</code>, <code>_PASSWORD</code>, <code>_HOOK_SECRET</code> are redacted.</p>
  <table class="admin-table">
    <thead><tr><th>Name</th><th>Value</th></tr></thead>
    <tbody>
      {#each envEntries as [k, v] (k)}
        <tr>
          <td><code>{k}</code></td>
          <td><code class="val">{v}</code></td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>

<style>
  .card {
    display: grid;
    gap: var(--sp-3);
    padding: var(--sp-4);
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--r-md);
  }
  dl {
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: var(--sp-1) var(--sp-3);
    margin: 0;
  }
  dt { color: var(--text-faint); }
  dd { margin: 0; }
  .hint { color: var(--text-faint); margin: 0; font-size: 0.9em; }
  .admin-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--bg-base);
    border: 1px solid var(--border-default);
    border-radius: var(--r-md);
    overflow: hidden;
  }
  .admin-table th,
  .admin-table td {
    text-align: left;
    padding: var(--sp-2) var(--sp-3);
    border-bottom: 1px solid var(--border-default);
    vertical-align: top;
  }
  .admin-table th { color: var(--text-faint); font-weight: 600; }
  .admin-table tbody tr:last-child td { border-bottom: 0; }
  code { font-family: inherit; font-size: 0.85em; color: var(--text-faint); }
  .val { word-break: break-all; }
  a.primary {
    justify-self: start;
    padding: var(--sp-2) var(--sp-3);
    background: var(--accent);
    color: var(--text-on-accent, var(--bg-base));
    border-radius: var(--r-md);
    text-decoration: none;
    font-weight: 700;
  }
</style>
