<script lang="ts">
  import { goto } from "$app/navigation";
  import type { CurrentUser } from "$lib/api/auth";

  export let user: CurrentUser;

  $: initial = (user.display_name || user.email || "?").charAt(0).toUpperCase();

  function openSearch() {
    goto("/search");
  }

  function handleKey(e: KeyboardEvent) {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      openSearch();
    }
  }
</script>

<svelte:window on:keydown={handleKey} />

<header class="topbar">
  <a class="brand" href="/" aria-label="SetVault home">
    <span class="brand-dot"></span>
    <span class="brand-name">SETVAULT</span>
  </a>

  <button class="search-trigger" type="button" on:click={openSearch} aria-label="Open search">
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" width="14" height="14" aria-hidden="true">
      <circle cx="7" cy="7" r="5" />
      <line x1="11" y1="11" x2="14" y2="14" />
    </svg>
    <span>Search artists, sets, parties…</span>
    <span class="kbd">⌘ K</span>
  </button>

  <div class="topbar-right">
    <a class="btn btn-ghost btn-icon" href="/me/bookmarks" aria-label="Bookmarks">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" width="14" height="14" aria-hidden="true">
        <path d="M4 2h8v12l-4-3-4 3V2z" />
      </svg>
    </a>
    <div class="user-pip" aria-label="Account">{initial}</div>
  </div>
</header>

<style>
  .user-pip {
    width: 32px;
    height: 32px;
    background: var(--accent-soft);
    border: 1px solid var(--accent);
    border-radius: 50%;
    display: grid;
    place-items: center;
    color: var(--accent);
    font-weight: 700;
    font-size: var(--ts-md);
  }
  .btn-icon {
    display: grid;
    place-items: center;
    width: 32px;
    height: 32px;
    color: var(--text-muted);
    text-decoration: none;
    border: 1px solid var(--border-default);
    border-radius: var(--r-sm);
  }
  .btn-icon:hover { color: var(--accent); border-color: var(--accent); }
</style>
