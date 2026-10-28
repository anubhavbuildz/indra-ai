import { it, expect, vi } from "vitest";
import { cn, findingsFromReport, severityCounts, formatDate, relativeTime, getErrorMessage, titleCase } from "./lib/utils";
it("UNIT-028 handles malformed findings and unknown severity", () => {
  expect(findingsFromReport(null)).toEqual([]); expect(findingsFromReport({findings: {}})).toEqual([]);
  expect(findingsFromReport({findings: [1]})).toEqual([1]);
  expect(severityCounts([{severity: "high"}, {severity: "unknown"}, null])).toEqual({CRITICAL: 0, HIGH: 1, MEDIUM: 0, LOW: 0});
});
it("UNIT-028 formats dates, times, errors, names and classes", () => {
  vi.spyOn(Date, "now").mockReturnValue(Date.parse("2026-01-01T00:00:00Z"));
  expect(formatDate(null)).toBe("Unknown date"); expect(formatDate("invalid")).toBe("Unknown date");
  expect(formatDate("2026-01-01T00:00:00Z")).toContain("2026");
  expect(relativeTime("invalid")).toBe("Unknown time"); expect(relativeTime("2026-01-01T00:00:00Z")).toBe("now");
  expect(relativeTime("2025-12-31T00:00:00Z")).toBe("yesterday");
  expect(getErrorMessage("error")).toBe("error"); expect(getErrorMessage(new Error("bad"))).toBe("bad");
  expect(getErrorMessage({})).toBe("An unexpected error occurred.");
  expect(titleCase("cloud_audit-test")).toBe("Cloud Audit Test"); expect(cn("p-2", "p-4")).toBe("p-4");
});
