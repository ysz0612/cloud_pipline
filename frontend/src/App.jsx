import {
    useEffect,
    useState,
} from "react";
import styled from "styled-components";

import Header from "./components/Header";
import ImageRagPage from "./pages/ImageRagPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";

import {
    useCurrentUserQuery,
} from "./query/useAuthQuery";


function App() {
    const [authPage, setAuthPage] =
        useState("login");

    const currentUserQuery =
        useCurrentUserQuery();

    useEffect(() => {
        const handleLogout = () => {
            setAuthPage("login");
        };

        window.addEventListener(
            "auth:logout",
            handleLogout,
        );

        return () => {
            window.removeEventListener(
                "auth:logout",
                handleLogout,
            );
        };
    }, []);

    if (
        currentUserQuery.isLoading ||
        currentUserQuery.isFetching
    ) {
        return (
            <LoadingPage>
                로그인 정보를 확인하고 있습니다.
            </LoadingPage>
        );
    }

    const user =
        currentUserQuery.data;

    if (!user) {
        if (authPage === "signup") {
            return (
                <SignupPage
                    onSignupSuccess={() => {
                        window.alert(
                            "회원가입이 완료되었습니다.",
                        );

                        setAuthPage("login");
                    }}
                    onShowLogin={() =>
                        setAuthPage("login")
                    }
                />
            );
        }

        return (
            <LoginPage
                onLoginSuccess={() =>
                    setAuthPage("login")
                }
                onShowSignup={() =>
                    setAuthPage("signup")
                }
            />
        );
    }

    return (
        <>
            <Header user={user} />
            <ImageRagPage />
        </>
    );
}


const LoadingPage = styled.div`
    min-height: 100vh;
    display: grid;
    place-items: center;
    color: #626b84;
    background: #f5f6fa;
`;

export default App;