import { error as kitError } from "@sveltejs/kit";
import type { PageLoad } from "./$types";

interface EmbedSet {
  slug: string;
  title: string;
  duration_seconds: number | null;
  audio_url: string;
  waveform_url: string | null;
  tracklist: {
    position: number;
    start_seconds: number | null;
    label: string | null;
  }[];
}

export const load: PageLoad = async ({ params, fetch }) => {
  const res = await fetch(`/api/sets/${params.slug}/embed`);
  if (!res.ok) throw kitError(res.status, "not found");
  const set = (await res.json()) as EmbedSet;
  return { set };
};

// Runtime data — don't pre-render.
export const ssr = false;
