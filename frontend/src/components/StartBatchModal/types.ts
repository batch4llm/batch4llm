export type ViewId = "main" | "model" | "files" | "filereader" | "sampleoutput" | "prompt";

export type FileMode = "upload" | "reader";

export interface ApiParams {
    top_p?: number;
    frequency_penalty?: number;
    presence_penalty?: number;
    max_tokens?: number;
    seed?: number;
}

export type InvalidField = "model" | "files" | "prompt" | "filereader" | "schedule";
