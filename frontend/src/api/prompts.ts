import { api } from "./client";
import type { Prompt } from "../types/Prompt";



export const PromptsAPI = {
    getAll: (): Promise<Prompt[]> => api.get("/prompts/").then(r => r.data),
    create: (payload: Partial<Prompt>): Promise<Prompt> => api.post("/prompts/add", payload).then(r => r.data),
    delete: (id: number): Promise<Prompt> => api.delete(`/prompts/delete/${id}`).then(r => r.data),
};
