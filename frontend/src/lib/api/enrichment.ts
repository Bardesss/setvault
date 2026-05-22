import { api } from "./client";

export interface ResolveCandidate {
  title: string;
  artist_name: string;
  confidence: number;
  source_kind: string;
  external_ids: Record<string, string>;
}

export interface BulkResolveRow {
  entry_id: string;
  candidates: ResolveCandidate[];
}

const entryBase = (slug: string, entryId: string) =>
  `/api/sets/${encodeURIComponent(slug)}/tracklist/entries/${entryId}`;

export async function resolveEntry(
  slug: string,
  entryId: string,
): Promise<ResolveCandidate[]> {
  const r = await api<{ entry_id: string; candidates: ResolveCandidate[] }>(
    `${entryBase(slug, entryId)}/resolve`,
    { method: "POST" },
  );
  return r.candidates;
}

export const acceptCandidate = (
  slug: string,
  entryId: string,
  cand: ResolveCandidate,
  confirmedViaAcoustid = false,
) =>
  api<{ track_id: string; status: string }>(
    `${entryBase(slug, entryId)}/resolve/accept`,
    {
      method: "POST",
      body: JSON.stringify({
        title: cand.title,
        artist_name: cand.artist_name,
        external_ids: cand.external_ids,
        confirmed_via_acoustid: confirmedViaAcoustid,
      }),
    },
  );

export async function idThis(slug: string, entryId: string): Promise<ResolveCandidate[]> {
  const r = await api<{ entry_id: string; candidates: ResolveCandidate[] }>(
    `${entryBase(slug, entryId)}/id-this`,
    { method: "POST" },
  );
  return r.candidates;
}

export async function bulkResolve(slug: string): Promise<BulkResolveRow[]> {
  const r = await api<{ results: BulkResolveRow[] }>(
    `/api/sets/${encodeURIComponent(slug)}/tracklist/bulk-resolve`,
    { method: "POST" },
  );
  return r.results;
}
