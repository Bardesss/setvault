<script lang="ts">
  import { _ } from "svelte-i18n";
  import AdminTable from "$lib/components/AdminTable.svelte";
  import EmptyState from "$lib/components/EmptyState.svelte";
  import { setSourceEnabled, type SourceState } from "$lib/api/ingest_sources";
  import type { PageData } from "./$types";

  export let data: PageData;
  let sources: SourceState[] = data.sources;
  let busy: Record<string, boolean> = {};
  let errorMsg: string | null = null;

  async function toggle(s: SourceState) {
    busy[s.kind] = true;
    busy = busy;
    errorMsg = null;
    try {
      const updated = await setSourceEnabled(s.kind, !s.enabled);
      sources = sources.map((x) => (x.kind === updated.kind ? updated : x));
    } catch (e) {
      errorMsg = e instanceof Error ? e.message : "failed";
    } finally {
      busy[s.kind] = false;
      busy = busy;
    }
  }
</script>

<svelte:head><title>{$_("sources.admin_title")} - SetVault</title></svelte:head>

<section>
  <h1>{$_("sources.admin_title")}</h1>

  {#if errorMsg}
    <p class="admin-msg is-error" role="alert">{errorMsg}</p>
  {/if}

  {#if sources.length === 0}
    <EmptyState message={$_("sources.admin_empty")} />
  {:else}
    <AdminTable
      columns={[
        $_("sources.col_source"),
        $_("sources.col_state"),
        $_("sources.col_enabled"),
        "",
      ]}
    >
      {#each sources as s (s.kind)}
        <tr class:is-disabled={!s.enabled}>
          <td>{s.name}</td>
          <td class="mono">{s.state}{s.last_error ? ` — ${s.last_error}` : ""}</td>
          <td>{s.enabled ? "✓" : "—"}</td>
          <td class="cell-actions">
            <button
              type="button"
              class="btn btn-sm"
              disabled={busy[s.kind]}
              on:click={() => toggle(s)}
            >
              {s.enabled ? $_("sources.disable") : $_("sources.enable")}
            </button>
          </td>
        </tr>
      {/each}
    </AdminTable>
  {/if}
</section>

<style>
  section { display: grid; gap: var(--sp-4); }
</style>
