import {
    useEffect,
    useState,
} from "react";

import AuthModal from "./components/AuthModal";
import Header from "./components/Header";
import ImageRagPage from "./pages/ImageRagPage";

import {
    useCurrentUserQuery,
} from "./query/useAuthQuery";


function App() {
    const [authModalMode, setAuthModalMode] =
        useState(null);

    const currentUserQuery =
        useCurrentUserQuery();

    const user =
        currentUserQuery.data || null;

    useEffect(() => {
        const handleLogout = () => {
            setAuthModalMode(null);
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

    const handleLoginSuccess = () => {
        setAuthModalMode(null);
    };

    return (
        <>
            <Header
                user={user}
                onOpenLogin={() =>
                    setAuthModalMode(
                        "login",
                    )
                }
                onOpenSignup={() =>
                    setAuthModalMode(
                        "signup",
                    )
                }
            />

            <ImageRagPage />

            {authModalMode && (
                <AuthModal
                    key={authModalMode}
                    initialMode={
                        authModalMode
                    }
                    onClose={() =>
                        setAuthModalMode(
                            null,
                        )
                    }
                    onLoginSuccess={
                        handleLoginSuccess
                    }
                />
            )}
        </>
    );
}


export default App;