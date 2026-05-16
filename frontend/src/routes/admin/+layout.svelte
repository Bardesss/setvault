<script lang="ts">
  import { goto } from "$app/navigation";
  import { page } from "$app/stores";
  import { session } from "$lib/stores/session";

  $: if ($session && $session.role !== "admin") {
    void goto("/");
  }

  const tabs = [
    { href: "/admin/users", label: "Users" },
    { href: "/admin/connectors", label: "Connectors" },
    { href: "/admin/storage", label: "Storage" },
    { href: "/admin/jobs", label: "Jobs" },
    { href: "/admin/system", label: "System" },
  ];

  $: currentPath = $page.url.pathname;
</script>

<svelte:head><title>Admin - SetVault</title></svelte:head>

<section class="admin">
  <header class="admin-header">
    <h1>Admin</h1>
    <nav class="tabs" aria-label="Admin sections">
      {#each tabs as t (t.href)}
        <a
          href={t.href}
          class:active={currentPath === t.href || currentPath.startsWith(t.href + "/")}
        >
          {t.label}
        </a>
      {/each}
    </nav>
  </header>
  <div class="content"><slot /></div>
</section>

<style>
  .admin {
    padding: var(--sp-6);
    display: grid;
    gap: var(--sp-4);
  }
  .admin-header { display: grid; gap: var(--sp-3); }
  .tabs {
    display: flex;
    gap: var(--sp-1);
    border-bottom: 1px solid var(--border-default);
    flex-wrap: wrap;
  }
  .tabs a {
    padding: var(--sp-2) var(--sp-3);
    border-bottom: 2px solid transparent;
    color: var(--text-faint);
    text-decoration: none;
    font-weight: 600;
  }
  .tabs a:hover { color: inherit; }
  .tabs a.active {
    color: inherit;
    border-bottom-color: var(--accent);
  }
  .content { display: grid; gap: var(--sp-3); }
</style>
