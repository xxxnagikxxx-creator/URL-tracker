import type { LinkDetails, LinkSummary, TelegramAuthPayload, User } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type ApiError = {
  detail?: string;
};

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let message = "Request failed";

    try {
      const data = (await response.json()) as ApiError;
      message = data.detail ?? message;
    } catch {
      message = response.statusText || message;
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export const api = {
  loginWithTelegram(payload: TelegramAuthPayload) {
    return request<User>("/auth/telegram", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  getCurrentUser() {
    return request<User>("/auth/get_full_user");
  },

  logout() {
    return request<{ status: string; message: string }>("/auth/logout", {
      method: "POST",
    });
  },

  getLinks() {
    return request<{ links: LinkSummary[] }>("/live_checker/get_links");
  },

  createLink(url: string) {
    return request<LinkDetails>("/live_checker/create_link", {
      method: "POST",
      body: JSON.stringify({ url }),
    });
  },

  getLink(linkId: number) {
    return request<LinkDetails>(`/live_checker/get_link/${linkId}`);
  },

  deleteLink(linkId: number) {
    return request<{ status: string; message: string }>(`/live_checker/delete_link/${linkId}`, {
      method: "DELETE",
    });
  },
};
