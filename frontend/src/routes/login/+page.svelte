<script lang="ts">
  import { goto } from "$app/navigation";
  import { invalidateAll } from "$app/navigation";
  import { _ } from "svelte-i18n";
  import { login } from "$lib/api/auth";
  import { ApiError } from "$lib/api/client";
  let email = "";
  let password = "";
  let error: string | null = null;
  let busy = false;

  async function submit() {
    error = null; busy = true;
    try {
      await login(email, password);
      await invalidateAll();
      await goto("/");
    } catch (e) {
      error = e instanceof ApiError && e.status === 429
        ? $_("auth.login.rate_limited")
        : $_("auth.login.invalid_credentials");
    } finally { busy = false; }
  }
</script>

<form class="login-card" on:submit|preventDefault={submit}>
  <h1>{$_("auth.login.heading")}</h1>
  <label>
    <span>{$_("auth.login.email")}</span>
    <input type="email" bind:value={email} required autocomplete="email" />
  </label>
  <label>
    <span>{$_("auth.login.password")}</span>
    <input type="password" bind:value={password} required autocomplete="current-password" />
  </label>
  {#if error}<p class="error" role="alert">{error}</p>{/if}
  <button type="submit" disabled={busy}>{busy ? $_("auth.login.submitting") : $_("auth.login.submit")}</button>
</form>

<style>
  .login-card { max-width: 360px; margin: 12vh auto; display: grid; gap: var(--sp-3); }
  label { display: grid; gap: var(--sp-1); }
  input { padding: var(--sp-2); background: var(--bg-surface);
          border: 1px solid var(--border-default); border-radius: var(--r-md); color: inherit; }
  .error { color: var(--accent-warning); }
  button { padding: var(--sp-3); background: var(--accent); color: var(--bg-base);
           border: 0; border-radius: var(--r-md); font-weight: 700; cursor: pointer; }
  @media (max-width: 600px) {
    .login-card { margin: var(--sp-6) var(--sp-3); max-width: none; }
    input { font-size: 16px; padding: var(--sp-3); }  /* prevents iOS auto-zoom on focus */
    button { padding: var(--sp-4); }
  }
</style>
