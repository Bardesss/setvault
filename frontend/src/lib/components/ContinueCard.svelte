<script lang="ts">
  export let slug: string;
  export let title: string;
  export let artist: string = "";
  export let positionSeconds: number;
  export let durationSeconds: number | null;

  function fmt(s: number): string {
    const safe = Math.max(0, Math.floor(s));
    const h = Math.floor(safe / 3600);
    const m = Math.floor((safe % 3600) / 60);
    const sec = safe % 60;
    if (h > 0) return `${h}:${m.toString().padStart(2, "0")}:${sec.toString().padStart(2, "0")}`;
    return `${m}:${sec.toString().padStart(2, "0")}`;
  }

  $: pct = durationSeconds && durationSeconds > 0
    ? Math.min(100, Math.max(0, (positionSeconds / durationSeconds) * 100))
    : 0;
</script>

<a class="continue-card" href={`/sets/${slug}`}>
  <div class="continue-cover" aria-hidden="true"></div>
  <div class="body">
    <div class="ttl">{title}</div>
    {#if artist}<div class="artist">{artist}</div>{/if}
    <div class="progress-time">
      {fmt(positionSeconds)} / {durationSeconds ? fmt(durationSeconds) : "?"}
      {#if pct > 0} · {pct.toFixed(0)}% played{/if}
    </div>
    <div class="progress-bar"><div class="progress-fill" style="width: {pct}%"></div></div>
  </div>
</a>
