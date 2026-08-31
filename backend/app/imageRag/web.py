from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from app.auth.dependencies import (
    get_current_user,
)
from app.imageRag.schema import (
    ImageRagResponse,
)
from app.imageRag.service import (
    run_image_rag,
)
from app.users.model import User


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

    current_user: Annotated[
        User,
        Depends(get_current_user),
    ] = None,
):
    """
    로그인한 사용자만 음식 이미지를
    분석할 수 있습니다.
    """
    try:
        return await run_image_rag(image)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "이미지 분석에 실패했습니다: "
                f"{error}"
            ),
        ) from error