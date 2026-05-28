import { api } from "./client";

export interface RssToken {
  id: string;
  name: string;
  favorites_url: string;
  recent_url: string;
  everything_url: string;
  created_at: string;
  last_used_at: string | null;
}

export interface RssTokenWithPlaintext extends RssToken {
  token: string;
}

interface RssTokensList {
  items: RssToken[];
}

export const listMyRssTokens = async (): Promise<RssToken[]> => {
  const r = await api<RssTokensList>("/api/me/rss-tokens");
  return r.items;
};

export const createRssToken = (name: string) =>
  api<RssTokenWithPlaintext>("/api/me/rss-tokens", {
    method: "POST",
    body: JSON.stringify({ name }),
  });

export const revokeRssToken = (id: string) =>
  api<void>(`/api/me/rss-tokens/${encodeURIComponent(id)}`, { method: "DELETE" });
