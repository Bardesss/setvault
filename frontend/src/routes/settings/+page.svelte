<script lang="ts">
  import { api, ApiError } from "$lib/api/client";
  import { session } from "$lib/stores/session";
  import { _ } from "svelte-i18n";

  let currentPassword = "";
  let newPassword = "";
  let error: string | null = null;
  let success: string | null = null;
  let busy = false;

  async function submit() {
    error = null;
    success = null;
    busy = true;
    try {
      await api("/api/me/change-password", {
        method: "POST",
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });
      success = $_("settings.password_updated");
      currentPassword = "";
      newPassword = "";
    } catch (e) {
      error = e instanceof ApiError ? e.detail : $_("settings.failed");
    } finally {
      busy = false;
    }
  }
</script>

<section class="settings">
  <h1>{$_("settings.heading")}</h1>

  {#if $session}
    <div class="card profile">
      <h2>{$_("settings.profile")}</h2>
      <dl>
        <dt>{$_("settings.display_name")}</dt><dd>{$session.display_name}</dd>
        <dt>{$_("settings.username")}</dt><dd>{$session.username}</dd>
        <dt>{$_("settings.email")}</dt><dd>{$session.email}</dd>
        <dt>{$_("settings.role")}</dt><dd>{$session.role}</dd>
      </dl>
    </div>
  {/if}

  <form class="card" on:submit|preventDefault={submit}>
    <h2>{$_("settings.change_password")}</h2>
    <label>
      <span>{$_("settings.current_password")}</span>
      <input
        type="password"
        bind:value={currentPassword}
        required
        autocomplete="current-password"
      />
    </label>
    <label>
      <span>{$_("settings.new_password")}</span>
      <input
        type="password"
        bind:value={newPassword}
        required
        minlength="12"
        autocomplete="new-password"
      />
    </label>
    {#if error}<p class="error" role="alert">{error}</p>{/if}
    {#if success}<p class="success" role="status">{success}</p>{/if}
    <button type="submit" disabled={busy}>
      {busy ? $_("settings.saving") : $_("settings.change_password")}
    </button>
  </form>
</section>

<style>
  .settings { padding: var(--sp-6); display: grid; gap: var(--sp-4); max-width: 560px; }
  .card {
    display: grid;
    gap: var(--sp-3);
    padding: var(--sp-4);
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--r-md);
  }
  .profile dl {
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: var(--sp-1) var(--sp-3);
    margin: 0;
  }
  .profile dt { color: var(--text-faint); }
  .profile dd { margin: 0; }
  label { display: grid; gap: var(--sp-1); }
  input {
    padding: var(--sp-2);
    background: var(--bg-base);
    border: 1px solid var(--border-default);
    border-radius: var(--r-md);
    color: inherit;
  }
  .error { color: var(--accent-warning); margin: 0; }
  .success { color: var(--accent); margin: 0; }
  button {
    padding: var(--sp-3);
    background: var(--accent);
    color: var(--bg-base);
    border: 0;
    border-radius: var(--r-md);
    font-weight: 700;
    cursor: pointer;
  }
  button:disabled { opacity: 0.6; cursor: progress; }
</style>
