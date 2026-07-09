export interface Prompt {
    id: number;
    name: string;
    content: string;
    multi_prompt: boolean;
    step_count: number | null;
    created_at: string;
}