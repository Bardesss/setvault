<script lang="ts">
  import type { PageData } from "./$types";
  export let data: PageData;
</script>

<h2>Connectors</h2>
{#if data.connectors.length === 0}
  <p>No connectors configured.</p>
{:else}
  <table class="admin-table">
    <thead>
      <tr>
        <th>Name</th>
        <th>Kind</th>
        <th>Enabled</th>
        <th>Scope</th>
      </tr>
    </thead>
    <tbody>
      {#each data.connectors as c (c.id)}
        <tr>
          <td>{c.name}</td>
          <td>{c.kind}</td>
          <td>{c.enabled ? "yes" : "no"}</td>
          <td><code>{JSON.stringify(c.scope_filter)}</code></td>
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
