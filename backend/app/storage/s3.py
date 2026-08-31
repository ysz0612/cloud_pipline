# s3 crud 코드
import re
import uuid
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.config import settings


s3_client = boto3.client(
    "s3",
    region_name=settings.aws_region,
)


BUCKET_NAME = settings.s3_bucket_name

IMAGE_PREFIX = (
    settings.s3_image_prefix.strip("/") + "/"
)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def _validate_food_name(
    food_name: str,
) -> str:
    normalized_name = food_name.strip()

    if not normalized_name:
        raise ValueError(
            "음식 이름이 비어 있습니다."
        )

    if len(normalized_name) > 50:
        raise ValueError(
            "음식 이름은 50자 이하여야 합니다."
        )

    if not re.fullmatch(
        r"[가-힣a-zA-Z0-9 _-]+",
        normalized_name,
    ):
        raise ValueError(
            "음식 이름에는 한글, 영문, 숫자, "
            "공백, 밑줄, 하이픈만 사용할 수 있습니다."
        )

    return normalized_name


def _validate_content_type(
    content_type: str,
) -> str:
    extension = ALLOWED_IMAGE_TYPES.get(
        content_type
    )

    if not extension:
        raise ValueError(
            "JPG, JPEG, PNG, WEBP 이미지만 "
            "사용할 수 있습니다."
        )

    return extension


def _validate_object_key(
    object_key: str,
) -> str:
    normalized_key = object_key.strip()

    if not normalized_key.startswith(
        IMAGE_PREFIX
    ):
        raise ValueError(
            f"S3 이미지 경로는 {IMAGE_PREFIX}로 "
            "시작해야 합니다."
        )

    if ".." in normalized_key.split("/"):
        raise ValueError(
            "올바르지 않은 S3 이미지 경로입니다."
        )

    extension = Path(
        normalized_key
    ).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "올바른 이미지 파일 경로가 아닙니다."
        )

    return normalized_key


def _extract_food_name(
    object_key: str,
) -> str:
    relative_key = object_key.removeprefix(
        IMAGE_PREFIX
    )

    path_parts = relative_key.split("/")

    if len(path_parts) < 2:
        return ""

    return path_parts[0]


def _create_presigned_url(
    object_key: str,
) -> str:
    return s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": object_key,
        },
        ExpiresIn=(
            settings.s3_presigned_url_expires
        ),
    )


def _check_image_exists(
    object_key: str,
) -> None:
    try:
        s3_client.head_object(
            Bucket=BUCKET_NAME,
            Key=object_key,
        )

    except ClientError as error:
        error_code = str(
            error.response.get(
                "Error",
                {},
            ).get("Code", "")
        )

        if error_code in {
            "404",
            "NoSuchKey",
            "NotFound",
        }:
            raise FileNotFoundError(
                f"S3 이미지를 찾을 수 없습니다: "
                f"{object_key}"
            ) from error

        raise RuntimeError(
            "S3 이미지 확인 중 오류가 발생했습니다."
        ) from error


# CREATE
async def create_image(
    food_name: str,
    image: UploadFile,
) -> dict[str, Any]:
    normalized_food_name = (
        _validate_food_name(food_name)
    )

    content_type = image.content_type or ""

    extension = _validate_content_type(
        content_type
    )

    image_bytes = await image.read()

    if not image_bytes:
        raise ValueError(
            "업로드한 이미지가 비어 있습니다."
        )

    file_name = f"{uuid.uuid4().hex}{extension}"

    object_key = (
        f"{IMAGE_PREFIX}"
        f"{normalized_food_name}/"
        f"{file_name}"
    )

    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=object_key,
            Body=image_bytes,
            ContentType=content_type,
        )

    except ClientError as error:
        raise RuntimeError(
            "S3 이미지 업로드에 실패했습니다."
        ) from error

    return {
        "message": "이미지가 등록되었습니다.",
        "food_name": normalized_food_name,
        "object_key": object_key,
        "image_url": _create_presigned_url(
            object_key
        ),
    }


