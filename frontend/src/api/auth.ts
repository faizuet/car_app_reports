import { apiRequest, setToken } from "./client";
import type { TokenResponse, User } from "../types";

export async function signup(data: {
  username: string;
  email: string;
  password: string;
}): Promise<User> {
  return apiRequest<User>("/auth/signup", {
    method: "POST",
    body: JSON.stringify(data),
  }, false);
}

export async function login(data: {
  email: string;
  password: string;
}): Promise<TokenResponse> {
  const result = await apiRequest<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  }, false);
  setToken(result.access_token);
  return result;
}

export async function getProfile(): Promise<User> {
  return apiRequest<User>("/users/me");
}

export async function updateProfile(data: {
  username?: string;
  display_name?: string;
  email?: string;
  bio?: string;
  phone?: string;
}): Promise<User> {
  return apiRequest<User>("/users/me", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}
