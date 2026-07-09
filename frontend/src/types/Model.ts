export interface ModelInfo {
    id: number;
    endpoint_id: number;
    endpoint_name: string;
    provider: string;
    model_name: string;
    input_cost_per_1m_tokens: number | null;
    output_cost_per_1m_tokens: number | null;
    created_at: string;
    updated_at: string;
}
