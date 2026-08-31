import {
    useMutation,
    useQuery,
    useQueryClient,
} from "@tanstack/react-query";

import {
    getCurrentUser,
    login,
    logout,
    signup,
} from "../api/authApi";

import {
    clearTokens,
    getRefreshToken,
    hasAccessToken,
    saveTokens,
} from "../api/tokenStorage";


export const AUTH_QUERY_KEY = [
    "auth",
    "currentUser",
];


export const useCurrentUserQuery = () => {
    const tokenExists =
        hasAccessToken();

    return useQuery({
        queryKey: AUTH_QUERY_KEY,
        queryFn: getCurrentUser,
        enabled: tokenExists,
        retry: false,
        staleTime: 5 * 60 * 1000,
    });
};


export const useSignupMutation = () => {
    return useMutation({
        mutationFn: signup,
    });
};


export const useLoginMutation = () => {
    const queryClient =
        useQueryClient();

    return useMutation({
        mutationFn: login,

        onSuccess: (data) => {
            saveTokens({
                accessToken:
                data.access_token,

                refreshToken:
                data.refresh_token,
            });

            queryClient.setQueryData(
                AUTH_QUERY_KEY,
                data.user,
            );
        },
    });
};


export const useLogoutMutation = () => {
    const queryClient =
        useQueryClient();

    return useMutation({
        mutationFn: async () => {
            const refreshToken =
                getRefreshToken();

            if (!refreshToken) {
                return;
            }

            await logout(refreshToken);
        },

        onSettled: async () => {
            /*
             * 로그아웃 API 성공 여부와 상관없이
             * 브라우저 로그인 정보를 정리합니다.
             */

            clearTokens();

            await queryClient.cancelQueries({
                queryKey:
                AUTH_QUERY_KEY,
            });

            /*
             * 현재 사용자 캐시를 null로 바꿔서
             * App.jsx가 즉시 로그아웃 상태로
             * 다시 렌더링되게 합니다.
             */
            queryClient.setQueryData(
                AUTH_QUERY_KEY,
                null,
            );

            queryClient.removeQueries({
                queryKey:
                AUTH_QUERY_KEY,
                exact: true,
            });

            window.dispatchEvent(
                new Event(
                    "auth:logout",
                ),
            );
        },
    });
};