import { api } from "./client";

export interface RipJob {
  id: string;
  live_set_id: string | null;
  live_set_slug: string | null;
  source_url: string;
  source_external_id: string | null;
  source_platform: string | null;
  status: string;
  progress_pct: number;
  message: string | null;
  error_text: string | null;
  probed_metadata: Record<string, unknown>;
  ytdlp_version: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

interface RipJobsList {
  items: RipJob[];
}

/** Terminal rip statuses — a job in one of these is done and won't change. */
const TERMINAL_STATUSES = new Set(["ready", "failed"]);

/** True while a rip is still in flight (queued/probing/downloading/…), i.e.
 * worth polling for updates. */
export const isRipActive = (job: RipJob): boolean =>
  !TERMINAL_STATUSES.has(job.status);

/** True if any job in the list is still in flight — drives whether to keep
 * polling the rip list. */
export const hasActiveRips = (jobs: RipJob[]): boolean => jobs.some(isRipActive);

/** True if a rip can be retried — only failed jobs (re-submitting the same URL
 * is allowed because dedup explicitly excludes failed jobs). */
export const canRetry = (job: RipJob): boolean => job.status === "failed";

export const submitUrl = (url: string) =>
  api<RipJob>("/api/sets/url-rip", {
    method: "POST",
    body: JSON.stringify({ url }),
  });

export const listMyRipJobs = async (status?: "active" | "all"): Promise<RipJob[]> => {
  const qs = status === "active" ? "?status=active" : "";
  const r = await api<RipJobsList>(`/api/me/rip-jobs${qs}`);
  return r.items;
};

/** Remove one rip from the caller's history. */
export const deleteRipJob = (id: string) =>
  api<void>(`/api/me/rip-jobs/${id}`, { method: "DELETE" });

/** Clear the caller's finished (ready/failed) rips; in-progress jobs are kept. */
export const clearFinishedRipJobs = () =>
  api<void>("/api/me/rip-jobs", { method: "DELETE" });
