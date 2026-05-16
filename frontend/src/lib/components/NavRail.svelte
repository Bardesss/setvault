<script lang="ts">
  import type { CurrentUser } from "$lib/api/auth";
  import { logout } from "$lib/api/auth";
  import { goto } from "$app/navigation";
  export let user: CurrentUser;

  async function doLogout() {
    await logout();
    await goto("/login");
  }
</script>

<aside class="nav-rail">
  <a class="brand" href="/">SetVault</a>
  <nav>
    <a href="/">Home</a>
    <a href="/sets">Library</a>
    <a href="/sets/new">Upload</a>
    <a href="/search">Search</a>
    <a href="/settings">Settings</a>
    {#if user.role === "admin"}<a href="/admin/users">Admin</a>{/if}
  </nav>
  <button class="signout" on:click={doLogout}>Sign out</button>
</aside>

<style>
  .nav-rail {
    display: flex; flex-direction: column; gap: var(--sp-3);
    padding: var(--sp-4); border-right: 1px solid var(--border-default);
    background: var(--bg-surface);
  }
  .brand { font-weight: 800; letter-spacing: 0.02em; }
  nav { display: flex; flex-direction: column; gap: var(--sp-2); }
  .signout { margin-top: auto; background: none; border: 1px solid var(--border-default);
             padding: var(--sp-2) var(--sp-3); border-radius: var(--r-md); color: inherit;
             cursor: pointer; }
</style>
