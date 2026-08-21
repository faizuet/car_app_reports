export interface Make {
  id: number;
  name: string;
}

export interface CarModel {
  id: number;
  name: string;
  make: Make;
}

export interface User {
  id: number;
  username: string;
  email: string;
  display_name: string | null;
  bio: string | null;
  phone: string | null;
  profile_image: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface CarReport {
  id: number;
  name: string;
  year: number;
  make: string;
  model: string;
  category: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface CursorPage<T> {
  total: number;
  items: T[];
  next_cursor: number | null;
}

export interface ReportFilters {
  make?: string;
  model?: string;
  year?: string;
  date_from?: string;
  date_to?: string;
  limit?: number;
  cursor?: number;
}

export interface Car {
  id: number;
  name: string;
  year: number;
  category: string | null;
  car_model: {
    id: number;
    name: string;
    make: { id: number; name: string };
  };
  created_at: string;
  updated_at: string | null;
  full_name?: string;
}

export interface ApiError {
  detail: string | { msg: string; type: string }[];
}
