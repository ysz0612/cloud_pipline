import base64

from fastapi import UploadFile
from openai import AsyncOpenAI

from app.config import settings
from app.imageRag.schema import (
    FoodCandidate,
    ImageRagResponse,
)


# 업로드 가능한 이미지 형식
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}


# 최대 이미지 용량: 10MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024


SYSTEM_PROMPT = """
당신은 한국 음식 이미지를 분석하는 전문가입니다.

사용자가 업로드한 음식 사진을 자세히 확인하고 분석하세요.

반드시 다음 조건을 지켜야 합니다.

1. 사진에서 가장 가능성이 높은 음식 이름을 찾으세요.
2. 사진에서 보이는 재료, 모양, 색상, 토핑, 조리 방법을 설명하세요.
3. 해당 음식으로 판단한 이유를 구체적으로 설명하세요.
4. 가능성이 높은 음식 후보를 정확히 3개 제시하세요.
5. 후보 음식은 가능성이 높은 순서대로 작성하세요.
6. 후보 음식은 서로 다른 음식이어야 합니다.
7. candidates의 rank는 반드시 1, 2, 3이어야 합니다.
8. similarity와 confidence는 0부터 1 사이의 숫자로 작성하세요.
9. 모든 음식 이름과 설명은 한국어로 작성하세요.
10. 음식이 아닌 이미지이거나 판단이 어려우면 신뢰도를 낮게 작성하세요.

예시:
{
    "predicted_food": "피자",
    "confidence": 0.95,
    "image_description": "토마토소스와 치즈가 올라간 둥근 형태의 음식입니다.",
    "reason": "둥근 도우 위에 토마토소스, 치즈, 올리브가 토핑되어 있습니다.",
    "candidates": [
        {
            "rank": 1,
            "food_name": "피자",
            "similarity": 0.95
        },
        {
            "rank": 2,
            "food_name": "프리타타",
            "similarity": 0.45
        },
        {
            "rank": 3,
            "food_name": "타르트",
            "similarity": 0.25
        }
    ]
}
"""


def validate_image(image: UploadFile) -> None:
    """
    업로드된 이미지 파일을 검사합니다.
    """

    if image is None:
        raise ValueError(
            "이미지 파일이 필요합니다."
        )

    if not image.filename:
        raise ValueError(
            "이미지 파일 이름이 없습니다."
        )

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            "JPG, JPEG, PNG, WEBP 형식의 "
            "이미지만 업로드할 수 있습니다."
        )


async def run_image_rag(
    image: UploadFile,
) -> ImageRagResponse:
    """
    업로드된 음식 이미지를 분석하고
    음식 후보 3개의 순위를 반환합니다.
    """

    # 1. 이미지 파일 형식 검사
    validate_image(image)

    # 2. 이미지 읽기
    image_bytes = await image.read()

    if not image_bytes:
        raise ValueError(
            "업로드된 이미지 파일이 비어 있습니다."
        )

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise ValueError(
            "이미지 크기는 10MB 이하여야 합니다."
        )

    # 3. 이미지를 Base64 문자열로 변환
    content_type = (
        image.content_type
        or "image/jpeg"
    )

    encoded_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_data_url = (
        f"data:{content_type};base64,{encoded_image}"
    )

    # 4. OpenAI 클라이언트 생성
    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
    )

    # 5. OpenAI Vision 분석 요청
    try:
        completion = (
            await client.chat.completions.parse(
                model=settings.openai_vision_model,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "이 음식 사진을 분석하세요. "
                                    "가장 가능성이 높은 음식과 "
                                    "유사한 음식 후보 3개를 "
                                    "순위와 유사도로 알려주세요."
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data_url,
                                    "detail": "auto",
                                },
                            },
                        ],
                    },
                ],
                response_format=ImageRagResponse,
            )
        )

    except Exception as error:
        raise RuntimeError(
            "OpenAI 이미지 분석 요청에 "
            f"실패했습니다: {error}"
        ) from error

    # 6. OpenAI 메시지 확인
    message = completion.choices[0].message

    if message.refusal:
        raise ValueError(
            "OpenAI가 이미지 분석 요청을 "
            f"거절했습니다: {message.refusal}"
        )

    result = message.parsed

    if result is None:
        raise RuntimeError(
            "OpenAI 분석 결과를 응답 모델로 "
            "변환하지 못했습니다."
        )

    # 7. 후보 개수 검사
    if len(result.candidates) != 3:
        raise RuntimeError(
            "OpenAI가 음식 후보를 정확히 "
            "3개 반환하지 않았습니다."
        )

    # 8. 유사도가 높은 순서대로 정렬
    sorted_candidates = sorted(
        result.candidates,
        key=lambda candidate: candidate.similarity,
        reverse=True,
    )

    # 9. 순위를 1, 2, 3으로 다시 설정
    ranked_candidates = [
        FoodCandidate(
            rank=index,
            food_name=candidate.food_name,
            similarity=candidate.similarity,
        )
        for index, candidate in enumerate(
            sorted_candidates,
            start=1,
        )
    ]

    # 10. 중복된 음식 후보 검사
    food_names = [
        candidate.food_name.strip()
        for candidate in ranked_candidates
    ]

    if len(set(food_names)) != 3:
        raise RuntimeError(
            "OpenAI가 중복된 음식 후보를 반환했습니다. "
            "이미지를 다시 분석해 주세요."
        )

    # 11. 1순위 후보를 최종 예측 결과로 반환
    return ImageRagResponse(
        predicted_food=ranked_candidates[0].food_name,
        confidence=ranked_candidates[0].similarity,
        image_description=result.image_description,
        reason=result.reason,
        candidates=ranked_candidates,
    )