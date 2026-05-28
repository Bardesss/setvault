<script lang="ts">
  export let title: string;
  export let subMeta: string | null = null;
  export let moreHref: string | null = null;
  export let moreLabel: string = "view all →";
</script>

<div class="section-head">
  <div>
    <h2>{title}</h2>
    {#if subMeta}<p class="sub-meta">{subMeta}</p>{/if}
  </div>
  {#if moreHref}
    <a class="show-more" href={moreHref}>{moreLabel}</a>
  {/if}
</div>
