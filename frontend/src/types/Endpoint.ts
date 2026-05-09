export interface Endpoint {
    id: number;
    name: string;
    client: string;
    provider: string;
    url: string;
    token: string;
    created_at: string;
    lastStatus?: "ok" | "down" | "idle";
}