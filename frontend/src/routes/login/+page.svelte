<script lang="ts">
  import { goto } from "$app/navigation";
  import { invalidateAll } from "$app/navigation";
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
        ? "too many attempts — try again in a minute"
        : "invalid credentials";
    } finally { busy = false; }
  }
</script>

<form class="login-card" on:submit|preventDefault={submit}>
  <h1>Sign in</h1>
  <label>
    <span>Email</span>
    <input type="email" bind:value={email} required autocomplete="email" />
  </label>
  <label>
    <span>Password</span>
    <input type="password" bind:value={password} required autocomplete="current-password" />
  </label>
  {#if error}<p class="error" role="alert">{error}</p>{/if}
  <button type="submit" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
</form>

<style>
  .login-card { max-width: 360px; margin: 12vh auto; display: grid; gap: var(--sp-3); }
  label { display: grid; gap: var(--sp-1); }
  input { padding: var(--sp-2); background: var(--bg-surface);
          border: 1px solid var(--border-default); border-radius: var(--r-md); color: inherit; }
  .error { color: var(--accent-warning); }
  button { padding: var(--sp-3); background: var(--accent); color: var(--bg-base);
           border: 0; border-radius: var(--r-md); font-weight: 700; cursor: pointer; }
</style>
