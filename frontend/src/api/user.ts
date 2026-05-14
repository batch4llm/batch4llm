import { api } from "./client";

export type User = {
    id: number;
    username: string;
    group_id: number | null;
    is_admin: boolean;
    is_supervisor: boolean;
    is_verified: boolean;
    created_at: string;
};

type GroupMember = { id: number; username: string };

export type Group = {
    id: number;
    name: string;
    created_at: string;
    users: GroupMember[];
};

export const UserAPI = {
    getMe: (): Promise<User> =>
        api.get<User>("/user/me").then(r => r.data),

    getGroup: (): Promise<Group | null> =>
        api.get<Group>("/user/group").then(r => r.data).catch(err => {
            if (err.response?.status === 404) return null;
            throw err;
        }),
};
