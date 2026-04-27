export type User = {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string;
  last_name: string | null;
  photo_url: string | null;
  created_at: string;
  updated_at: string;
};

export type LinkSummary = {
  id: number;
  url: string;
};

export type LinkCheck = {
  id: number;
  link_id: number;
  status_code: number;
  response_time: number;
  created_at: string;
};

export type LinkDetails = {
  id: number;
  url: string;
  telegram_id: number;
  created_at: string;
  checks: LinkCheck[];
};

export type TelegramAuthPayload = {
  id: number;
  first_name: string;
  auth_date: number;
  hash: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
};
