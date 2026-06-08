<script lang="ts">
  import { createEventDispatcher } from "svelte";
  export let title: string | null = null;
  const dispatch = createEventDispatcher<{ submit: void }>();
</script>

<form class="admin-form" on:submit|preventDefault={() => dispatch("submit")}>
  {#if title}<h2>{title}</h2>{/if}
  <slot />
  {#if $$slots.actions}
    <div class="admin-actions"><slot name="actions" /></div>
  {/if}
</form>

<style>
  h2 { margin: 0; font-size: var(--ts-lg); color: var(--text-strong); }
</style>
