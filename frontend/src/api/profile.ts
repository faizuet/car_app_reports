import { apiRequest } from "./client";
import type { User } from "../types";

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

export async function changePassword(data: {
  current_password: string;
  new_password: string;
}): Promise<User> {
  return apiRequest<User>("/users/me/password", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function uploadAvatar(file: File): Promise<User> {
  const formData = new FormData();
  formData.append("file", file);
  return apiRequest<User>("/users/me/avatar", {
    method: "POST",
    body: formData,
  });
}

export async function removeAvatar(): Promise<User> {
  return apiRequest<User>("/users/me/avatar", { method: "DELETE" });
}
