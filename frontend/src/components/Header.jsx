import styled from "styled-components";

import {
    useLogoutMutation,
} from "../query/useAuthQuery";


function Header({ user }) {
    const logoutMutation =
        useLogoutMutation();

    return (
        <Container>
            <Inner>
                <Logo>
                    Image RAG
                </Logo>

                <UserArea>
                    <Username>
                        {user.username}님
                    </Username>

                    <LogoutButton
                        type="button"
                        disabled={
                            logoutMutation.isPending
                        }
                        onClick={() =>
                            logoutMutation.mutate()
                        }
                    >
                        로그아웃
                    </LogoutButton>
                </UserArea>
            </Inner>
        </Container>
    );
}


const Container = styled.header`
    position: relative;
    z-index: 10;
    border-bottom: 1px solid #e5e7ef;
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(12px);
`;

const Inner = styled.div`
    width: min(1120px, calc(100% - 40px));
    height: 68px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
`;

const Logo = styled.div`
    color: #28314d;
    font-size: 20px;
    font-weight: 800;
`;

const UserArea = styled.div`
    display: flex;
    align-items: center;
    gap: 16px;
`;

const Username = styled.span`
    color: #51596f;
    font-size: 14px;
    font-weight: 700;
`;

const LogoutButton = styled.button`
    padding: 9px 15px;
    border: 1px solid #dfe2ec;
    border-radius: 10px;
    color: #4d566f;
    background: #ffffff;
    cursor: pointer;

    &:hover {
        color: #5364d5;
        border-color: #9ca7ea;
    }

    &:disabled {
        cursor: not-allowed;
        opacity: 0.6;
    }
`;

export default Header;