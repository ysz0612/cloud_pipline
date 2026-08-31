from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from app.imageRag.schema import ImageRagResponse
from app.imageRag.service import run_image_rag


router = APIRouter(
    prefix="/api/image-rag",
    tags=["Image RAG"],
)


@router.post(
    "/analyze",
    response_model=ImageRagResponse,
)
async def analyze_food_image(
    image: UploadFile = File(...),
):
    """
    음식 이미지를 업로드하면 음식 종류와 특징을 분석합니다.
    """
    try:
        return await run_image_rag(image)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"이미지 분석에 실패했습니다: {error}",
        ) from error