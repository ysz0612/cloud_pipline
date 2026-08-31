import base64
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import UploadFile
from openai import OpenAI

from app.imageRag.schema import ImageRagResponse


# 로컬 실행 시:
# project/backend/app/imageRag/service.py
# parents[3] = project
PROJECT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_DIR / ".env"

# 로컬에서는 project/.env를 읽습니다.
# Docker에서는 docker-compose의 env_file로 주입됩니다.
load_dotenv(ENV_FILE)


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VISION_MODEL = os.getenv(
    "OPENAI_VISION_MODEL",
    "gpt-4o-mini",
)


if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY가 설정되지 않았습니다. "
        "프로젝트 최상단의 .env 파일을 확인하세요."
    )


client = OpenAI(
    api_key=OPENAI_API_KEY,
)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def encode_image(
    image_bytes: bytes,
    content_type: str,
) -> str:
    encoded_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    return (
        f"data:{content_type};base64,"
        f"{encoded_image}"
    )


def remove_code_block(text: str) -> str:
    cleaned_text = text.strip()

    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]

    return cleaned_text.strip()


async def run_image_rag(
    image: UploadFile,
) -> ImageRagResponse:
    content_type = image.content_type or ""

    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            "JPG, JPEG, PNG, WEBP 이미지만 "
            "업로드할 수 있습니다."
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise ValueError(
            "업로드한 이미지가 비어 있습니다."
        )

    image_url = encode_image(
        image_bytes=image_bytes,
        content_type=content_type,
    )

    prompt = """
당신은 한국 음식 이미지 분석 전문가입니다.

업로드된 이미지를 확인하고 다음 내용을 분석하세요.

1. 이미지에 있는 음식의 정확한 종류
2. 음식에서 관찰되는 주요 재료
3. 음식의 색상과 형태
4. 국물 유무
5. 대표적인 조리 방식
6. 일반적인 맛과 식감
7. 해당 음식이라고 판단한 시각적인 근거

음식 이름은 한국어로 답하세요.

확실하지 않은 경우에도 이미지에서 가장 가능성이 높은
음식 하나를 선택하세요.

반드시 다음 JSON 형식으로만 응답하세요.

{
  "predicted_food": "음식 이름",
  "confidence": 0.0,
  "image_description": "음식의 주요 재료, 조리 방법, 맛, 형태 등의 특징",
  "reason": "사진 속 음식을 해당 음식이라고 판단한 이유"
}

confidence는 0.0 이상 1.0 이하의 숫자로 작성하세요.
JSON 외의 설명이나 마크다운은 출력하지 마세요.
"""

    response = client.responses.create(
        model=VISION_MODEL,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url,
                        "detail": "low",
                    },
                ],
            }
        ],
    )

    result_text = remove_code_block(
        response.output_text
    )

    try:
        result = json.loads(result_text)

    except json.JSONDecodeError as error:
        raise RuntimeError(
            "OpenAI 응답을 JSON으로 변환하지 못했습니다."
        ) from error

    confidence = float(
        result.get("confidence", 0.0)
    )

    confidence = max(
        0.0,
        min(confidence, 1.0),
    )

    return ImageRagResponse(
        predicted_food=result.get(
            "predicted_food",
            "알 수 없는 음식",
        ),
        confidence=confidence,
        image_description=result.get(
            "image_description",
            "음식 특징을 분석하지 못했습니다.",
        ),
        reason=result.get(
            "reason",
            "판단 근거를 생성하지 못했습니다.",
        ),
    )