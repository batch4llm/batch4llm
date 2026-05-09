import { api } from "./client";

export const ExportAPI = {
    exportBatches: (mode: string, batchIds: number[]) => {
        const params = new URLSearchParams();
        params.append("mode", mode);
        batchIds.forEach(id => params.append("batch_ids", id.toString()));

        return api.get(`/export/batches?${params.toString()}`, {
            responseType: "blob",
        });
    },
};
