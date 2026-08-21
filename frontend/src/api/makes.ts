import { apiRequest } from "./client";
import type { Make, CarModel } from "../types";

export async function listMakes(): Promise<Make[]> {
  return apiRequest<Make[]>("/makes/");
}

export async function listModelsForMake(makeId: number): Promise<CarModel[]> {
  return apiRequest<CarModel[]>(`/makes/${makeId}/models`);
}
