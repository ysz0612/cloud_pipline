import { apiClient } from "./apiClient";


export const signup = async (
    signupData,
) => {
    const response = await apiClient.post(
        "/auth/signup",
        signupData,
    );

    return response.data;
};


export const login = async (
    loginData,
) => {
    const response = await apiClient.post(
        "/auth/login",
        loginData,
    );

    return response.data;
};


export const getCurrentUser =
    async () => {
        const response =
            await apiClient.get(
                "/auth/me",
            );

        return response.data;
    };


export const logout = async (
    refreshToken,
) => {
    const response =
        await apiClient.post(
            "/auth/logout",
            {
                refresh_token:
                refreshToken,
            },
        );

    return response.data;
};