import { api } from "./client";

type SuccessResponse = {
    success: boolean;
};

export const LoginAPI = {
    login: (username: string, password: string): Promise<boolean> =>
        api
            .post<SuccessResponse>("/authentication/login", { username, password })
            .then(r => r.data.success),

    authenticate: (): Promise<boolean> =>
        api
            .get<SuccessResponse>("/authentication/me")
            .then(r => r.data.success),

    logout: (): Promise<boolean> =>
        api
            .post<SuccessResponse>("/authentication/logout")
            .then(r => r.data.success),
};
