import { apiClient } from "./apiClient";


export const analyzeFoodImage = async (
    imageFile,
) => {
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