import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

export interface ConnectorRow {
  id: string;
  kind: string;
  name: string;
  enabled: boolean;
  scope_filter: Record<string, unknown>;
}

export const load: PageLoad = async ({ fetch }) => {
  const response = await fetch("/api/connectors");
  if (!response.ok) {
    throw error(response.status, "Failed to load connectors");
  }
  const body = (await response.json()) as { items: ConnectorRow[] };
  return { connectors: body.items };
};
