import { describe, it, expect } from "vitest";
import { clampRate, formatTime, pickNext, pickPrev } from "./audio";

const entries = [
  { start_seconds: 0 },
  { start_seconds: 60 },
  { start_seconds: 120 },
] as Array<{ start_seconds: number }>;

describe("clampRate", () => {
  it("clamps to 0.5..2 and rounds to 2dp", () => {
    expect(clampRate(0.1)).toBe(0.5);
    expect(clampRate(3)).toBe(2);
    expect(clampRate(1.234)).toBe(1.23);
    expect(clampRate(NaN)).toBe(1);
  });
});

describe("formatTime", () => {
  it("formats mm:ss and h:mm:ss", () => {
    expect(formatTime(0)).toBe("0:00");
    expect(formatTime(75)).toBe("1:15");
    expect(formatTime(3661)).toBe("1:01:01");
    expect(formatTime(-5)).toBe("0:00");
  });
});

describe("pickNext / pickPrev", () => {
  it("next returns the first entry after position, else null", () => {
    expect(pickNext(entries, 10)).toBe(60);
    expect(pickNext(entries, 130)).toBeNull();
  });
  it("prev returns the entry before position with a 2s rewind zone", () => {
    expect(pickPrev(entries, 130)).toBe(120);
    expect(pickPrev(entries, 61)).toBe(0); // within 2s of 60 -> still 60? 61-2=59 < 60 so prev is 0
    expect(pickPrev(entries, 5)).toBe(0);
  });
});
