import type {BatchTask} from "./BatchTask.ts";

export interface BatchFile {
    id: number;
    batch_id: number;
    file_id: number;
    name: string;
    status: "QUEUED" | "RUNNING" | "FAILED" | "COMPLETED";
    input_token_count: number;
    output_token_count: number;
    costs_in_usd?: number;
    created_at: string;
    updated_at: string;
    batch_tasks: BatchTask[];
}
