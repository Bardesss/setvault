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
