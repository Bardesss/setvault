import { api } from "./client";

export interface PrivateNote {
  body_md: string;
  body_html: string;
  updated_at: string | null;
}

export const getNote = (slug: string) =>
  api<PrivateNote>(`/api/sets/${encodeURIComponent(slug)}/note`);

export const saveNote = (slug: string, body_md: string) =>
  api<PrivateNote>(`/api/sets/${encodeURIComponent(slug)}/note`, {
    method: "PUT",
    body: JSON.stringify({ body_md }),
  });
