<script lang="ts">
  import type { CurrentUser } from "$lib/api/auth";
  import { logout } from "$lib/api/auth";
  import { goto } from "$app/navigation";
  import { _ } from "svelte-i18n";
  export let user: CurrentUser;

  async function doLogout() {
    await logout();
    await goto("/login");
  }
</script>

<aside class="nav-rail">
  <!-- Brand name is intentionally not translated. -->
  <a class="brand" href="/">SetVault</a>
  <nav>
    <a href="/">{$_("nav.home")}</a>
    <a href="/sets">{$_("nav.library")}</a>
    <a href="/sets/new">{$_("nav.upload")}</a>
    <a href="/search">{$_("nav.search")}</a>
    <a href="/settings">{$_("nav.settings")}</a>
    {#if user.role === "admin"}<a href="/admin/users">{$_("nav.admin")}</a>{/if}
  </nav>
  <button class="signout" on:click={doLogout}>{$_("nav.sign_out")}</button>
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
