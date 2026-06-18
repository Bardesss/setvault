import type { PageLoad } from "./$types";
import { listEntities, listDuplicates, type EntityRow } from "$lib/api/catalog_admin";
import type { EntityKind } from "$lib/api/catalog";

export const ssr = false;

export const load: PageLoad = async ({ url }) => {
  const kind = (url.searchParams.get("kind") as EntityKind) || "artists";
  const [items, clusters] = await Promise.all([listEntities(kind), listDuplicates(kind)]);
  return { kind, items, clusters } as { kind: EntityKind; items: EntityRow[]; clusters: EntityRow[][] };
};
