from pydantic import BaseModel, Field


class FoodCandidate(BaseModel):
    """
    음식 후보 한 개의 순위 정보
    """

    rank: int = Field(
        ge=1,
        le=3,
        description="음식 후보 순위",
    )

    food_name: str = Field(
        description="후보 음식 이름",
    )

    similarity: float = Field(
        ge=0,
        le=1,
        description="후보 음식 유사도",
    )


class ImageRagResponse(BaseModel):
    """
    음식 이미지 분석 API 응답
    """

    predicted_food: str = Field(
        description="가장 가능성이 높은 음식 이름",
    )

    confidence: float = Field(
        ge=0,
        le=1,
        description="최종 예측 신뢰도",
    )

    image_description: str = Field(
        description="사진에서 확인되는 음식의 특징",
    )

    reason: str = Field(
        description="해당 음식으로 판단한 이유",
    )

    candidates: list[FoodCandidate] = Field(
        description="가능성이 높은 음식 후보 3개",
    )