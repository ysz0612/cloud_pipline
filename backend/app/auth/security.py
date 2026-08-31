from datetime import (
    datetime,
    timedelta,
    timezone,
)
from secrets import token_urlsafe
from typing import Any

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.config import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    회원 비밀번호를 단방향 해시로 변환합니다.
    """
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    입력한 비밀번호와 저장된 해시를 비교합니다.
    """
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    user_id: int,
) -> str:
    """
    API 인증에 사용할 Access Token을 만듭니다.
    """
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(
            minutes=(
                settings.access_token_expire_minutes
            )
        ),
        "jti": token_urlsafe(32),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(
    user_id: int,
) -> tuple[str, str]:
    """
    로그인 연장에 사용할 Refresh Token을 만듭니다.

    반환:
    (JWT Refresh Token, 토큰 고유번호)
    """
    now = datetime.now(timezone.utc)
    token_id = token_urlsafe(32)

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(
            days=settings.refresh_token_expire_days
        ),
        "jti": token_id,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token, token_id


def decode_token(
    token: str,
    expected_type: str,
) -> dict[str, Any]:
    """
    JWT의 서명, 유효기간, 토큰 종류를 검사합니다.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

    except InvalidTokenError as error:
        raise ValueError(
            "유효하지 않거나 만료된 토큰입니다."
        ) from error

    token_type = payload.get("type")
    user_id = payload.get("sub")
    token_id = payload.get("jti")

    if token_type != expected_type:
        raise ValueError(
            "잘못된 종류의 토큰입니다."
        )

    if not user_id:
        raise ValueError(
            "토큰에 사용자 정보가 없습니다."
        )

    if not token_id:
        raise ValueError(
            "토큰 고유번호가 없습니다."
        )

    return payload