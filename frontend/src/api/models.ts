import { api } from "./client";
import type { ModelInfo } from "../types/Model";

export const ModelsAPI = {
    getAll: (): Promise<ModelInfo[]> => api.get("/models/").then(r => r.data),
};
