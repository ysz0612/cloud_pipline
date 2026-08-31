import styled from "styled-components";

import SignupForm from "../components/SignupForm";


function SignupPage({
                        onSignupSuccess,
                        onShowLogin,
                    }) {
    return (
        <Page>
            <Card>
                <Brand>
                    Image RAG
                </Brand>

                <SignupForm
                    onSignupSuccess={
                        onSignupSuccess
                    }
                    onShowLogin={
                        onShowLogin
                    }
                />
            </Card>
        </Page>
    );
}


const Page = styled.main`
    min-height: 100vh;
    display: grid;
    place-items: center;
    padding: 32px 20px;
    background:
        radial-gradient(
            circle at top right,
            rgba(91, 107, 216, 0.16),
            transparent 34%
        ),
        #f5f6fa;
`;

const Card = styled.section`
    width: min(460px, 100%);
    padding: 38px 42px;
    border: 1px solid #e5e7ef;
    border-radius: 24px;
    background: #ffffff;
    box-shadow:
        0 24px 70px
        rgba(38, 47, 82, 0.1);

    @media (max-width: 520px) {
        padding: 30px 22px;
    }
`;

const Brand = styled.div`
    margin-bottom: 30px;
    color: #5969d7;
    font-size: 18px;
    font-weight: 800;
`;

export default SignupPage;