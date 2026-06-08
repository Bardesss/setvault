<script lang="ts">
  import type { PageData } from "./$types";
  import AdminTable from "$lib/components/AdminTable.svelte";
  import StatusBlock from "$lib/components/StatusBlock.svelte";
  export let data: PageData;

  $: envEntries = Object.entries(data.info.env).sort(([a], [b]) =>
    a.localeCompare(b),
  );
</script>

<h2>System</h2>

<StatusBlock
  title="Build"
  rows={[
    { label: "Version", value: String(data.info.version) },
    { label: "Users", value: String(data.info.user_count) },
    { label: "Sets", value: String(data.info.set_count) },
  ]}
/>

<StatusBlock title="Backup">
  <p class="hint">
    Downloads a <code>.tar</code> archive containing a Postgres dump and
    every file under each configured media root. Streaming starts as soon as
    <code>pg_dump</code> begins producing output. Scheduled backups + restore
    are tracked for v0.1.1.
  </p>
  <a class="btn btn-primary" href="/api/admin/backup" download>Download backup</a>
</StatusBlock>

<StatusBlock title="Environment">
  <p class="hint">
    Secrets ending in <code>_KEY</code>, <code>_SECRET</code>,
    <code>_TOKEN</code>, <code>_PASSWORD</code>, <code>_HOOK_SECRET</code> are
    redacted.
  </p>
  <AdminTable columns={["Name", "Value"]}>
    {#each envEntries as [k, v] (k)}
      <tr>
        <td class="mono">{k}</td>
        <td class="mono val">{v}</td>
      </tr>
    {/each}
  </AdminTable>
</StatusBlock>

<style>
  .hint { color: var(--text-faint); margin: 0; font-size: var(--ts-sm); }
  .val { word-break: break-all; }
</style>
