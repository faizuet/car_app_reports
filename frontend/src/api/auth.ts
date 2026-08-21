import { apiRequest, setToken } from "./client";
import type { TokenResponse } from "../types";

export async function signup(data: {
  username: string;
  email: string;
  password: string;
}) {
  return apiRequest("/auth/signup", {
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
