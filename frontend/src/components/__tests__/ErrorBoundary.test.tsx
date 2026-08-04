// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import ErrorBoundary from "../ErrorBoundary";

function Boom(): React.ReactElement {
  throw new Error("عناصر پیدا نشد");
}

describe("ErrorBoundary", () => {
  it("shows a readable message instead of blanking the page", () => {
    // React logs the caught error; silence it for a clean test run.
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    render(
      <ErrorBoundary>
        <Boom />
      </ErrorBoundary>,
    );
    expect(screen.getByText("این بخش با خطا مواجه شد")).toBeTruthy();
    expect(screen.getByText("عناصر پیدا نشد")).toBeTruthy();
    spy.mockRestore();
  });

  it("renders children when nothing throws", () => {
    render(
      <ErrorBoundary>
        <p>سالم</p>
      </ErrorBoundary>,
    );
    expect(screen.getByText("سالم")).toBeTruthy();
  });
});
