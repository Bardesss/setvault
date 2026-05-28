<script lang="ts">
  import { onMount } from "svelte";
  import { api, ApiError } from "$lib/api/client";

  interface ScheduledTask {
    id: string;
    func_name: string;
    short_name: string;
    next_run_at: string | null;
    interval_seconds: number | null;
    last_run_at: string | null;
    last_status: string | null;
  }

  let items: ScheduledTask[] = [];
  let loading = true;
  let error: string | null = null;
  let busy: Record<string, boolean> = {};
  let notice: string | null = null;

  async function load() {
    loading = true;
    try {
      const r = await api<{ items: ScheduledTask[] }>("/api/admin/tasks");
      items = r.items;
    } catch (e) {
      error = e instanceof ApiError ? e.detail : "load failed";
    } finally {
      loading = false;
    }
  }

  async function runNow(funcName: string) {
    busy[funcName] = true;
    busy = busy;
    notice = null;
    try {
      await api("/api/admin/tasks/run-now", {
        method: "POST",
        body: JSON.stringify({ func_name: funcName }),
      });
      notice = `Queued ${funcName.split(".").pop()}`;
    } catch (e) {
      error = e instanceof ApiError ? e.detail : "run-now failed";
    } finally {
      busy[funcName] = false;
      busy = busy;
    }
  }

  function fmtInterval(secs: number | null): string {
    if (!secs) return "—";
    if (secs < 60) return `${secs}s`;
    if (secs < 3600) return `${Math.round(secs / 60)}m`;
    if (secs < 86400) return `${Math.round(secs / 3600)}h`;
    return `${Math.round(secs / 86400)}d`;
  }

  function fmtDate(iso: string | null): string {
    if (!iso) return "—";
    return iso.slice(0, 16).replace("T", " ");
  }

  onMount(load);
</script>

<section class="tasks">
  <header>
    <h2>Scheduled tasks</h2>
    <p class="muted">
      Periodic jobs registered with rq-scheduler. Re-runs on next interval
      automatically; the Run-now button enqueues an immediate one-off.
    </p>
  </header>

  {#if error}<p class="error" role="alert">{error}</p>{/if}
  {#if notice}<p class="ok" role="status">{notice}</p>{/if}

  {#if loading}
    <p>Loading…</p>
  {:else if items.length === 0}
    <p class="empty">No scheduled jobs registered.</p>
  {:else}
    <table>
      <thead>
        <tr>
          <th>Job</th>
          <th>Interval</th>
          <th>Next run</th>
          <th>Last run</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each items as task (task.id)}
          <tr>
            <td><code>{task.short_name}</code></td>
            <td class="mono">{fmtInterval(task.interval_seconds)}</td>
            <td class="mono">{fmtDate(task.next_run_at)}</td>
            <td class="mono">{fmtDate(task.last_run_at)}</td>
            <td class="mono">{task.last_status ?? "—"}</td>
            <td>
              <button
                type="button"
                disabled={busy[task.func_name]}
                on:click={() => runNow(task.func_name)}
              >Run now</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</section>

<style>
  .tasks { display: grid; gap: var(--sp-3); }
  header { display: grid; gap: var(--sp-1); }
  .muted { color: var(--text-faint); font-size: var(--ts-sm); margin: 0; }
  .error { color: #c33; }
  .ok { color: var(--accent); }
  .empty { color: var(--text-faint); font-style: italic; }
  table { width: 100%; border-collapse: collapse; }
  th, td {
    text-align: left;
    padding: var(--sp-2);
    border-bottom: 1px solid var(--border-default);
  }
  th { color: var(--text-faint); font-weight: 600; font-size: var(--ts-sm); }
  code { font-family: var(--font-mono); font-size: var(--ts-sm); }
  .mono { font-family: var(--font-mono); font-size: var(--ts-sm); color: var(--text-faint); }
  button {
    padding: var(--sp-1) var(--sp-2);
    border: 1px solid var(--border-default);
    background: transparent;
    color: inherit;
    border-radius: var(--r-sm);
    cursor: pointer;
  }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
