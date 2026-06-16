import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

export interface JobRow {
  id: string;
  kind: string;
  status: string;
  progress_pct: number;
  message: string | null;
  created_at: string;
  finished_at: string | null;
}

export const load: PageLoad = async ({ fetch }) => {
  const response = await fetch("/api/admin/jobs");
  if (!response.ok) {
    throw error(response.status, "Failed to load jobs");
  }
  const body = (await response.json()) as { items: JobRow[] };
  return { jobs: body.items };
};
