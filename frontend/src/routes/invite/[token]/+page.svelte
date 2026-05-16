<script lang="ts">
  import { page } from "$app/stores";
  import { invalidateAll, goto } from "$app/navigation";
  import { _ } from "svelte-i18n";
  import { api, ApiError } from "$lib/api/client";
  let username = "", display_name = "", password = "", error: string | null = null;

  async function accept() {
    error = null;
    try {
      await api(`/api/invites/${$page.params.token}/redeem`, {
        method: "POST",
        body: JSON.stringify({ username, display_name, password }),
      });
      await invalidateAll();
      await goto("/");
    } catch (e) {
      error = e instanceof ApiError ? e.detail : $_("auth.invite.unknown_error");
    }
  }
</script>

<form class="card" on:submit|preventDefault={accept}>
  <h1>{$_("auth.invite.heading")}</h1>
  <label><span>{$_("auth.invite.username")}</span><input bind:value={username} required minlength="2" /></label>
  <label><span>{$_("auth.invite.display_name")}</span><input bind:value={display_name} required /></label>
  <label><span>{$_("auth.invite.password")}</span><input type="password" bind:value={password} required minlength="12" /></label>
  {#if error}<p class="error" role="alert">{error}</p>{/if}
  <button type="submit">{$_("auth.invite.accept_invite")}</button>
</form>

<style>
  .card { max-width: 380px; margin: 10vh auto; display: grid; gap: var(--sp-3); }
  label { display: grid; gap: var(--sp-1); }
  input { padding: var(--sp-2); background: var(--bg-surface);
          border: 1px solid var(--border-default); border-radius: var(--r-md); color: inherit; }
  .error { color: var(--accent-warning); }
  button { padding: var(--sp-3); background: var(--accent); color: var(--bg-base);
           border: 0; border-radius: var(--r-md); font-weight: 700; }
</style>
