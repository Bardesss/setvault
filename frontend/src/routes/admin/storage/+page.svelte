<script lang="ts">
  import type { PageData } from "./$types";
  export let data: PageData;

  function formatBytes(n: number | null): string {
    if (n === null) return "unlimited";
    const units = ["B", "KB", "MB", "GB", "TB"];
    let value = n;
    let i = 0;
    while (value >= 1024 && i < units.length - 1) {
      value /= 1024;
      i += 1;
    }
    return `${value.toFixed(1)} ${units[i]}`;
  }
</script>

<h2>Storage</h2>
{#if data.roots.length === 0}
  <p>No media roots configured.</p>
{:else}
  <table class="admin-table">
    <thead>
      <tr>
        <th>Name</th>
        <th>Host path</th>
        <th>Default ingest</th>
        <th>Quota</th>
        <th>Health</th>
      </tr>
    </thead>
    <tbody>
      {#each data.roots as r (r.id)}
        <tr>
          <td>{r.name}</td>
          <td><code>{r.host_path}</code></td>
          <td>{r.default_for_ingest ? "yes" : "no"}</td>
          <td>{formatBytes(r.max_bytes)}</td>
          <td>{r.last_health_status ?? "unknown"}</td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}

<style>
  .admin-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--r-md);
    overflow: hidden;
  }
  .admin-table th,
  .admin-table td {
    text-align: left;
    padding: var(--sp-2) var(--sp-3);
    border-bottom: 1px solid var(--border-default);
  }
  .admin-table th { color: var(--text-faint); font-weight: 600; }
  .admin-table tbody tr:last-child td { border-bottom: 0; }
  code { font-family: inherit; font-size: 0.85em; color: var(--text-faint); }
</style>
