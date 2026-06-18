import { api } from "./client";
import type { EntityKind } from "./catalog";

export interface EntityRow { id: string; name: string; slug: string; ref_count: number; }

export const listEntities = async (kind: EntityKind): Promise<EntityRow[]> =>
  (await api<{ items: EntityRow[] }>(`/api/admin/catalog/${kind}`)).items;

export const listDuplicates = async (kind: EntityKind): Promise<EntityRow[][]> =>
  (await api<{ clusters: EntityRow[][] }>(`/api/admin/catalog/${kind}/duplicates`)).clusters;

export const mergeEntities = (kind: EntityKind, loserId: string, survivorId: string, dryRun = false) =>
  api<unknown>(`/api/catalog/${kind}/${loserId}/merge${dryRun ? "?dry_run=1" : ""}`,
    { method: "POST", body: JSON.stringify({ survivor_id: survivorId }) });

export const unmergeEntity = (kind: EntityKind, loserId: string) =>
  api<void>(`/api/catalog/${kind}/${loserId}/unmerge`, { method: "POST" });

export const deleteEntity = (kind: EntityKind, slug: string) =>
  api<void>(`/api/catalog/${kind}/${slug}`, { method: "DELETE" });

export const enrichArtist = (slug: string) =>
  api<{ written: string[] }>(`/api/catalog/artists/${slug}/enrich`, { method: "POST" });
