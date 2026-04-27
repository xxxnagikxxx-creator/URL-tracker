/// <reference types="vite/client" />

import type { TelegramAuthPayload } from "./types";

declare global {
  interface Window {
    onTelegramAuth?: (user: TelegramAuthPayload) => void;
  }
}

export {};
