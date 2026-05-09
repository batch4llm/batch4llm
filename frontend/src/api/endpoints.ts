import { api } from "./client";
import type { Endpoint } from "../types/Endpoint";



export const EndpointsAPI = {
    getAll: (): Promise<Endpoint[]> => api.get("/endpoints/").then(r => r.data),
    create: (payload: Partial<Endpoint>): Promise<Endpoint> => api.post("/endpoints/add", payload).then(r => r.data),
    delete: (endpoint_id: number): Promise<Endpoint> => api.delete(`/endpoints/delete/${endpoint_id}`).then(r => r.data),
    getModels: (endpoint_id: number): Promise<string[]> => api.get(`/endpoints/models/${endpoint_id}`).then(r => r.data),
    test: (payload: Partial<Endpoint>): Promise<{ success: boolean; error?: string }> => api.post("/endpoints/test", payload).then(r => r.data),
};
