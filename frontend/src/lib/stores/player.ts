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

// Seek bridge: the active <Player> registers a handler that drives its
// wavesurfer instance. Other components (e.g. the tracklist) call seekTo()
// to move the playhead without holding a wavesurfer reference themselves.
let seekHandler: ((seconds: number) => void) | null = null;

export function registerSeek(fn: ((seconds: number) => void) | null): void {
  seekHandler = fn;
}

export function seekTo(seconds: number): void {
  seekHandler?.(seconds);
}
