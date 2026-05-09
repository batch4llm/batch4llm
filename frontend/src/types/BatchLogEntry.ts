export type LogLevel = "INFO" | "WARN" | "ERROR" | "FATAL";

export interface BatchLogEntry {
    id: number;
    batch_id: number;
    batch_file_id: number;
    batch_task_id: number;
    message: string;
    level: LogLevel;
    created_at: string;
}