<script lang="ts">
  import type { PageData } from "./$types";
  export let data: PageData;
</script>

<h2>Jobs</h2>
{#if data.jobs.length === 0}
  <p>No jobs recorded yet.</p>
{:else}
  <table class="admin-table">
    <thead>
      <tr>
        <th>ID</th>
        <th>Kind</th>
        <th>Status</th>
        <th>Progress</th>
        <th>Created</th>
        <th>Finished</th>
        <th>Message</th>
      </tr>
    </thead>
    <tbody>
      {#each data.jobs as j (j.id)}
        <tr>
          <td><code>{j.id}</code></td>
          <td>{j.kind}</td>
          <td>{j.status}</td>
          <td>{j.progress_pct}%</td>
          <td>{j.created_at}</td>
          <td>{j.finished_at ?? "—"}</td>
          <td>{j.message ?? ""}</td>
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
