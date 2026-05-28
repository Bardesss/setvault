<script lang="ts">
  export let value: string;
  export let label: string;
  export let delta: string | null = null;
  export let deltaUp: boolean = false;
  export let accent: boolean = false;
</script>

<div class="home-stat">
  <div class="v" class:acc={accent}>{value}</div>
  <div class="k">{label}</div>
  {#if delta}
    <div class="delta" class:up={deltaUp}>{delta}</div>
  {/if}
</div>
