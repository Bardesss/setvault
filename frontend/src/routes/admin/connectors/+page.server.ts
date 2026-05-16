import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export interface ConnectorRow {
  id: string;
  kind: string;
  name: string;
  enabled: boolean;
  scope_filter: Record<string, unknown>;
}

export const load: PageServerLoad = async ({ fetch, cookies }) => {
  if (!cookies.get("session")) {
    throw error(401, "Not authenticated");
  }
  const response = await fetch("/api/connectors");
  if (!response.ok) {
    throw error(response.status, "Failed to load connectors");
  }
  const body = (await response.json()) as { items: ConnectorRow[] };
  return { connectors: body.items };
};
