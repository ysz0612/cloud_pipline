import { useState } from "react";
import styled from "styled-components";

import { useLoginMutation } from "../query/useAuthQuery";


function LoginForm({
                       onLoginSuccess,
                       onMoveToSignup,
                   }) {
    const [username, setUsername] =
        useState("");

    const [password, setPassword] =
        useState("");

    const loginMutation =
        useLoginMutation();

    const handleSubmit = (event) => {
        event.preventDefault();

        loginMutation.mutate(
            {
                username,
                password,
            },
            {
                onSuccess: () => {
                    onLoginSuccess();
                },
            },
        );
    };

    const errorMessage =
        loginMutation.error?.response
            ?.data?.detail ||
        loginMutation.error?.message;

    return (
        <Form onSubmit={handleSubmit}>
            <Field>
                <Label htmlFor="username">
                    아이디
                </Label>

                <Input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(event) =>
                        setUsername(
                            event.target.value,
                        )
                    }
                    placeholder="아이디를 입력하세요"
                    autoComplete="username"
                    required
                />
            </Field>

            <Field>
                <Label htmlFor="password">
                    비밀번호
                </Label>

                <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(event) =>
                        setPassword(
                            event.target.value,
                        )
                    }
                    placeholder="비밀번호를 입력하세요"
                    autoComplete="current-password"
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
                disabled={loginMutation.isPending}
            >
                {loginMutation.isPending
                    ? "로그인 중..."
                    : "로그인"}
            </SubmitButton>

            <MoveButton
                type="button"
                onClick={onMoveToSignup}
            >
                아직 회원이 아니신가요?
                회원가입
            </MoveButton>
        </Form>
    );
}


const Form = styled.form`
    display: flex;
    flex-direction: column;
    gap: 20px;
`;

const Field = styled.div`
    display: flex;
    flex-direction: column;
    gap: 8px;
`;

const Label = styled.label`
    color: #28324a;
    font-size: 14px;
    font-weight: 700;
`;

const Input = styled.input`
    width: 100%;
    height: 52px;
    padding: 0 16px;
    border: 1px solid #dce1ec;
    border-radius: 12px;
    background: #ffffff;
    color: #1f2940;
    outline: none;
    transition: 0.2s;

    &:focus {
        border-color: #5d6bd8;
        box-shadow:
            0 0 0 3px
            rgba(93, 107, 216, 0.12);
    }

    &::placeholder {
        color: #a3a9b8;
    }
`;

const SubmitButton = styled.button`
    width: 100%;
    height: 52px;
    border: 0;
    border-radius: 12px;
    background: #5d6bd8;
    color: #ffffff;
    font-weight: 800;
    cursor: pointer;

    &:hover:not(:disabled) {
        background: #4f5dc9;
    }

    &:disabled {
        cursor: not-allowed;
        opacity: 0.65;
    }
`;

const MoveButton = styled.button`
    border: 0;
    background: transparent;
    color: #5d6bd8;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
`;

const ErrorMessage = styled.div`
    padding: 12px 14px;
    border-radius: 10px;
    background: #fff0f0;
    color: #d14343;
    font-size: 14px;
`;


export default LoginForm;