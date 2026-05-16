import { writable } from "svelte/store";
import type { SetDetail } from "$lib/api/sets";

export interface PlayerState {
  set: SetDetail | null;
  playing: boolean;
  position: number;
  duration: number;
}

export const player = writable<PlayerState>({
  set: null,
  playing: false,
  position: 0,
  duration: 0,
});
