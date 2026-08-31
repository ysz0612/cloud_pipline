import asyncio
import base64

from fastapi import UploadFile
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.config import settings
from app.imageRag.schema import (
    FoodCandidate,
    ImageRagResponse,
)
from app.storage.s3 import list_food_names


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024


class ModelCandidate(BaseModel):
    """
    OpenAI 내부 응답입니다.

    음식 이름을 직접 받지 않고,
    S3 음식 목록의 번호를 받습니다.
    """

    food_index: int = Field(
        description="제공된 음식 목록의 번호",
    )

    similarity: float = Field(
        ge=0,
        le=1,
        description="업로드 이미지와의 유사도",
    )


class ModelImageAnalysis(BaseModel):
    """
    OpenAI 내부 이미지 분석 응답입니다.
    """

    image_description: str
    reason: str
    candidates: list[ModelCandidate]


SYSTEM_PROMPT = """
당신은 음식 이미지 분류 전문가입니다.

사용자가 제공하는 음식 사진을 분석한 다음,
함께 제공되는 'S3 음식 데이터 목록' 안에서만
가장 유사한 음식 후보 3개를 선택하세요.

반드시 다음 규칙을 지키세요.

1. 음식 목록에 없는 음식은 절대로 선택하지 마세요.
2. 음식 이름을 직접 작성하지 마세요.
3. 반드시 목록에 표시된 food_index 번호만 반환하세요.
4. 서로 다른 food_index를 정확히 3개 반환하세요.
5. 가장 가능성이 높은 후보부터 순서대로 반환하세요.
6. similarity는 0부터 1 사이의 숫자입니다.
7. image_description은 사진에서 실제로 보이는 특징을 설명하세요.
8. reason은 후보를 선택한 근거를 한국어로 설명하세요.
9. 목록에 정확한 음식이 없어도 목록 안에서 가장 가까운 후보를 선택하세요.
10. 모든 설명은 한국어로 작성하세요.
"""


def validate_image(image: UploadFile) -> None:
    """
    업로드 이미지 파일을 검사합니다.
    """
    if image is None:
        raise ValueError("이미지 파일이 필요합니다.")

    if not image.filename:
        raise ValueError("이미지 파일 이름이 없습니다.")

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            "JPG, JPEG, PNG, WEBP 형식의 "
            "이미지만 업로드할 수 있습니다."
        )


def create_food_list_prompt(
    food_names: list[str],
) -> str:
    """
    S3 음식 폴더 목록에 번호를 붙입니다.

    예:
    1: 갈비구이
    2: 갈비탕
    3: 김밥
    """
    lines = [
        f"{index}: {food_name}"
        for index, food_name in enumerate(
            food_names,
            start=1,
        )
    ]

    return "\n".join(lines)


def validate_model_candidates(
    analysis: ModelImageAnalysis,
    food_count: int,
) -> None:
    """
    OpenAI가 반환한 번호가 실제 S3 음식 목록에
    존재하는지 검사합니다.
    """
    if len(analysis.candidates) != 3:
        raise ValueError(
            "음식 후보가 정확히 3개가 아닙니다."
        )

    candidate_indexes = [
        candidate.food_index
        for candidate in analysis.candidates
    ]

    if len(set(candidate_indexes)) != 3:
        raise ValueError(
            "중복된 음식 후보가 반환되었습니다."
        )

    for food_index in candidate_indexes:
        if food_index < 1 or food_index > food_count:
            raise ValueError(
                "S3 음식 목록에 없는 번호가 반환되었습니다."
            )


async def request_openai_analysis(
    image_data_url: str,
    food_names: list[str],
) -> ModelImageAnalysis:
    """
    OpenAI에 이미지와 S3 음식 목록을 전달합니다.
    """
    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
    )

    food_list_prompt = create_food_list_prompt(
        food_names
    )

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
                            "다음은 S3에 실제로 저장된 "
                            "음식 데이터 목록입니다.\n\n"
                            f"{food_list_prompt}\n\n"
                            "업로드한 사진과 가장 유사한 "
                            "음식 번호 3개를 선택하세요."
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
        response_format=ModelImageAnalysis,
    )

    message = completion.choices[0].message

    if message.refusal:
        raise ValueError(
            f"이미지 분석이 거절되었습니다: {message.refusal}"
        )

    if message.parsed is None:
        raise RuntimeError(
            "OpenAI 분석 결과를 변환하지 못했습니다."
        )

    return message.parsed


async def run_image_rag(
    image: UploadFile,
) -> ImageRagResponse:
    """
    S3 음식 데이터 목록 안에서만
    음식 후보 3개를 검색합니다.
    """
    validate_image(image)

    # S3 호출은 동기 함수이므로 별도 스레드에서 실행합니다.
    try:
        food_names = await asyncio.to_thread(
            list_food_names
        )

    except Exception as error:
        raise RuntimeError(
            f"S3 음식 데이터 조회에 실패했습니다: {error}"
        ) from error

    if not food_names:
        raise FileNotFoundError(
            "S3의 images/ 폴더에서 "
            "음식 데이터 폴더를 찾지 못했습니다."
        )

    if len(food_names) < 3:
        raise ValueError(
            "순위를 표시하려면 S3에 "
            "음식 폴더가 최소 3개 있어야 합니다."
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise ValueError(
            "업로드된 이미지 파일이 비어 있습니다."
        )

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise ValueError(
            "이미지 크기는 10MB 이하여야 합니다."
        )

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

    analysis: ModelImageAnalysis | None = None
    last_error: Exception | None = None

    # 모델이 잘못된 번호나 중복 번호를 반환할 경우
    # 최대 두 번 다시 분석합니다.
    for _ in range(2):
        try:
            analysis = await request_openai_analysis(
                image_data_url=image_data_url,
                food_names=food_names,
            )

            validate_model_candidates(
                analysis=analysis,
                food_count=len(food_names),
            )

            break

        except ValueError as error:
            last_error = error
            analysis = None

    if analysis is None:
        raise RuntimeError(
            "S3 음식 데이터 안에서 후보를 "
            f"선택하지 못했습니다: {last_error}"
        )

    # 유사도가 높은 순서대로 다시 정렬합니다.
    sorted_candidates = sorted(
        analysis.candidates,
        key=lambda candidate: candidate.similarity,
        reverse=True,
    )

    ranked_candidates: list[FoodCandidate] = []

    for rank, candidate in enumerate(
        sorted_candidates,
        start=1,
    ):
        # food_index는 1부터 시작하므로
        # 파이썬 리스트 접근 시 1을 뺍니다.
        food_name = food_names[
            candidate.food_index - 1
        ]

        ranked_candidates.append(
            FoodCandidate(
                rank=rank,
                food_name=food_name,
                similarity=candidate.similarity,
            )
        )

    first_candidate = ranked_candidates[0]

    return ImageRagResponse(
        predicted_food=first_candidate.food_name,
        confidence=first_candidate.similarity,
        image_description=analysis.image_description,
        reason=analysis.reason,
        candidates=ranked_candidates,
    )