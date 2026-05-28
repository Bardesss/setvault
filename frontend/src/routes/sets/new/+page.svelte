<script lang="ts">
  import { _ } from "svelte-i18n";
  import AddSetUrlTab from "$lib/components/AddSetUrlTab.svelte";
  import Uploader from "$lib/components/Uploader.svelte";

  let activeTab: "upload" | "url" = "upload";
</script>

<svelte:head><title>New set - SetVault</title></svelte:head>

<section>
  <h1>New set</h1>

  <div class="tabs" role="tablist">
    <button
      type="button"
      role="tab"
      aria-selected={activeTab === "upload"}
      class:active={activeTab === "upload"}
      on:click={() => (activeTab = "upload")}
    >
      {$_("url_rip.tab_upload")}
    </button>
    <button
      type="button"
      role="tab"
      aria-selected={activeTab === "url"}
      class:active={activeTab === "url"}
      on:click={() => (activeTab = "url")}
    >
      {$_("url_rip.tab_label")}
    </button>
  </div>

  {#if activeTab === "upload"}
    <Uploader />
  {:else}
    <AddSetUrlTab />
  {/if}
</section>

<style>
  section { padding: var(--sp-6); display: grid; gap: var(--sp-4); }
  .tabs { display: flex; gap: var(--sp-2); border-bottom: 1px solid var(--border-default); }
  .tabs button {
    background: transparent;
    border: none;
    padding: var(--sp-2) var(--sp-3);
    color: var(--text-faint);
    font: inherit;
    cursor: pointer;
    border-bottom: 2px solid transparent;
  }
  .tabs button.active {
    color: var(--text-default);
    border-bottom-color: var(--accent, var(--text-default));
  }
</style>
