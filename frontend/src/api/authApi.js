import { apiClient } from "./apiClient";


export const signup = async ({
                                 username,
                                 email,
                                 password,
                             }) => {
    const response = await apiClient.post(
        "/auth/signup",
        {
            username,
            email,
            password,
        },
    );

    return response.data;
};


export const login = async ({
                                username,
                                password,
                            }) => {
    const response = await apiClient.post(
        "/auth/login",
        {
            username,
            password,
        },
    );

    return response.data;
};


export const getCurrentUser = async () => {
    const response = await apiClient.get(
        "/auth/me",
    );

    return response.data;
};


export const refreshAccessToken = async (
    refreshToken,
) => {
    const response = await apiClient.post(
        "/auth/refresh",
        {
            refresh_token: refreshToken,
        },
    );

    return response.data;
};


export const logout = async (
    refreshToken,
) => {
    const response = await apiClient.post(
        "/auth/logout",
        {
            refresh_token: refreshToken,
        },
    );

    return response.data;
};