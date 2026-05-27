import { api } from "./client";

export interface Bookmark {
  id: string;
  live_set_id: string;
  live_set_slug: string | null;
  live_set_title: string | null;
  position_seconds: number | null;
  label: string | null;
  created_at: string;
}

interface BookmarksList {
  items: Bookmark[];
}

export const listForSet = async (slug: string): Promise<Bookmark[]> => {
  const r = await api<BookmarksList>(`/api/sets/${encodeURIComponent(slug)}/bookmarks`);
  return r.items;
};

export const createBookmark = (
  slug: string,
  position_seconds: number | null,
  label: string | null,
) =>
  api<Bookmark>(`/api/sets/${encodeURIComponent(slug)}/bookmarks`, {
    method: "POST",
    body: JSON.stringify({ position_seconds, label }),
  });

export const deleteBookmark = (slug: string, id: string) =>
  api<void>(`/api/sets/${encodeURIComponent(slug)}/bookmarks/${id}`, {
    method: "DELETE",
  });

export const listMyBookmarks = async (): Promise<Bookmark[]> => {
  const r = await api<BookmarksList>("/api/me/bookmarks");
  return r.items;
};
