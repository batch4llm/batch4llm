export type BatchTaskStatus = "QUEUED" | "RUNNING" | "FAILED" | "COMPLETED";

/** One task as shown in a file's task list (output truncated to a preview). */
export interface BatchTaskPreview {
    id: number;
    batch_file_id: number;
    status: BatchTaskStatus;
    prompt_marker?: string;
    depends_on_batch_task_id?: number;
    output_preview?: string;
    output_truncated: boolean;
    retry_count: number;
    input_token_count?: number;
    output_token_count?: number;
    costs_in_usd?: number;
    started_at?: string;
    stopped_at?: string;
    created_at: string;
    updated_at: string;
}

/** One LLM attempt (retry) of a task. Failed attempts carry no output.
 *  `reason` is a placeholder until the backend carries a dedicated error
 *  field on the request. */
export interface LlmAttempt {
    id: number;
    status: BatchTaskStatus;
    output?: string | null;
    reason?: string | null;
    input_token_count?: number | null;
    output_token_count?: number | null;
    costs_in_usd?: number | null;
    started_at?: string;
    stopped_at?: string;
    created_at: string;
    updated_at: string;
}

/** Full task detail: the task's columns, its effective prompt/input, and the
 *  raw list of attempts. The result, cost, retry count and failed list are all
 *  derived client-side from `attempts`. */
export interface BatchTaskDetail {
    id: number;
    batch_id: number;
    batch_file_id: number;
    file_id: number;
    status: BatchTaskStatus;
    prompt_marker?: string;
    depends_on_batch_task_id?: number;
    system_prompt?: string | null;
    user_input?: string | null;
    attempts: LlmAttempt[];
    started_at?: string;
    stopped_at?: string;
    created_at: string;
    updated_at: string;
}
