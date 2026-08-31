import { apiClient } from "./apiClient";

import {
    getAccessToken,
} from "./tokenStorage";


export const analyzeFoodImage = async (
    imageFile,
) => {
    const accessToken =
        getAccessToken();

    if (!accessToken) {
        window.dispatchEvent(
            new Event(
                "auth:required",
            ),
        );

        throw new Error(
            "음식 분석을 이용하려면 로그인이 필요합니다.",
        );
    }

    const formData = new FormData();

    formData.append(
        "image",
        imageFile,
    );

    const response = await apiClient.post(
        "/image-rag/analyze",
        formData,
        {
            headers: {
                "Content-Type":
                    "multipart/form-data",
            },
        },
    );

    return response.data;
};