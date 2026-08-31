import { useState } from "react";
import styled from "styled-components";

import LoginForm from "./LoginForm";
import SignupForm from "./SignupForm";


function AuthModal({
                       initialMode = "login",
                       onClose,
                       onLoginSuccess,
                   }) {
    const [mode, setMode] =
        useState(initialMode);

    const handleBackdropClick = (
        event,
    ) => {
        if (
            event.target ===
            event.currentTarget
        ) {
            onClose();
        }
    };

    const handleSignupSuccess = () => {
        window.alert(
            "회원가입이 완료되었습니다. 로그인해 주세요.",
        );

        setMode("login");
    };

    return (
        <Backdrop
            onMouseDown={
                handleBackdropClick
            }
        >
            <Modal>
                <CloseButton
                    type="button"
                    aria-label="닫기"
                    onClick={onClose}
                >
                    ×
                </CloseButton>

                {mode === "login" ? (
                    <LoginForm
                        onLoginSuccess={
                            onLoginSuccess
                        }
                        onShowSignup={() =>
                            setMode("signup")
                        }
                    />
                ) : (
                    <SignupForm
                        onSignupSuccess={
                            handleSignupSuccess
                        }
                        onShowLogin={() =>
                            setMode("login")
                        }
                    />
                )}
            </Modal>
        </Backdrop>
    );
}


const Backdrop = styled.div`
    position: fixed;
    inset: 0;
    z-index: 1000;
    display: grid;
    place-items: center;
    padding: 24px;
    overflow-y: auto;
    background: rgba(22, 28, 48, 0.52);
    backdrop-filter: blur(5px);
`;

const Modal = styled.section`
    position: relative;
    width: min(460px, 100%);
    max-height: calc(100vh - 48px);
    padding: 42px;
    overflow-y: auto;
    border: 1px solid
        rgba(255, 255, 255, 0.75);
    border-radius: 24px;
    background: #ffffff;
    box-shadow:
        0 30px 90px
        rgba(20, 26, 52, 0.25);

    @media (max-width: 520px) {
        padding: 36px 22px 28px;
    }
`;

const CloseButton = styled.button`
    position: absolute;
    top: 16px;
    right: 18px;
    width: 36px;
    height: 36px;
    padding: 0;
    border: 0;
    border-radius: 50%;
    color: #697087;
    background: #f2f3f8;
    font-size: 26px;
    line-height: 1;
    cursor: pointer;

    &:hover {
        color: #27304c;
        background: #e7e9f2;
    }
`;

export default AuthModal;