# READ: 이미지 목록
def list_images(
    food_name: str | None = None,
) -> list[dict[str, Any]]:
    if food_name:
        normalized_food_name = (
            _validate_food_name(food_name)
        )

        search_prefix = (
            f"{IMAGE_PREFIX}"
            f"{normalized_food_name}/"
        )
    else:
        search_prefix = IMAGE_PREFIX

    paginator = s3_client.get_paginator(
        "list_objects_v2"
    )

    results: list[dict[str, Any]] = []

    try:
        pages = paginator.paginate(
            Bucket=BUCKET_NAME,
            Prefix=search_prefix,
        )

        for page in pages:
            for item in page.get(
                "Contents",
                [],
            ):
                object_key = item["Key"]

                extension = Path(
                    object_key
                ).suffix.lower()

                if extension not in (
                    SUPPORTED_EXTENSIONS
                ):
                    continue

                detected_food_name = (
                    _extract_food_name(
                        object_key
                    )
                )

                if not detected_food_name:
                    continue

                results.append(
                    {
                        "food_name": (
                            detected_food_name
                        ),
                        "object_key": object_key,
                        "size": item.get(
                            "Size",
                            0,
                        ),
                        "last_modified": (
                            item[
                                "LastModified"
                            ].isoformat()
                            if item.get(
                                "LastModified"
                            )
                            else None
                        ),
                        "image_url": (
                            _create_presigned_url(
                                object_key
                            )
                        ),
                    }
                )

    except ClientError as error:
        raise RuntimeError(
            "S3 이미지 목록 조회에 실패했습니다."
        ) from error

    return results


# READ: 이미지 하나
def get_image(
    object_key: str,
) -> dict[str, Any]:
    normalized_key = _validate_object_key(
        object_key
    )

    _check_image_exists(normalized_key)

    return {
        "food_name": _extract_food_name(
            normalized_key
        ),
        "object_key": normalized_key,
        "image_url": _create_presigned_url(
            normalized_key
        ),
    }


# READ: 이미지 원본 bytes
def get_image_bytes(
    object_key: str,
) -> tuple[bytes, str]:
    normalized_key = _validate_object_key(
        object_key
    )

    try:
        response = s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key=normalized_key,
        )

    except ClientError as error:
        error_code = str(
            error.response.get(
                "Error",
                {},
            ).get("Code", "")
        )

        if error_code in {
            "404",
            "NoSuchKey",
            "NotFound",
        }:
            raise FileNotFoundError(
                f"S3 이미지를 찾을 수 없습니다: "
                f"{normalized_key}"
            ) from error

        raise RuntimeError(
            "S3 이미지 조회에 실패했습니다."
        ) from error

    image_bytes = response["Body"].read()

    content_type = response.get(
        "ContentType",
        "application/octet-stream",
    )

    return image_bytes, content_type


# UPDATE
async def update_image(
    object_key: str,
    image: UploadFile,
) -> dict[str, Any]:
    normalized_key = _validate_object_key(
        object_key
    )

    _check_image_exists(normalized_key)

    content_type = image.content_type or ""

    new_extension = _validate_content_type(
        content_type
    )

    current_extension = Path(
        normalized_key
    ).suffix.lower()

    if (
        current_extension == ".jpeg"
        and new_extension == ".jpg"
    ):
        new_extension = ".jpeg"

    if current_extension != new_extension:
        raise ValueError(
            "기존 이미지와 같은 확장자의 파일로 "
            "교체해주세요."
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise ValueError(
            "업로드한 이미지가 비어 있습니다."
        )

    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=normalized_key,
            Body=image_bytes,
            ContentType=content_type,
        )

    except ClientError as error:
        raise RuntimeError(
            "S3 이미지 교체에 실패했습니다."
        ) from error

    return {
        "message": "이미지가 교체되었습니다.",
        "food_name": _extract_food_name(
            normalized_key
        ),
        "object_key": normalized_key,
        "image_url": _create_presigned_url(
            normalized_key
        ),
    }


# DELETE
def delete_image(
    object_key: str,
) -> dict[str, str]:
    normalized_key = _validate_object_key(
        object_key
    )

    _check_image_exists(normalized_key)

    try:
        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=normalized_key,
        )

    except ClientError as error:
        raise RuntimeError(
            "S3 이미지 삭제에 실패했습니다."
        ) from error

    return {
        "message": "이미지가 삭제되었습니다.",
        "object_key": normalized_key,
    }