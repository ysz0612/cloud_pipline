import axios from "axios";

import {
    clearTokens,
    getAccessToken,
    getRefreshToken,
    saveAccessToken,
} from "./tokenStorage";


const API_BASE_URL =
    import.meta.env.VITE_API_URL ||
    "/api";


export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,
});


apiClient.interceptors.request.use(
    (config) => {
        const accessToken = getAccessToken();

        if (accessToken) {
            config.headers.Authorization =
                `Bearer ${accessToken}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    },
);


let refreshPromise = null;


const requestNewAccessToken = async () => {
    const refreshToken = getRefreshToken();

    if (!refreshToken) {
        throw new Error(
            "Refresh Token이 없습니다.",
        );
    }

    const response = await axios.post(
        `${API_BASE_URL}/auth/refresh`,
        {
            refresh_token: refreshToken,
        },
        {
            timeout: 10000,
        },
    );

    const newAccessToken =
        response.data.access_token;

    saveAccessToken(newAccessToken);

    return newAccessToken;
};


apiClient.interceptors.response.use(
    (response) => response,

    async (error) => {
        const originalRequest = error.config;

        if (
            error.response?.status !== 401 ||
            !originalRequest ||
            originalRequest._retry
        ) {
            return Promise.reject(error);
        }

        const requestUrl =
            originalRequest.url || "";

        if (
            requestUrl.includes("/auth/login") ||
            requestUrl.includes("/auth/signup") ||
            requestUrl.includes("/auth/refresh")
        ) {
            return Promise.reject(error);
        }

        originalRequest._retry = true;

        try {
            if (!refreshPromise) {
                refreshPromise =
                    requestNewAccessToken().finally(
                        () => {
                            refreshPromise = null;
                        },
                    );
            }

            const newAccessToken =
                await refreshPromise;

            originalRequest.headers.Authorization =
                `Bearer ${newAccessToken}`;

            return apiClient(originalRequest);

        } catch (refreshError) {
            clearTokens();

            window.dispatchEvent(
                new Event("auth:logout"),
            );

            return Promise.reject(
                refreshError,
            );
        }
    },
);