import { writable } from "svelte/store";
import type { CurrentUser } from "$lib/api/auth";

export const session = writable<CurrentUser | null>(null);
