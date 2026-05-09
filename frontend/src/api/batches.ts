import { api } from "./client";
import type { Batch } from "../types/Batch";
import type {BatchFile} from "../types/BatchFile.ts";
import type {BatchLogEntry} from "../types/BatchLogEntry.ts";



export const BatchesAPI = {
    getAll: (): Promise<Batch[]> => api.get("/batches/").then(r => r.data),
    getLogEntries: (id: number, afterId?: number): Promise<BatchLogEntry[]> => {
        const params = afterId !== undefined ? { after_id: afterId } : {};
        return api.get(`/batches/log/${id}`, { params }).then(r => r.data);
    },
    getById: (id: number): Promise<Batch> => api.get(`/batches/${id}`).then(r => r.data),
    getBatchFilesById: (id: number): Promise<BatchFile[]> => api.get(`/batches/files/${id}`).then(r => r.data),
    create: (payload: Partial<Batch>): Promise<Batch> => api.post("/batches/start", payload).then(r => r.data),
    stop: (id: number): Promise<Batch> => api.post(`/batches/stop/${id}`).then(r => r.data),
};
