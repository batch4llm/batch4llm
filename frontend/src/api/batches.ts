import { api } from "./client";
import type { Batch, BatchStartRequest } from "../types/Batch";
import type { BatchFileOverview, BatchFileDetail } from "../types/BatchFile.ts";
import type { BatchTaskDetail } from "../types/BatchTask.ts";
import type { BatchLogEntry } from "../types/BatchLogEntry.ts";



export const BatchesAPI = {
    getAll: (): Promise<Batch[]> => api.get("/batches/").then(r => r.data),
    getLogEntries: (id: number, afterId?: number): Promise<BatchLogEntry[]> => {
        const params = afterId !== undefined ? { after_id: afterId } : {};
        return api.get(`/batches/log/${id}`, { params }).then(r => r.data);
    },
    getById: (id: number): Promise<Batch> => api.get(`/batches/${id}`).then(r => r.data),

    // ── Granular batch detail (file overview → file detail → task detail) ──
    getBatchFiles: (batchId: number): Promise<BatchFileOverview[]> =>
        api.get(`/batches/${batchId}/files`).then(r => r.data),
    getBatchFile: (fileId: number): Promise<BatchFileDetail> =>
        api.get(`/batches/files/${fileId}`).then(r => r.data),
    getBatchTask: (taskId: number): Promise<BatchTaskDetail> =>
        api.get(`/batches/tasks/${taskId}`).then(r => r.data),

    create: (payload: BatchStartRequest): Promise<Batch> => api.post("/batches/start", payload).then(r => r.data),
    stop: (id: number): Promise<Batch> => api.post(`/batches/stop/${id}`).then(r => r.data),
    archive: (id: number, archived = true): Promise<Batch> =>
        api.patch(`/batches/${id}/archive`, null, { params: { archived } }).then(r => r.data),
};
