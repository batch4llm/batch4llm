import { api } from "./client";
import type { FileData } from "../types/FileData";

export const FilesAPI = {
    getAll: (): Promise<FileData[]> =>
        api.get("/files/").then(r => r.data),

    upload: (file: File, tags?: string[]): Promise<FileData> => {
        const formData = new FormData();
        formData.append("file", file);

        tags?.forEach(tag => formData.append("tags", tag));

        return api.post("/files/upload", formData, {
            headers: { "Content-Type": "multipart/form-data" },
        }).then(r => r.data);
    },

    delete: (file_id: number): Promise<void> =>
        api.delete(`/files/delete/${file_id}`),

    download: (file_id: number): Promise<Blob> =>
        api.get(`/files/download/${file_id}`, {
            responseType: "blob",
        }).then(r => r.data),

    getFileTags: (): Promise<string[]> =>
        api.get("/files/tags").then(r => r.data),

    getFilesByTag: (tag: string): Promise<FileData[]> =>
        api.get(`/files/by-tag/${tag}`).then(r => r.data),

    getUrl: (file_id: number): Promise<string> =>
        api.get(`/files/${file_id}/url`).then(r => r.data.url),
};
