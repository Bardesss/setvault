<script lang="ts">
  export let tabs: Array<{ id: string; label: string; count?: number | null }>;
  export let active: string;
</script>

<div class="tab-strip" role="tablist">
  {#each tabs as t (t.id)}
    <button
      type="button"
      role="tab"
      class="tab"
      class:active={t.id === active}
      aria-selected={t.id === active}
      on:click={() => (active = t.id)}
    >
      {t.label}
      {#if t.count != null}<span class="count">{t.count}</span>{/if}
    </button>
  {/each}
</div>
