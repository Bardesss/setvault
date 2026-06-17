import { describe, it, expect } from "vitest";
import { isRipActive, hasActiveRips, canRetry, replaceRipJob, type RipJob } from "./url_rip";

function job(status: string): RipJob {
  return {
    id: status,
    live_set_id: null,
    live_set_slug: null,
    source_url: "https://example.test/x",
    source_external_id: null,
    source_platform: null,
    status,
    progress_pct: 0,
    message: null,
    error_text: null,
    probed_metadata: {},
    ytdlp_version: null,
    created_at: "2026-01-01T00:00:00Z",
    started_at: null,
    finished_at: null,
  };
}

describe("isRipActive", () => {
  it("is false for terminal states (ready, failed)", () => {
    expect(isRipActive(job("ready"))).toBe(false);
    expect(isRipActive(job("failed"))).toBe(false);
  });

  it("is true while in flight (queued, probing, downloading, …)", () => {
    expect(isRipActive(job("queued"))).toBe(true);
    expect(isRipActive(job("downloading"))).toBe(true);
    expect(isRipActive(job("transcoding"))).toBe(true);
  });
});

describe("hasActiveRips", () => {
  it("is true when any job is still in flight", () => {
    expect(hasActiveRips([job("ready"), job("downloading")])).toBe(true);
  });

  it("is false when every job is terminal", () => {
    expect(hasActiveRips([job("ready"), job("failed")])).toBe(false);
  });

  it("is false for an empty list", () => {
    expect(hasActiveRips([])).toBe(false);
  });
});

describe("canRetry", () => {
  it("is true only for failed jobs", () => {
    expect(canRetry(job("failed"))).toBe(true);
  });

  it("is false for terminal-success and in-flight jobs", () => {
    expect(canRetry(job("ready"))).toBe(false);
    expect(canRetry(job("downloading"))).toBe(false);
    expect(canRetry(job("queued"))).toBe(false);
  });
});

describe("replaceRipJob", () => {
  it("drops the retried (old) job and puts the fresh one at the front", () => {
    const failed = { ...job("failed"), id: "old" };
    const other = { ...job("ready"), id: "other" };
    const fresh = { ...job("queued"), id: "new" };

    const result = replaceRipJob([failed, other], "old", fresh);

    expect(result.map((j) => j.id)).toEqual(["new", "other"]);
    // the old failed row is gone — Retry shows one row, not two
    expect(result.some((j) => j.id === "old")).toBe(false);
  });

  it("still prepends the fresh job when the old id is not present", () => {
    const other = { ...job("ready"), id: "other" };
    const fresh = { ...job("queued"), id: "new" };

    expect(replaceRipJob([other], "missing", fresh).map((j) => j.id)).toEqual([
      "new",
      "other",
    ]);
  });
});
