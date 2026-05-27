import { api } from "./client";

export interface InAppNotification {
  id: string;
  kind: string;
  subject_type: string;
  subject_id: string;
  payload: Record<string, unknown>;
  read_at: string | null;
  created_at: string;
}

export interface NotificationsList {
  items: InAppNotification[];
  unread_count: number;
}

export const listNotifications = (unread = false) =>
  api<NotificationsList>(`/api/me/notifications${unread ? "?unread=true" : ""}`);

export const markRead = (id: string) =>
  api<void>(`/api/me/notifications/${id}/read`, { method: "POST" });

export const readAll = () =>
  api<void>("/api/me/notifications/read-all", { method: "POST" });
