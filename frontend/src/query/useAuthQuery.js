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
    "current-user",
];


export const useCurrentUserQuery = () => {
    return useQuery({
        queryKey: AUTH_QUERY_KEY,
        queryFn: getCurrentUser,
        enabled: hasAccessToken(),
        retry: false,
    });
};


export const useSignupMutation = () => {
    return useMutation({
        mutationFn: signup,
    });
};


export const useLoginMutation = () => {
    const queryClient = useQueryClient();

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
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async () => {
            const refreshToken =
                getRefreshToken();

            if (refreshToken) {
                await logout(refreshToken);
            }
        },

        onSettled: () => {
            clearTokens();

            queryClient.removeQueries({
                queryKey: AUTH_QUERY_KEY,
            });

            window.dispatchEvent(
                new Event("auth:logout"),
            );
        },
    });
};