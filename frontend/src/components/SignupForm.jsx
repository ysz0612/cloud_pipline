import { useState } from "react";
import styled from "styled-components";

import {
    useSignupMutation,
} from "../query/useAuthQuery";


function getErrorMessage(error) {
    return (
        error?.response?.data?.detail ||
        error?.message ||
        "회원가입에 실패했습니다."
    );
}


function SignupForm({
                        onSignupSuccess,
                        onShowLogin,
                    }) {
    const [username, setUsername] =
        useState("");

    const [email, setEmail] =
        useState("");

    const [password, setPassword] =
        useState("");

    const [
        passwordConfirm,
        setPasswordConfirm,
    ] = useState("");

    const [formError, setFormError] =
        useState("");

    const signupMutation =
        useSignupMutation();

    const handleSubmit = (event) => {
        event.preventDefault();
        setFormError("");

        if (password !== passwordConfirm) {
            setFormError(
                "비밀번호가 일치하지 않습니다.",
            );

            return;
        }

        signupMutation.mutate(
            {
                username,
                email,
                password,
            },
            {
                onSuccess: () => {
                    onSignupSuccess();
                },
            },
        );
    };

    const errorMessage =
        formError ||
        (
            signupMutation.isError
                ? getErrorMessage(
                    signupMutation.error,
                )
                : ""
        );

    return (
        <Form onSubmit={handleSubmit}>
            <Title>회원가입</Title>

            <Description>
                계정을 만들고 음식 이미지
                분석을 시작해 보세요.
            </Description>

            <Field>
                <Label htmlFor="signup-username">
                    아이디
                </Label>

                <Input
                    id="signup-username"
                    type="text"
                    value={username}
                    placeholder="영문, 숫자, 밑줄 사용"
                    minLength={3}
                    maxLength={50}
                    autoComplete="username"
                    onChange={(event) => {
                        setUsername(
                            event.target.value,
                        );
                    }}
                    required
                />
            </Field>

            <Field>
                <Label htmlFor="signup-email">
                    이메일
                </Label>

                <Input
                    id="signup-email"
                    type="email"
                    value={email}
                    placeholder="example@email.com"
                    autoComplete="email"
                    onChange={(event) => {
                        setEmail(
                            event.target.value,
                        );
                    }}
                    required
                />
            </Field>

            <Field>
                <Label htmlFor="signup-password">
                    비밀번호
                </Label>

                <Input
                    id="signup-password"
                    type="password"
                    value={password}
                    placeholder="8자 이상 입력"
                    minLength={8}
                    maxLength={128}
                    autoComplete="new-password"
                    onChange={(event) => {
                        setPassword(
                            event.target.value,
                        );
                    }}
                    required
                />
            </Field>

            <Field>
                <Label htmlFor="password-confirm">
                    비밀번호 확인
                </Label>

                <Input
                    id="password-confirm"
                    type="password"
                    value={passwordConfirm}
                    placeholder="비밀번호 다시 입력"
                    minLength={8}
                    maxLength={128}
                    autoComplete="new-password"
                    onChange={(event) => {
                        setPasswordConfirm(
                            event.target.value,
                        );
                    }}
                    required
                />
            </Field>

            {errorMessage && (
                <ErrorMessage>
                    {errorMessage}
                </ErrorMessage>
            )}

            <SubmitButton
                type="submit"
                disabled={
                    signupMutation.isPending
                }
            >
                {signupMutation.isPending
                    ? "가입 중..."
                    : "회원가입"}
            </SubmitButton>

            <SwitchText>
                이미 계정이 있으신가요?

                <TextButton
                    type="button"
                    onClick={onShowLogin}
                >
                    로그인
                </TextButton>
            </SwitchText>
        </Form>
    );
}


const Form = styled.form`
    width: 100%;
`;

const Title = styled.h1`
    margin: 0 0 12px;
    color: #19213a;
    font-size: 32px;
`;

const Description = styled.p`
    margin: 0 0 28px;
    color: #71788d;
    line-height: 1.6;
`;

const Field = styled.div`
    margin-bottom: 16px;
`;

const Label = styled.label`
    display: block;
    margin-bottom: 8px;
    color: #30384f;
    font-size: 14px;
    font-weight: 700;
`;

const Input = styled.input`
    width: 100%;
    height: 50px;
    padding: 0 16px;
    border: 1px solid #dfe2ec;
    border-radius: 12px;
    outline: none;
    color: #22283b;
    background: #ffffff;

    &:focus {
        border-color: #5b6bd8;
        box-shadow:
            0 0 0 4px
            rgba(91, 107, 216, 0.12);
    }
`;

const ErrorMessage = styled.div`
    margin-bottom: 16px;
    padding: 12px 14px;
    border-radius: 10px;
    color: #c33d4a;
    background: #fff0f1;
    font-size: 14px;
`;

const SubmitButton = styled.button`
    width: 100%;
    height: 52px;
    border: 0;
    border-radius: 12px;
    color: #ffffff;
    background: #5b6bd8;
    font-weight: 700;
    cursor: pointer;

    &:hover {
        background: #4c5cc9;
    }

    &:disabled {
        cursor: not-allowed;
        opacity: 0.65;
    }
`;

const SwitchText = styled.div`
    margin-top: 22px;
    color: #777e90;
    text-align: center;
    font-size: 14px;
`;

const TextButton = styled.button`
    margin-left: 8px;
    padding: 0;
    border: 0;
    color: #5364d5;
    background: transparent;
    font-weight: 700;
    cursor: pointer;
`;

export default SignupForm;