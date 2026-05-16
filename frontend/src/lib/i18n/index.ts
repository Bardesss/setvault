import { addMessages, init, getLocaleFromNavigator } from "svelte-i18n";
import en from "./locales/en.json";

let initialized = false;

export function setupI18n(): void {
  if (initialized) return;
  addMessages("en", en);
  init({ fallbackLocale: "en", initialLocale: getLocaleFromNavigator() ?? "en" });
  if (typeof window !== "undefined") (window as any).__i18n_initialized__ = true;
  initialized = true;
}
