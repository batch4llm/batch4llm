export interface Endpoint {
    id: number;
    name: string;
    client: string;
    provider: string;
    url: string;
    token: string;
    created_at: string;
    is_healthy?: boolean | null;
    health_checked_at?: string | null;
    health_error?: string | null;
}