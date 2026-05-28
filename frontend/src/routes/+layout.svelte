<script lang="ts">
  import "$lib/styles/fonts.css";
  import "$lib/styles/tokens.css";
  import "$lib/styles/_breakpoints.css";
  import "$lib/styles/base.css";
  import "$lib/styles/components.css";
  import { onMount } from "svelte";
  import { browser } from "$app/environment";
  import { page } from "$app/stores";
  import { session } from "$lib/stores/session";
  import { setupI18n } from "$lib/i18n";
  import NavRail from "$lib/components/NavRail.svelte";
  import MiniPlayer from "$lib/components/MiniPlayer.svelte";

  setupI18n();

  onMount(async () => {
    if (browser && "serviceWorker" in navigator) {
      try {
        await navigator.serviceWorker.register("/service-worker.js", {
          type: "module",
        });
      } catch {
        // best-effort; offline mode just doesn't activate
      }
    }
  });

  export let data: { user: import("$lib/api/auth").CurrentUser | null };
  $: session.set(data.user);

  $: user = data.user;
  $: showShell = !!user && !$page.url.pathname.startsWith("/login")
                  && !$page.url.pathname.startsWith("/invite/")
                  && !$page.url.pathname.startsWith("/reset/")
                  && !$page.url.pathname.startsWith("/embed/");
</script>

<div class="app-shell" class:no-shell={!showShell}>
  {#if showShell && user}<NavRail {user} />{/if}
  <main class="main"><slot /></main>
</div>
{#if showShell}<MiniPlayer />{/if}

<style>
  .app-shell { display: grid; grid-template-columns: 220px 1fr; min-height: 100vh; }
  .app-shell.no-shell { grid-template-columns: 1fr; }
  .main { min-width: 0; }
  @media (max-width: 760px) {
    .app-shell { grid-template-columns: 1fr; }
  }
  /* Phone: NavRail becomes a fixed bottom bar, so leave room for it */
  @media (max-width: 600px) {
    .app-shell:not(.no-shell) .main {
      padding-bottom: calc(64px + env(safe-area-inset-bottom, 0px));
    }
  }
</style>
