import axios from "axios";

import { appConfig } from "../config";

import {
    clearTokens,
    getAccessToken,
    getRefreshToken,
    saveAccessToken,
} from "./tokenStorage";


export const apiClient = axios.create({
    baseURL: appConfig.apiBaseUrl,
    timeout: appConfig.requestTimeout,
    headers: {
        "Content-Type":
            "application/json",
    },
});


apiClient.interceptors.request.use(
    (config) => {
        const accessToken =
            getAccessToken();

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


const requestNewAccessToken =
    async () => {
        const refreshToken =
            getRefreshToken();

        if (!refreshToken) {
            throw new Error(
                "Refresh Token이 없습니다.",
            );
        }

        const response = await axios.post(
            `${appConfig.apiBaseUrl}/auth/refresh`,
            {
                refresh_token:
                refreshToken,
            },
            {
                timeout: 10000,
            },
        );

        const newAccessToken =
            response.data.access_token;

        saveAccessToken(
            newAccessToken,
        );

        return newAccessToken;
    };


apiClient.interceptors.response.use(
    (response) => response,

    async (error) => {
        const originalRequest =
            error.config;

        const isUnauthorized =
            error.response?.status === 401;

        const requestUrl =
            originalRequest?.url || "";

        const isAuthRequest =
            requestUrl.includes(
                "/auth/login",
            ) ||
            requestUrl.includes(
                "/auth/signup",
            ) ||
            requestUrl.includes(
                "/auth/refresh",
            );

        if (
            !isUnauthorized ||
            !originalRequest ||
            originalRequest._retry ||
            isAuthRequest
        ) {
            return Promise.reject(error);
        }

        originalRequest._retry = true;

        try {
            if (!refreshPromise) {
                refreshPromise =
                    requestNewAccessToken()
                        .finally(() => {
                            refreshPromise =
                                null;
                        });
            }

            const newAccessToken =
                await refreshPromise;

            originalRequest
                .headers
                .Authorization =
                `Bearer ${newAccessToken}`;

            return apiClient(
                originalRequest,
            );

        } catch (refreshError) {
            clearTokens();

            window.dispatchEvent(
                new Event(
                    "auth:logout",
                ),
            );

            return Promise.reject(
                refreshError,
            );
        }
    },
);