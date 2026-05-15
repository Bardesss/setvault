import adapter from "@sveltejs/adapter-static";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

export default {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({ pages: "../apps/web/src/setvault_web/static", fallback: "index.html" }),
    alias: { $lib: "src/lib" },
  },
};
