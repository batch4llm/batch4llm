export type BatchStatus =
    | "SCHEDULED"
    | "QUEUED"
    | "RUNNING"
    | "PROVIDER_BATCH_PENDING"
    | "COMPLETED"
    | "STOPPED"
    | "FAILED";

export const ACTIVE_STATUSES: BatchStatus[] = [
    "SCHEDULED",
    "QUEUED",
    "RUNNING",
    "PROVIDER_BATCH_PENDING",
];

export interface Batch {
    id: number;
    name: string;
    status: BatchStatus;
    progress?: string;
    prompt_id: number | null;
    prompt_name?: string;
    endpoint_id: number | null;
    endpoint_name?: string;
    files: number[];
    file_reader: string;
    model: string;
    temperature: number;
    json_format: boolean;
    use_provider_batch?: boolean;
    scheduled_at?: string;
    delay: number;
    costs_in_usd?: number;
    created_at: string;
    updated_at: string;
    started_at?: string;
    stopped_at?: string;
    archived_at?: string;
    batch_worker_settings: BatchWorkerSettings;
}

export interface BatchWorkerSettings {
    // Starting point for the request rate; adaptive_rate_limiting adjusts it
    // automatically from here.
    max_tasks_per_minute: number;
    allow_concurrency: boolean;
    adaptive_rate_limiting: boolean;
    retries_per_failed_task: number;
    failure_threshold_percent: number;
}

export interface BatchStartRequest {
    prompt_id: number;
    files: number[];
    endpoint_id: number;
    file_reader: string;
    model: string;
    temperature: number;
    json_format?: boolean;
    use_provider_batch?: boolean;
    scheduled_at?: string;
    name?: string;
    batch_worker_settings: BatchWorkerSettings;
}