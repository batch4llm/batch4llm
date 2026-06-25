export interface LlmRequest {
    id: number;
    batch_task_id: number;
    status: "QUEUED" | "RUNNING" | "FAILED" | "COMPLETED";
    output?: string;
    input_token_count?: number;
    output_token_count?: number;
    costs_in_usd?: number;
    created_at: string;
    updated_at: string;
    started_at?: string;
    stopped_at?: string;
}

export interface BatchTask {
    id: number;
    batch_id: number;
    batch_file_id: number;
    file_id: number;
    status: "QUEUED" | "RUNNING" | "FAILED" | "COMPLETED";
    prompt_marker: string;
    depends_on_batch_task_id?: number;
    output?: string;
    input_token_count?: number;
    output_token_count?: number;
    costs_in_usd?: number;
    llm_requests?: LlmRequest[];
    created_at: string;
    updated_at: string;
}
