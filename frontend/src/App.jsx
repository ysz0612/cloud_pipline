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
    const [
        authModalMode,
        setAuthModalMode,
    ] = useState(null);

    const currentUserQuery =
        useCurrentUserQuery();

    const user =
        currentUserQuery.data || null;

    useEffect(() => {
        const handleLogout = () => {
            setAuthModalMode(null);
        };

        const handleAuthRequired = () => {
            setAuthModalMode("login");
        };

        window.addEventListener(
            "auth:logout",
            handleLogout,
        );

        window.addEventListener(
            "auth:required",
            handleAuthRequired,
        );

        return () => {
            window.removeEventListener(
                "auth:logout",
                handleLogout,
            );

            window.removeEventListener(
                "auth:required",
                handleAuthRequired,
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