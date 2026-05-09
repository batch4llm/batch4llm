export interface BatchTask {
    id: number;
    batch_id: number;
    batch_file_id: number;
    file_id: number;
    status: "QUEUED" | "RUNNING" | "FAILED" | "COMPLETED";
    prompt_marker: string;
    output: string;
    input_token_count: number;
    output_token_count: number;
    seed?: string;
    costs_in_usd?: number;
    created_at: string;
    updated_at: string;
}