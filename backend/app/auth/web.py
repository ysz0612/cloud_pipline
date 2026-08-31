from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
)
from app.auth.schema import (
    AccessTokenResponse,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.auth.service import (
    authenticate_user,
    create_user,
    issue_tokens,
    refresh_access_token,
    revoke_refresh_token,
)
from app.database import get_db
from app.users.model import User


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    request: SignupRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    """
    회원가입
    """
    try:
        return create_user(
            db=db,
            request=request,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    request: LoginRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    """
    로그인 및 토큰 발급
    """
    try:
        user = authenticate_user(
            db=db,
            request=request,
        )

        return await issue_tokens(user)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 처리 중 오류가 발생했습니다: {error}",
        ) from error


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
)
async def refresh(
    request: RefreshTokenRequest,
):
    """
    Access Token 재발급
    """
    try:
        access_token = await refresh_access_token(
            request.refresh_token
        )

        return AccessTokenResponse(
            access_token=access_token,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error


@router.post(
    "/logout",
    response_model=MessageResponse,
)
async def logout(
    request: LogoutRequest,
):
    """
    Redis에서 Refresh Token을 삭제합니다.
    """
    try:
        await revoke_refresh_token(
            request.refresh_token
        )

        return MessageResponse(
            message="로그아웃되었습니다.",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    """
    현재 로그인 사용자 조회
    """
    return current_user