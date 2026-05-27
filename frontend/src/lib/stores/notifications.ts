import { writable } from "svelte/store";
import type { InAppNotification } from "../api/notifications";

interface State {
  items: InAppNotification[];
  unread_count: number;
}

export const notifications = writable<State>({ items: [], unread_count: 0 });
