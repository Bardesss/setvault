import { api } from "./client";

export interface SourceCandidate {
  source_kind: string;
  external_id: string;
  title: string;
  uploader: string | null;
  duration_seconds: number | null;
  thumbnail_url: string | null;
  webpage_url: string;
  already_in_library: boolean;
}

export interface SourceState {
  kind: string;
  name: string;
  enabled: boolean;
  state: string;
  consecutive_failures: number;
  last_error: string | null;
}

export async function searchSources(
  q: string,
  source = "youtube",
): Promise<SourceCandidate[]> {
  const { items } = await api<{ items: SourceCandidate[] }>(
    "/api/ingest-sources/search",
    {
      method: "POST",
      body: JSON.stringify({ q, source }),
    },
  );
  return items;
}

export async function listSources(): Promise<SourceState[]> {
  const { items } = await api<{ items: SourceState[] }>(
    "/api/admin/ingest-sources",
  );
  return items;
}

export const setSourceEnabled = (kind: string, enabled: boolean) =>
  api<SourceState>(`/api/admin/ingest-sources/${encodeURIComponent(kind)}`, {
    method: "PUT",
    body: JSON.stringify({ enabled }),
  });
