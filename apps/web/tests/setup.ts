import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

afterEach(() => cleanup());

Object.defineProperty(window, "scrollTo", {
  configurable: true,
  value: vi.fn(),
});

Object.defineProperty(HTMLCanvasElement.prototype, "getContext", {
  configurable: true,
  value: vi.fn(() => ({
    beginPath: vi.fn(),
    clearRect: vi.fn(),
    lineTo: vi.fn(),
    moveTo: vi.fn(),
    scale: vi.fn(),
    stroke: vi.fn(),
    set fillStyle(_value: string) {},
    set lineWidth(_value: number) {},
    set shadowBlur(_value: number) {},
    set shadowColor(_value: string) {},
    set strokeStyle(_value: string) {},
  })),
});

Object.defineProperty(HTMLCanvasElement.prototype, "getBoundingClientRect", {
  configurable: true,
  value: () => ({
    width: 640,
    height: 160,
    top: 0,
    left: 0,
    right: 640,
    bottom: 160,
    x: 0,
    y: 0,
    toJSON: () => ({}),
  }),
});
