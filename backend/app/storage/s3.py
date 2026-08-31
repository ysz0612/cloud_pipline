import re
from pathlib import Path
from typing import Any
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.config import settings


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}


def get_s3_client():
    """
    EC2에 연결된 IAM Role을 이용해서 S3 클라이언트를 생성합니다.

    AWS_ACCESS_KEY_ID와 AWS_SECRET_ACCESS_KEY는 사용하지 않습니다.
    """
    return boto3.client(
        "s3",
        region_name=settings.aws_region,
    )


def get_image_prefix() -> str:
    """
    S3 이미지 경로가 항상 슬래시로 끝나도록 처리합니다.
    """
    prefix = settings.s3_image_prefix.strip("/")

    if not prefix:
        return ""

    return f"{prefix}/"


def validate_food_name(food_name: str) -> str:
    """
    음식 폴더 이름을 검사합니다.
    """
    cleaned_name = food_name.strip()

    if not cleaned_name:
        raise ValueError("음식 이름이 필요합니다.")

    if "/" in cleaned_name or "\\" in cleaned_name:
        raise ValueError(
            "음식 이름에는 경로 문자를 사용할 수 없습니다."
        )

    if not re.fullmatch(
        r"[가-힣a-zA-Z0-9 _()-]+",
        cleaned_name,
    ):
        raise ValueError(
            "음식 이름에 사용할 수 없는 문자가 포함되어 있습니다."
        )

    return cleaned_name


def validate_object_key(object_key: str) -> str:
    """
    S3 객체 경로가 images/ 내부인지 검사합니다.
    """
    cleaned_key = object_key.strip().lstrip("/")
    image_prefix = get_image_prefix()

    if not cleaned_key:
        raise ValueError("S3 이미지 경로가 필요합니다.")

    if not cleaned_key.startswith(image_prefix):
        raise ValueError(
            f"S3 객체는 {image_prefix} 내부에 있어야 합니다."
        )

    if ".." in cleaned_key:
        raise ValueError(
            "잘못된 S3 객체 경로입니다."
        )

    return cleaned_key


def validate_upload_image(image: UploadFile) -> None:
    """
    업로드 이미지 형식을 검사합니다.
    """
    if image is None:
        raise ValueError("이미지 파일이 필요합니다.")

    if not image.filename:
        raise ValueError("이미지 파일 이름이 없습니다.")

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            "JPG, JPEG, PNG, WEBP 이미지만 저장할 수 있습니다."
        )


def list_food_names() -> list[str]:
    """
    S3 images/ 아래에 존재하는 음식 폴더 이름을 조회합니다.

    예:
    images/갈비구이/001.jpg
    images/김밥/001.jpg
    images/피자/001.jpg

    반환:
    ["갈비구이", "김밥", "피자"]
    """
    client = get_s3_client()
    prefix = get_image_prefix()

    food_names: list[str] = []
    continuation_token: str | None = None

    try:
        while True:
            request: dict[str, Any] = {
                "Bucket": settings.s3_bucket_name,
                "Prefix": prefix,
                "Delimiter": "/",
            }

            if continuation_token:
                request["ContinuationToken"] = continuation_token

            response = client.list_objects_v2(**request)

            for common_prefix in response.get(
                "CommonPrefixes",
                [],
            ):
                folder_key = common_prefix["Prefix"]

                food_name = (
                    folder_key
                    .removeprefix(prefix)
                    .strip("/")
                )

                if food_name:
                    food_names.append(food_name)

            if not response.get("IsTruncated"):
                break

            continuation_token = response.get(
                "NextContinuationToken"
            )

    except ClientError as error:
        raise RuntimeError(
            f"S3 음식 폴더 조회에 실패했습니다: {error}"
        ) from error

    return sorted(set(food_names))


async def create_image(
    food_name: str,
    image: UploadFile,
) -> dict[str, Any]:
    """
    S3 음식 폴더에 새로운 이미지를 저장합니다.
    """
    validate_upload_image(image)

    cleaned_food_name = validate_food_name(food_name)

    original_filename = Path(
        image.filename or "image.jpg"
    )

    extension = original_filename.suffix.lower()

    if not extension:
        extension = ".jpg"

    object_key = (
        f"{get_image_prefix()}"
        f"{cleaned_food_name}/"
        f"{uuid4().hex}{extension}"
    )

    image_bytes = await image.read()

    if not image_bytes:
        raise ValueError(
            "업로드된 이미지 파일이 비어 있습니다."
        )

    client = get_s3_client()

    try:
        client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=object_key,
            Body=image_bytes,
            ContentType=image.content_type or "image/jpeg",
        )

    except ClientError as error:
        raise RuntimeError(
            f"S3 이미지 저장에 실패했습니다: {error}"
        ) from error

    return {
        "bucket": settings.s3_bucket_name,
        "object_key": object_key,
        "food_name": cleaned_food_name,
        "filename": original_filename.name,
    }


