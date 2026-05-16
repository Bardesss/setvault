<script lang="ts">
  import Uploader from "$lib/components/Uploader.svelte";
</script>

<svelte:head><title>New set - SetVault</title></svelte:head>

<section>
  <h1>New set</h1>
  <Uploader />
</section>

<style>
  section { padding: var(--sp-6); display: grid; gap: var(--sp-4); }
</style>
