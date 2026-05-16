<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";
  import { api, ApiError } from "$lib/api/client";
  let password = "", error: string | null = null;

  async function submit() {
    error = null;
    try {
      await api(`/api/password-reset/${$page.params.token}/redeem`, {
        method: "POST",
        body: JSON.stringify({ password }),
      });
      await goto("/login");
    } catch (e) {
      error = e instanceof ApiError ? e.detail : "unknown error";
    }
  }
</script>

<form class="card" on:submit|preventDefault={submit}>
  <h1>Reset password</h1>
  <label><span>New password</span><input type="password" bind:value={password} required minlength="12" /></label>
  {#if error}<p class="error" role="alert">{error}</p>{/if}
  <button type="submit">Reset password</button>
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
