<script lang="ts">
  import TabStrip from "./TabStrip.svelte";
  import CommentThread from "./CommentThread.svelte";
  import BookmarkButton from "./BookmarkButton.svelte";
  import PrivateNotesPanel from "./PrivateNotesPanel.svelte";

  export let slug: string;

  // Honest-now tabs: the three engagement surfaces that actually exist.
  // (Mockup's About/Artist/Activity tabs are deferred to a later phase.)
  let active = "comments";
  const tabs = [
    { id: "comments", label: "Comments" },
    { id: "bookmarks", label: "Bookmarks" },
    { id: "notes", label: "Notes" },
  ];
</script>

<aside class="side-panel" aria-label="Set engagement">
  <div class="side-panel-tabs">
    <TabStrip {tabs} bind:active />
  </div>
  <div class="side-content">
    {#if active === "comments"}
      <div class="side-section" role="tabpanel" aria-label="Comments">
        <CommentThread {slug} flat />
      </div>
    {:else if active === "bookmarks"}
      <div class="side-section" role="tabpanel" aria-label="Bookmarks">
        <h4>Your bookmarks</h4>
        <BookmarkButton {slug} flat />
      </div>
    {:else if active === "notes"}
      <div class="side-section" role="tabpanel" aria-label="Notes">
        <h4>Private notes</h4>
        <PrivateNotesPanel {slug} flat />
      </div>
    {/if}
  </div>
</aside>
