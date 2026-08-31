import { useState } from "react";
import styled from "styled-components";

import { useSignupMutation } from "../query/useAuthQuery";


function SignupForm({
                        onSignupSuccess,
                        onMoveToLogin,
                    }) {
    const [username, setUsername] =
        useState("");

    const [email, setEmail] =
        useState("");

    const [password, setPassword] =
        useState("");

    const [passwordConfirm, setPasswordConfirm] =
        useState("");

    const [validationError, setValidationError] =
        useState("");

    const signupMutation =
        useSignupMutation();

    const handleSubmit = (event) => {
        event.preventDefault();

        setValidationError("");

        if (password !== passwordConfirm