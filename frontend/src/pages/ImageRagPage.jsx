import styled from "styled-components";

import ImageRagResult from "../components/ImageRagResult";
import ImageUpload from "../components/ImageUpload";
import { useImageRagMutation } from "../query/useImageRagMutation";

function ImageRagPage() {
    const imageRagMutation = useImageRagMutation();

    const handleAnalyze = (imageFile) => {
        imageRagMutation.mutate(imageFile);
    };

    const handleImageChange = () => {
        imageRagMutation.reset();
    };

    const errorMessage =
        imageRagMutation.error?.response?.data?.detail ||
        imageRagMutation.error?.message ||
        "이미지를 분석하지 못했습니다.";

    return (
        <Page>
            <PageContainer>
                <PageHeader>
                    <Badge>IMAGE RAG</Badge>

                    <PageTitle>음식 이미지 분석</PageTitle>

                    <PageDescription>
                        업로드한 이미지를 분석하고 음식 데이터에서
                        유사한 후보를 검색합니다.
                    </PageDescription>
                </PageHeader>

                {imageRagMutation.isError && (
                    <ServerError>
                        <ErrorTitle>분석에 실패했습니다</ErrorTitle>
                        <ErrorDetail>{errorMessage}</ErrorDetail>
                    </ServerError>
                )}

                <ContentGrid>
                    <ImageUpload
                        onAnalyze={handleAnalyze}
                        onImageChange={handleImageChange}
                        isPending={imageRagMutation.isPending}
                    />

                    <ImageRagResult
                        result={imageRagMutation.data}
                    />
                </ContentGrid>
            </PageContainer>
        </Page>
    );
}

export default ImageRagPage;

const Page = styled.main`
  min-height: 100vh;
  padding: 60px 24px;
  background:
    radial-gradient(
      circle at top left,
      rgba(196, 202, 255, 0.38),
      transparent 34%
    ),
    #f5f6fa;
`;

const PageContainer = styled.div`
  width: min(1120px, 100%);
  margin: 0 auto;
`;

const PageHeader = styled.header`
  margin-bottom: 32px;
  text-align: center;
`;

const Badge = styled.span`
  display: inline-block;
  padding: 7px 12px;
  border-radius: 999px;
  background: #e7eaff;
  color: #5969cd;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 1.3px;
`;

const PageTitle = styled.h1`
  margin: 15px 0 10px;
  color: #22283b;
  font-size: clamp(32px, 5vw, 48px);
  letter-spacing: -1.8px;
`;

const PageDescription = styled.p`
  margin: 0;
  color: #747b8f;
  font-size: 16px;
  line-height: 1.7;
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 24px;
  align-items: start;

  @media (max-width: 850px) {
    grid-template-columns: 1fr;
  }
`;

const ServerError = styled.div`
  margin-bottom: 20px;
  padding: 16px 18px;
  border: 1px solid #f3c7c7;
  border-radius: 14px;
  background: #fff4f4;
`;

const ErrorTitle = styled.strong`
  display: block;
  color: #b73e3e;
  font-size: 14px;
`;

const ErrorDetail = styled.p`
  margin: 5px 0 0;
  color: #8f4d4d;
  font-size: 13px;
`;