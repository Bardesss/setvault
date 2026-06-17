import { describe, it, expect } from "vitest";
import { isPublicRoute } from "./routes";

describe("isPublicRoute", () => {
  it("treats the login and setup pages as public", () => {
    expect(isPublicRoute("/login")).toBe(true);
    expect(isPublicRoute("/setup")).toBe(true);
  });

  it("treats embed / invite / reset subtrees as public", () => {
    expect(isPublicRoute("/embed/abc123")).toBe(true);
    expect(isPublicRoute("/invite/tok")).toBe(true);
    expect(isPublicRoute("/reset/tok")).toBe(true);
  });

  it("treats app routes as protected", () => {
    expect(isPublicRoute("/")).toBe(false);
    expect(isPublicRoute("/sets")).toBe(false);
    expect(isPublicRoute("/me/downloads")).toBe(false);
    expect(isPublicRoute("/admin/users")).toBe(false);
  });
});
