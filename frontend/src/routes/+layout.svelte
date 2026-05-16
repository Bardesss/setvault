<script lang="ts">
  import "$lib/styles/fonts.css";
  import "$lib/styles/tokens.css";
  import "$lib/styles/base.css";
  import "$lib/styles/components.css";
  import { page } from "$app/stores";
  import { session } from "$lib/stores/session";
  import NavRail from "$lib/components/NavRail.svelte";
  import MiniPlayer from "$lib/components/MiniPlayer.svelte";

  export let data: { user: import("$lib/api/auth").CurrentUser | null };
  $: session.set(data.user);

  $: user = data.user;
  $: showShell = !!user && !$page.url.pathname.startsWith("/login")
                  && !$page.url.pathname.startsWith("/invite/")
                  && !$page.url.pathname.startsWith("/reset/");
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
</style>
