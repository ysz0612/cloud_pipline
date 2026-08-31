import styled from "styled-components";

import {
    useLogoutMutation,
} from "../query/useAuthQuery";


function Header({
                    user,
                    onOpenLogin,
                    onOpenSignup,
                }) {
    const logoutMutation =
        useLogoutMutation();

    return (
        <Container>
            <Inner>
                <Logo>
                    Image RAG
                </Logo>

                {user ? (
                    <UserArea>
                        <Username>
                            {user.username}님
                        </Username>

                        <LogoutButton
                            type="button"
                            disabled={
                                logoutMutation
                                    .isPending
                            }
                            onClick={() =>
                                logoutMutation
                                    .mutate()
                            }
                        >
                            {logoutMutation.isPending
                                ? "로그아웃 중"
                                : "로그아웃"}
                        </LogoutButton>
                    </UserArea>
                ) : (
                    <ButtonArea>
                        <LoginButton
                            type="button"
                            onClick={
                                onOpenLogin
                            }
                        >
                            로그인
                        </LoginButton>

                        <SignupButton
                            type="button"
                            onClick={
                                onOpenSignup
                            }
                        >
                            회원가입
                        </SignupButton>
                    </ButtonArea>
                )}
            </Inner>
        </Container>
    );
}


const Container = styled.header`
    position: relative;
    z-index: 100;
    border-bottom: 1px solid #e5e7ef;
    background: rgba(255, 255, 255, 0.94);
    backdrop-filter: blur(12px);
`;

const Inner = styled.div`
    width: min(
            1120px,
            calc(100% - 40px)
    );
    height: 68px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
`;

const Logo = styled.div`
    color: #27304b;
    font-size: 20px;
    font-weight: 800;
`;

const UserArea = styled.div`
    display: flex;
    align-items: center;
    gap: 14px;
`;

const ButtonArea = styled.div`
    display: flex;
    align-items: center;
    gap: 10px;
`;

const Username = styled.span`
    color: #51596f;
    font-size: 14px;
    font-weight: 700;
`;

const LoginButton = styled.button`
    height: 40px;
    padding: 0 17px;
    border: 1px solid #dfe2ec;
    border-radius: 10px;
    color: #4d566f;
    background: #ffffff;
    font-weight: 700;
    cursor: pointer;

    &:hover {
        color: #5364d5;
        border-color: #9ca7ea;
    }
`;

const SignupButton = styled.button`
    height: 40px;
    padding: 0 18px;
    border: 0;
    border-radius: 10px;
    color: #ffffff;
    background: #5b6bd8;
    font-weight: 700;
    cursor: pointer;

    &:hover {
        background: #4c5cc9;
    }
`;

const LogoutButton = styled.button`
    height: 40px;
    padding: 0 16px;
    border: 1px solid #dfe2ec;
    border-radius: 10px;
    color: #4d566f;
    background: #ffffff;
    font-weight: 700;
    cursor: pointer;

    &:hover {
        color: #c24752;
        border-color: #e9b6ba;
    }

    &:disabled {
        cursor: not-allowed;
        opacity: 0.6;
    }
`;

export default Header;