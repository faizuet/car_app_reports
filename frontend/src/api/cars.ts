import { apiRequest, buildQuery } from "./client";
import type { Car, CursorPage } from "../types";

export async function listCars(limit = 10, cursor?: number): Promise<CursorPage<Car>> {
  return apiRequest<CursorPage<Car>>(
    `/cars/${buildQuery({ limit, cursor })}`
  );
}

export async function createCar(data: {
  name: string;
  year: number;
  make_id: number;
  car_model_name?: string;
  car_model_id?: number;
  category?: string;
}): Promise<Car> {
  return apiRequest<Car>("/cars/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateCar(
  id: number,
  data: {
    name?: string;
    year?: number;
    make_id?: number;
    car_model_name?: string;
    category?: string;
  }
): Promise<Car> {
  return apiRequest<Car>(`/cars/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteCar(id: number): Promise<void> {
  return apiRequest<void>(`/cars/${id}`, { method: "DELETE" });
}
