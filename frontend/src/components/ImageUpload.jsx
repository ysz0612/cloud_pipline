import { useEffect, useRef, useState } from "react";
import styled from "styled-components";

const ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
];

function ImageUpload({
                         onAnalyze,
                         isPending,
                         onImageChange,
                     }) {
    const inputRef = useRef(null);

    const [selectedImage, setSelectedImage] = useState(null);
    const [previewUrl, setPreviewUrl] = useState("");
    const [validationError, setValidationError] =
        useState("");

    useEffect(() => {
        return () => {
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }
        };
    }, [previewUrl]);

    const handleImageChange = (event) => {
        const file = event.target.files?.[0];

        setValidationError("");

        if (!file) {
            return;
        }

        if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
            setSelectedImage(null);
            setPreviewUrl("");
            setValidationError(
                "JPG, PNG, WEBP 이미지만 선택할 수 있습니다.",
            );

            event.target.value = "";
            return;
        }

        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
        }

        const newPreviewUrl = URL.createObjectURL(file);

        setSelectedImage(file);
        setPreviewUrl(newPreviewUrl);

        if (onImageChange) {
            onImageChange();
        }
    };

    const handleSelectClick = () => {
        if (!isPending) {
            inputRef.current?.click();
        }
    };

    const handleSubmit = (event) => {
        event.preventDefault();

        if (!selectedImage) {
            setValidationError(
                "분석할 음식 이미지를 먼저 선택해주세요.",
            );
            return;
        }

        onAnalyze(selectedImage);
    };

    return (
        <UploadCard>
            <SectionTitle>음식 이미지 업로드</SectionTitle>

            <SectionDescription>
                음식 사진을 올리면 기존 음식 정보를 검색한 후
                음식 종류를 분석합니다.
            </SectionDescription>

            <Form onSubmit={handleSubmit}>
                <HiddenInput
                    ref={inputRef}
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={handleImageChange}
                />

                <ImageArea
                    type="button"
                    onClick={handleSelectClick}
                    disabled={isPending}
                >
                    {previewUrl ? (
                        <PreviewImage
                            src={previewUrl}
                            alt="선택한 음식 미리보기"
                        />
                    ) : (
                        <EmptyPreview>
                            <UploadIcon>＋</UploadIcon>
                            <EmptyTitle>음식 사진 선택</EmptyTitle>
                            <EmptyText>
                                JPG, PNG, WEBP 파일을 올려주세요.
                            </EmptyText>
                        </EmptyPreview>
                    )}
                </ImageArea>

                {selectedImage && (
                    <FileInformation>
                        <FileName>{selectedImage.name}</FileName>

                        <ChangeButton
                            type="button"
                            onClick={handleSelectClick}
                            disabled={isPending}
                        >
                            사진 변경
                        </ChangeButton>
                    </FileInformation>
                )}

                {validationError && (
                    <ErrorMessage>{validationError}</ErrorMessage>
                )}

                <AnalyzeButton
                    type="submit"
                    disabled={!selectedImage || isPending}
                >
                    {isPending ? "이미지 분석 중..." : "음식 분석하기"}
                </AnalyzeButton>
            </Form>
        </UploadCard>
    );
}

export default ImageUpload;

const UploadCard = styled.section`
  width: 100%;
  padding: 28px;
  border: 1px solid #e7e9ef;
  border-radius: 24px;
  background: #ffffff;
  box-shadow: 0 16px 40px rgba(33, 43, 77, 0.08);
`;

const SectionTitle = styled.h2`
  margin: 0;
  color: #20263a;
  font-size: 22px;
`;

const SectionDescription = styled.p`
  margin: 10px 0 24px;
  color: #70778c;
  font-size: 14px;
  line-height: 1.6;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const HiddenInput = styled.input`
  display: none;
`;

const ImageArea = styled.button`
  width: 100%;
  height: 320px;
  padding: 0;
  overflow: hidden;
  border: 2px dashed #cad0df;
  border-radius: 20px;
  background: #f8f9fc;
  cursor: pointer;
  transition:
    border-color 0.2s,
    background 0.2s;

  &:hover:not(:disabled) {
    border-color: #6878d6;
    background: #f2f3ff;
  }

  &:disabled {
    cursor: wait;
    opacity: 0.7;
  }
`;

const PreviewImage = styled.img`
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #f5f6fa;
`;

const EmptyPreview = styled.div`
  display: flex;
  height: 100%;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`;

const UploadIcon = styled.span`
  display: flex;
  width: 58px;
  height: 58px;
  margin-bottom: 14px;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  background: #e9ebff;
  color: #5969cd;
  font-size: 36px;
  font-weight: 300;
`;

const EmptyTitle = styled.strong`
  color: #31384e;
  font-size: 17px;
`;

const EmptyText = styled.span`
  margin-top: 7px;
  color: #9197a8;
  font-size: 13px;
`;

const FileInformation = styled.div`
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
`;

const FileName = styled.span`
  overflow: hidden;
  color: #555d72;
  font-size: 14px;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const ChangeButton = styled.button`
  flex-shrink: 0;
  border: 0;
  background: transparent;
  color: #5969cd;
  font-weight: 700;
  cursor: pointer;

  &:disabled {
    cursor: wait;
    opacity: 0.6;
  }
`;

const ErrorMessage = styled.p`
  margin: 0;
  color: #d14343;
  font-size: 14px;
`;

const AnalyzeButton = styled.button`
  min-height: 52px;
  border: 0;
  border-radius: 15px;
  background: #5969cd;
  color: #ffffff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition:
    background 0.2s,
    transform 0.2s;

  &:hover:not(:disabled) {
    background: #4959bf;
    transform: translateY(-1px);
  }

  &:disabled {
    background: #c7cada;
    cursor: not-allowed;
  }
`;