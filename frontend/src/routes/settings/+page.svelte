<script lang="ts">
  import { onMount } from "svelte";
  import { api, ApiError } from "$lib/api/client";
  import {
    createRssToken,
    listMyRssTokens,
    revokeRssToken,
    type RssToken,
    type RssTokenWithPlaintext,
  } from "$lib/api/feeds";
  import { session } from "$lib/stores/session";
  import { _ } from "svelte-i18n";

  let currentPassword = "";
  let newPassword = "";
  let error: string | null = null;
  let success: string | null = null;
  let busy = false;

  let rssTokens: RssToken[] = [];
  let rssTokensLoaded = false;
  let rssBusy = false;
  let rssNewName = "";
  let rssJustMinted: RssTokenWithPlaintext | null = null;
  let rssError: string | null = null;

  async function loadRssTokens() {
    try {
      rssTokens = await listMyRssTokens();
    } finally {
      rssTokensLoaded = true;
    }
  }

  async function mintRssToken() {
    rssError = null;
    rssBusy = true;
    try {
      const minted = await createRssToken(rssNewName.trim() || "RSS");
      rssJustMinted = minted;
      rssNewName = "";
      await loadRssTokens();
    } catch (e) {
      rssError = e instanceof ApiError ? e.detail : "failed";
    } finally {
      rssBusy = false;
    }
  }

  async function doRevoke(id: string) {
    rssError = null;
    try {
      await revokeRssToken(id);
      rssTokens = rssTokens.filter((t) => t.id !== id);
    } catch (e) {
      rssError = e instanceof ApiError ? e.detail : "failed";
    }
  }

  function copyToClipboard(text: string) {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      void navigator.clipboard.writeText(text);
    }
  }

  type Kind = "account_security" | "mention" | "comment_reply";
  type Channel = "in_app" | "email" | "both" | "off";

  interface Pref {
    kind: string;
    channel: Channel;
    connector_id: string | null;
  }

  const KINDS: Kind[] = ["account_security", "mention", "comment_reply"];

  let prefs: Record<string, Channel> = {};
  let prefsLoaded = false;

  async function loadPrefs() {
    try {
      const r = await api<{ items: Pref[] }>("/api/me/notification-preferences");
      for (const p of r.items) prefs[p.kind] = p.channel;
    } finally {
      prefsLoaded = true;
    }
  }

  async function setPref(kind: Kind, channel: Channel) {
    prefs[kind] = channel;
    prefs = prefs;
    try {
      await api(`/api/me/notification-preferences/${kind}`, {
        method: "PUT",
        body: JSON.stringify({ channel }),
      });
    } catch {
      /* surface as a separate concern; minimal UI for now */
    }
  }

  function onPrefChange(kind: Kind, ev: Event) {
    const target = ev.currentTarget as HTMLSelectElement;
    void setPref(kind, target.value as Channel);
  }

  onMount(() => {
    void loadPrefs();
    void loadRssTokens();
  });

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

  <section class="card feeds">
    <h2>{$_("feeds.heading")}</h2>
    <p class="muted">{$_("feeds.description")}</p>

    {#if rssJustMinted}
      {@const minted = rssJustMinted}
      <aside class="just-minted" role="status">
        <p><strong>{$_("feeds.shown_once")}</strong></p>
        <ul>
          <li>
            <span>{$_("feeds.favorites")}</span>
            <code>{minted.favorites_url}</code>
            <button type="button" on:click={() => copyToClipboard(minted.favorites_url)}>
              {$_("feeds.copy")}
            </button>
          </li>
          <li>
            <span>{$_("feeds.recent")}</span>
            <code>{minted.recent_url}</code>
            <button type="button" on:click={() => copyToClipboard(minted.recent_url)}>
              {$_("feeds.copy")}
            </button>
          </li>
          <li>
            <span>{$_("feeds.everything")}</span>
            <code>{minted.everything_url}</code>
            <button type="button" on:click={() => copyToClipboard(minted.everything_url)}>
              {$_("feeds.copy")}
            </button>
          </li>
        </ul>
        <button type="button" on:click={() => (rssJustMinted = null)}>OK</button>
      </aside>
    {/if}

    <form on:submit|preventDefault={mintRssToken}>
      <label>
        <span>{$_("feeds.name_label")}</span>
        <input type="text" bind:value={rssNewName} disabled={rssBusy} placeholder="Podcast app" />
      </label>
      <button type="submit" disabled={rssBusy}>
        {$_("feeds.create")}
      </button>
      {#if rssError}<p class="error">{rssError}</p>{/if}
    </form>

    {#if rssTokensLoaded && rssTokens.length > 0}
      <ul class="token-list">
        {#each rssTokens as t (t.id)}
          <li>
            <strong>{t.name}</strong>
            <span class="muted">— {t.last_used_at ? `used ${t.last_used_at.slice(0, 10)}` : "unused"}</span>
            <button type="button" on:click={() => doRevoke(t.id)}>{$_("feeds.revoke")}</button>
          </li>
        {/each}
      </ul>
    {/if}
  </section>

  <section class="card prefs">
    <h2>{$_("settings.notifications")}</h2>
    {#if !prefsLoaded}
      <p>{$_("settings.loading")}</p>
    {:else}
      <dl>
        {#each KINDS as kind (kind)}
          <dt>{$_(`settings.notification_kinds.${kind}`)}</dt>
          <dd>
            <select
              value={prefs[kind] ?? "both"}
              on:change={(e) => onPrefChange(kind, e)}
              aria-label={$_(`settings.notification_kinds.${kind}`)}
            >
              <option value="in_app">{$_("settings.channel.in_app")}</option>
              <option value="email">{$_("settings.channel.email")}</option>
              <option value="both">{$_("settings.channel.both")}</option>
              <option value="off">{$_("settings.channel.off")}</option>
            </select>
          </dd>
        {/each}
      </dl>
    {/if}
  </section>
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
  .profile dl,
  .prefs dl {
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: var(--sp-2) var(--sp-3);
    margin: 0;
    align-items: center;
  }
  .profile dt,
  .prefs dt { color: var(--text-faint); }
  .profile dd,
  .prefs dd { margin: 0; }
  .prefs select {
    padding: var(--sp-1) var(--sp-2);
    background: var(--bg-base);
    border: 1px solid var(--border-default);
    border-radius: var(--r-sm);
    color: inherit;
    font: inherit;
  }
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
  .muted { color: var(--text-faint); font-size: var(--ts-sm); margin: 0; }
  .feeds form { display: grid; gap: var(--sp-2); }
  .feeds .token-list { list-style: none; padding: 0; margin: 0;
                        display: grid; gap: var(--sp-1); }
  .feeds .token-list li { display: flex; gap: var(--sp-2);
                          align-items: baseline; flex-wrap: wrap; }
  .feeds .token-list button { padding: var(--sp-1) var(--sp-2);
                              background: transparent; color: inherit;
                              border: 1px solid var(--border-default);
                              font-weight: 400; }
  .feeds .just-minted {
    padding: var(--sp-2); background: var(--bg-base);
    border: 1px dashed var(--accent); border-radius: var(--r-sm);
    display: grid; gap: var(--sp-2);
  }
  .feeds .just-minted ul { list-style: none; padding: 0; margin: 0;
                            display: grid; gap: var(--sp-1); }
  .feeds .just-minted li { display: grid;
                            grid-template-columns: max-content 1fr max-content;
                            gap: var(--sp-2); align-items: center; }
  .feeds .just-minted code {
    font-family: var(--font-mono); font-size: var(--ts-xs);
    overflow-wrap: anywhere;
  }
  @media (max-width: 600px) {
    .settings { padding: var(--sp-3); max-width: none; }
    .card { padding: var(--sp-3); }
    input { font-size: 16px; }  /* prevents iOS auto-zoom on focus */
    .profile dl, .prefs dl { grid-template-columns: 1fr; gap: var(--sp-1); }
    .feeds .just-minted li {
      grid-template-columns: 1fr;
      gap: var(--sp-1);
    }
  }
</style>
