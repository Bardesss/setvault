<script lang="ts">
  import type { CurrentUser } from "$lib/api/auth";
  import { logout } from "$lib/api/auth";
  import { goto } from "$app/navigation";
  import { _ } from "svelte-i18n";
  import NotificationBell from "./NotificationBell.svelte";
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
    <a href="/" aria-label={$_("nav.home")}>
      <span class="icon" aria-hidden="true">🏠</span>
      <span class="label">{$_("nav.home")}</span>
    </a>
    <a href="/sets" aria-label={$_("nav.library")}>
      <span class="icon" aria-hidden="true">📚</span>
      <span class="label">{$_("nav.library")}</span>
    </a>
    <a href="/sets/new" aria-label={$_("nav.upload")}>
      <span class="icon" aria-hidden="true">⬆️</span>
      <span class="label">{$_("nav.upload")}</span>
    </a>
    <a href="/search" aria-label={$_("nav.search")}>
      <span class="icon" aria-hidden="true">🔍</span>
      <span class="label">{$_("nav.search")}</span>
    </a>
    <a href="/settings" aria-label={$_("nav.settings")}>
      <span class="icon" aria-hidden="true">⚙️</span>
      <span class="label">{$_("nav.settings")}</span>
    </a>
    {#if user.role === "admin"}
      <a href="/admin/users" aria-label={$_("nav.admin")}>
        <span class="icon" aria-hidden="true">🛡️</span>
        <span class="label">{$_("nav.admin")}</span>
      </a>
    {/if}
  </nav>
  <NotificationBell />
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
  nav a { display: flex; align-items: center; gap: var(--sp-2); color: inherit;
          text-decoration: none; padding: var(--sp-1) var(--sp-2);
          border-radius: var(--r-sm); }
  nav a:hover { background: var(--accent-softer, transparent); }
  .icon { display: none; }                /* desktop: text-only */
  .signout { margin-top: auto; background: none; border: 1px solid var(--border-default);
             padding: var(--sp-2) var(--sp-3); border-radius: var(--r-md); color: inherit;
             cursor: pointer; }

  @media (max-width: 600px) {
    .nav-rail {
      position: fixed;
      bottom: 0; left: 0; right: 0;
      flex-direction: row;
      justify-content: space-around;
      align-items: center;
      border-right: none;
      border-top: 1px solid var(--border-default);
      padding: var(--sp-2);
      z-index: 90;
      gap: 0;
      /* Pin under any browser bottom-bar / iOS safe-area */
      padding-bottom: max(var(--sp-2), env(safe-area-inset-bottom));
    }
    .brand, .signout { display: none; }   /* surface elsewhere */
    nav { flex-direction: row; gap: 0; flex: 1; justify-content: space-around; }
    nav a {
      flex-direction: column;
      gap: 2px;
      padding: var(--sp-1);
      min-width: 44px;
      min-height: 44px;
      font-size: var(--ts-xs);
      text-align: center;
    }
    .icon { display: block; font-size: 22px; line-height: 1; }
    .label { font-size: 10px; }
  }
</style>
