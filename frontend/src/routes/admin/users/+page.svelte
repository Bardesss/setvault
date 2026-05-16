<script lang="ts">
  import type { PageData } from "./$types";
  export let data: PageData;
</script>

<h2>Users</h2>
{#if data.users.length === 0}
  <p>No users.</p>
{:else}
  <table class="admin-table">
    <thead>
      <tr>
        <th>Email</th>
        <th>Username</th>
        <th>Display name</th>
        <th>Role</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {#each data.users as u (u.id)}
        <tr>
          <td>{u.email}</td>
          <td>{u.username}</td>
          <td>{u.display_name}</td>
          <td>{u.role}</td>
          <td>{u.disabled_at ? "disabled" : "active"}</td>
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
</style>