def list_images(
    food_name: str | None = None,
) -> list[dict[str, Any]]:
    """
    S3에 저장된 이미지 목록을 조회합니다.
    """
    prefix = get_image_prefix()

    if food_name:
        cleaned_food_name = validate_food_name(food_name)
        prefix = f"{prefix}{cleaned_food_name}/"

    client = get_s3_client()

    images: list[dict[str, Any]] = []
    continuation_token: str | None = None

    try:
        while True:
            request: dict[str, Any] = {
                "Bucket": settings.s3_bucket_name,
                "Prefix": prefix,
            }

            if continuation_token:
                request["ContinuationToken"] = continuation_token

            response = client.list_objects_v2(**request)

            for item in response.get("Contents", []):
                object_key = item["Key"]

                if object_key.endswith("/"):
                    continue

                images.append(
                    {
                        "object_key": object_key,
                        "size": item["Size"],
                        "last_modified": (
                            item["LastModified"].isoformat()
                        ),
                    }
                )

            if not response.get("IsTruncated"):
                break

            continuation_token = response.get(
                "NextContinuationToken"
            )

    except ClientError as error:
        raise RuntimeError(
            f"S3 이미지 목록 조회에 실패했습니다: {error}"
        ) from error

    return images


def get_image(object_key: str) -> dict[str, Any]:
    """
    S3 이미지의 임시 접근 URL을 생성합니다.
    """
    cleaned_key = validate_object_key(object_key)
    client = get_s3_client()

    try:
        client.head_object(
            Bucket=settings.s3_bucket_name,
            Key=cleaned_key,
        )

        image_url = client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": settings.s3_bucket_name,
                "Key": cleaned_key,
            },
            ExpiresIn=settings.s3_presigned_url_expires,
        )

    except ClientError as error:
        error_code = error.response.get(
            "Error",
            {},
        ).get("Code")

        if error_code in {
            "404",
            "NoSuchKey",
            "NotFound",
        }:
            raise FileNotFoundError(
                f"S3 이미지를 찾을 수 없습니다: {cleaned_key}"
            ) from error

        raise RuntimeError(
            f"S3 이미지 조회에 실패했습니다: {error}"
        ) from error

    return {
        "bucket": settings.s3_bucket_name,
        "object_key": cleaned_key,
        "url": image_url,
        "expires_in": settings.s3_presigned_url_expires,
    }


def get_image_bytes(object_key: str) -> bytes:
    """
    S3 이미지의 실제 바이트 데이터를 가져옵니다.
    """
    cleaned_key = validate_object_key(object_key)
    client = get_s3_client()

    try:
        response = client.get_object(
            Bucket=settings.s3_bucket_name,
            Key=cleaned_key,
        )

        return response["Body"].read()

    except ClientError as error:
        error_code = error.response.get(
            "Error",
            {},
        ).get("Code")

        if error_code in {
            "404",
            "NoSuchKey",
            "NotFound",
        }:
            raise FileNotFoundError(
                f"S3 이미지를 찾을 수 없습니다: {cleaned_key}"
            ) from error

        raise RuntimeError(
            f"S3 이미지 다운로드에 실패했습니다: {error}"
        ) from error


async def update_image(
    object_key: str,
    image: UploadFile,
) -> dict[str, Any]:
    """
    기존 S3 이미지를 새로운 이미지로 교체합니다.
    """
    validate_upload_image(image)

    cleaned_key = validate_object_key(object_key)
    image_bytes = await image.read()

    if not image_bytes:
        raise ValueError(
            "업로드된 이미지 파일이 비어 있습니다."
        )

    client = get_s3_client()

    try:
        client.head_object(
            Bucket=settings.s3_bucket_name,
            Key=cleaned_key,
        )

        client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=cleaned_key,
            Body=image_bytes,
            ContentType=image.content_type or "image/jpeg",
        )

    except ClientError as error:
        error_code = error.response.get(
            "Error",
            {},
        ).get("Code")

        if error_code in {
            "404",
            "NoSuchKey",
            "NotFound",
        }:
            raise FileNotFoundError(
                f"S3 이미지를 찾을 수 없습니다: {cleaned_key}"
            ) from error

        raise RuntimeError(
            f"S3 이미지 수정에 실패했습니다: {error}"
        ) from error

    return {
        "bucket": settings.s3_bucket_name,
        "object_key": cleaned_key,
        "updated": True,
    }


def delete_image(object_key: str) -> dict[str, Any]:
    """
    S3 이미지를 삭제합니다.
    """
    cleaned_key = validate_object_key(object_key)
    client = get_s3_client()

    try:
        client.head_object(
            Bucket=settings.s3_bucket_name,
            Key=cleaned_key,
        )

        client.delete_object(
            Bucket=settings.s3_bucket_name,
            Key=cleaned_key,
        )

    except ClientError as error:
        error_code = error.response.get(
            "Error",
            {},
        ).get("Code")

        if error_code in {
            "404",
            "NoSuchKey",
            "NotFound",
        }:
            raise FileNotFoundError(
                f"S3 이미지를 찾을 수 없습니다: {cleaned_key}"
            ) from error

        raise RuntimeError(
            f"S3 이미지 삭제에 실패했습니다: {error}"
        ) from error

    return {
        "bucket": settings.s3_bucket_name,
        "object_key": cleaned_key,
        "deleted": True,
    }