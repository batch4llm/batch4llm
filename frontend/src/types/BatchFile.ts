import type { BatchTaskPreview, BatchTaskStatus } from "./BatchTask.ts";

/** Lightweight file entry for the batch overview (no output, no tasks). */
export interface BatchFileOverview {
    id: number;
    batch_id: number;
    file_id: number;
    name: string;
    status: BatchTaskStatus;
    task_count: number;
    completed_task_count: number;
    created_at: string;
    updated_at: string;
}

/** A file with its task previews and aggregated cost/token totals. */
export interface BatchFileDetail {
    id: number;
    batch_id: number;
    file_id: number;
    name: string;
    status: BatchTaskStatus;
    batch_tasks: BatchTaskPreview[];
    input_token_count: number;
    output_token_count: number;
    costs_in_usd: number;
    created_at: string;
    updated_at: string;
}
