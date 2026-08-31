from pydantic import BaseModel, Field


class ImageRagResponse(BaseModel):
    predicted_food: str = Field(
        description="이미지에서 판별한 음식 이름"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="음식 판별 신뢰도",
    )

    image_description: str = Field(
        description="음식의 재료, 맛, 형태, 조리법 등 특징"
    )

    reason: str = Field(
        description="해당 음식으로 판단한 이유"
    )