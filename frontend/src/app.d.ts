declare global {
  namespace App {
    interface Locals { user: import("$lib/api/auth").CurrentUser | null }
    interface PageData { user: import("$lib/api/auth").CurrentUser | null }
  }
}
export {};
