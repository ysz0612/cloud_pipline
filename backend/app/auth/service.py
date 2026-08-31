from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.schema import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.config import settings
from app.redis_client import redis_client
from app.users.model import User


def get_refresh_key(token_id: str) -> str:
    """
    Redis에 저장할 Refresh Token 키를 만듭니다.
    """
    return f"auth:refresh:{token_id}"


def create_user(
    db: Session,
    request: SignupRequest,
) -> User:
    """
    새로운 회원을 RDS에 저장합니다.
    """
    normalized_username = (
        request.username.strip().lower()
    )

    normalized_email = (
        request.email.strip().lower()
    )

    existing_user = db.scalar(
        select(User).where(
            or_(
                User.username == normalized_username,
                User.email == normalized_email,
            )
        )
    )

    if existing_user:
        if (
            existing_user.username
            == normalized_username
        ):
            raise ValueError(
                "이미 사용 중인 아이디입니다."
            )

        raise ValueError(
            "이미 사용 중인 이메일입니다."
        )

    user = User(
        username=normalized_username,
        email=normalized_email,
        password_hash=hash_password(
            request.password
        ),
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except IntegrityError as error:
        db.rollback()

        raise ValueError(
            "이미 등록된 회원정보입니다."
        ) from error

    return user


def authenticate_user(
    db: Session,
    request: LoginRequest,
) -> User:
    """
    아이디와 비밀번호를 확인합니다.
    """
    normalized_username = (
        request.username.strip().lower()
    )

    user = db.scalar(
        select(User).where(
            User.username == normalized_username
        )
    )

    if user is None:
        raise ValueError(
            "아이디 또는 비밀번호가 올바르지 않습니다."
        )

    if not verify_password(
        request.password,
        user.password_hash,
    ):
        raise ValueError(
            "아이디 또는 비밀번호가 올바르지 않습니다."
        )

    if not user.is_active:
        raise ValueError(
            "비활성화된 계정입니다."
        )

    return user


async def issue_tokens(
    user: User,
) -> TokenResponse:
    """
    Access Token과 Refresh Token을 발급하고
    Refresh Token 정보를 Redis에 저장합니다.
    """
    access_token = create_access_token(
        user.id
    )

    refresh_token, token_id = (
        create_refresh_token(user.id)
    )

    redis_key = get_refresh_key(token_id)

    expire_seconds = (
        settings.refresh_token_expire_days
        * 24
        * 60
        * 60
    )

    await redis_client.set(
        redis_key,
        str(user.id),
        ex=expire_seconds,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


async def refresh_access_token(
    refresh_token: str,
) -> str:
    """
    Redis에 유효한 Refresh Token인지 확인한 뒤
    새로운 Access Token을 발급합니다.
    """
    payload = decode_token(
        refresh_token,
        expected_type="refresh",
    )

    user_id = int(payload["sub"])
    token_id = payload["jti"]

    redis_key = get_refresh_key(token_id)

    stored_user_id = await redis_client.get(
        redis_key
    )

    if stored_user_id is None:
        raise ValueError(
            "로그아웃되었거나 만료된 토큰입니다."
        )

    if stored_user_id != str(user_id):
        raise ValueError(
            "Refresh Token의 사용자 정보가 "
            "일치하지 않습니다."
        )

    return create_access_token(user_id)


async def revoke_refresh_token(
    refresh_token: str,
) -> None:
    """
    로그아웃할 때 Redis에서 Refresh Token을 삭제합니다.
    """
    payload = decode_token(
        refresh_token,
        expected_type="refresh",
    )

    token_id = payload["jti"]

    await redis_client.delete(
        get_refresh_key(token_id)
    )