import { api } from "./client";


export const PipelineAPI = {
    getEngines: (): Promise<string[]> => api.get("/pipeline/engines").then(r => r.data),
    getFileReaders: (): Promise<string[]> => api.get("/pipeline/file_readers").then(r => r.data),
};
