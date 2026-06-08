<script lang="ts">
  export let title: string | null = null;
  export let rows: Array<{ label: string; value: string }> = [];
</script>

<section class="status-block">
  {#if title}<h3>{title}</h3>{/if}
  {#each rows as r (r.label)}
    <div class="stat-line"><span class="k">{r.label}</span><span class="v">{r.value}</span></div>
  {/each}
  <slot />
</section>
