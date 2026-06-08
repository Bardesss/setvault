<script lang="ts">
  export let columns: string[];
  export let caption: string | null = null;
</script>

<table class="admin-table">
  {#if caption}<caption class="sr-only">{caption}</caption>{/if}
  <thead>
    <tr>
      {#each columns as c (c)}<th>{c}</th>{/each}
    </tr>
  </thead>
  <tbody>
    <slot />
  </tbody>
</table>

<style>
  .sr-only {
    position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
    overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;
  }
</style>
