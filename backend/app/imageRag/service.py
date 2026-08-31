import base64

from fastapi import UploadFile
from openai import AsyncOpenAI

from app.config import settings
from app.imageRag.schema import (
    FoodCandidate,
    ImageRagResponse,
)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024


SYSTEM_PROMPT = """
당신은 한국 음식 이미지를 분석하는 전문가입니다.

사용자가 업로드한 음식 사진을 확인하고 다음 내용을 분석하세요.

분석 조건:
1. 사진에서 가장 가능성이 높은 음식 이름을 찾으세요.
2. 음식의 재료, 모양, 색상, 조리 방법 등 특징을 설명하세요.
3. 해당 음식으로 판단한 이유를 구체적으로 설명하세요.
4. 가능성이 높은 음식 후보를 정확히 3개 제시하세요.
5. 후보는 가능성이 높은 순서대로 작성하세요.
6. 모든 점수는 0부터 1 사이의 숫자로 작성하세요.
7. candidates의 rank는 반드시 1, 2, 3이어야 합니다.
8. 서로 다른 음식 후보를 작성하세요.
9. 음식이 아닌 이미지라도 임의로 확신하지 말고 낮은 점수를 사용하세요.
10. 모든 설명은 한국어로 작성하세요.

예시:
- 1순위: 김밥, score 0.93
- 2순위: 충무김밥, score 0.61
- 3순위: 주먹밥, score 0.35
"""


def validate_image(image: UploadFile) -> None:
    """
    업로드 파일의 형식을 검사합니다.
    """
    if image is None:
        raise ValueError("이미지 파일이 필요합니다.")

    if not image.filename:
        raise ValueError("이미지 파일 이름이 없습니다.")

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            "JPG, JPEG, PNG, WEBP 형식의 이미지만 업로드할 수 있습니다."
        )


async def run_image_rag(
    image: UploadFile,
) -> ImageRagResponse:
    """
    업로드된 음식 이미지를 OpenAI Vision으로 분석하고
    가능성이 높은 음식 후보 3개를 반환합니다.
    """
    validate_image(image)

    image_bytes = await image.read()

    if not image_bytes:
        raise ValueError("업로드된 이미지 파일이 비어 있습니다.")

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise ValueError("이미지 크기는 10MB 이하여야 합니다.")

    content_type = image.content_type or "image/jpeg"

    encoded_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_data_url = (
        f"data:{content_type};base64,{encoded_image}"
    )

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
    )

    try:
        completion = await client.chat.completions.parse(
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
                                "이 음식 이미지를 분석해서 "
                                "가장 가능성이 높은 음식과 "
                                "후보 음식 3개의 순위를 알려주세요."
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

    except Exception as error:
        raise RuntimeError(
            f"OpenAI 이미지 분석 요청에 실패했습니다: {error}"
        ) from error

    message = completion.choices[0].message

    if message.refusal:
        raise ValueError(
            f"이미지 분석이 거절되었습니다: {message.refusal}"
        )

    result = message.parsed

    if result is None:
        raise RuntimeError(
            "OpenAI 응답을 분석 결과로 변환하지 못했습니다."
        )

    if len(result.candidates) != 3:
        raise RuntimeError(
            "음식 후보가 정확히 3개 반환되지 않았습니다."
        )

    # 점수가 높은 후보부터 정렬합니다.
    sorted_candidates = sorted(
        result.candidates,
        key=lambda candidate: candidate.score,
        reverse=True,
    )

    # rank를 항상 1, 2, 3으로 다시 설정합니다.
    ranked_candidates = [
        FoodCandidate(
            rank=index,
            food_name=candidate.food_name,
            score=candidate.score,
        )
        for index, candidate in enumerate(
            sorted_candidates,
            start=1,
        )
    ]

    # 최종 음식과 신뢰도는 1순위 후보에 맞춥니다.
    return ImageRagResponse(
        predicted_food=ranked_candidates[0].food_name,
        confidence=ranked_candidates[0].score,
        image_description=result.image_description,
        reason=result.reason,
        candidates=ranked_candidates,
    )