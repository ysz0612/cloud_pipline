import { useMutation } from "@tanstack/react-query";

import { analyzeFoodImage } from "../api/imageRagApi";


export const useImageRagMutation = () => {
    return useMutation({
        mutationFn: analyzeFoodImage,
    });
};