import axios from "axios";

const imageRagClient = axios.create({
    baseURL:
        import.meta.env.VITE_API_URL ||
        "/api/image-rag",
    timeout: 60000,
});

export const analyzeFoodImage = async (imageFile) => {
    const formData = new FormData();

    formData.append("image", imageFile);

    const response = await imageRagClient.post(
        "/analyze",
        formData,
    );

    return response.data;
};