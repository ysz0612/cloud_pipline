import styled from "styled-components";


function ImageRagResult({ result }) {
    if (!result) {
        return (
            <EmptyResult>
                <EmptyEmoji>🍽️</EmptyEmoji>

                <EmptyResultTitle>
                    아직 분석 결과가 없습니다
                </EmptyResultTitle>

                <EmptyResultText>
                    음식 이미지를 선택하고 분석 버튼을 눌러주세요.
                </EmptyResultText>
            </EmptyResult>
        );
    }

    const confidence = Number(
        result.confidence,
    );

    const confidencePercent = Number.isFinite(
        confidence,
    )
        ? Math.max(
            0,
            Math.min(
                100,
                Math.round(confidence * 100),
            ),
        )
        : 0;

    const candidates = Array.isArray(
        result.candidates,
    )
        ? result.candidates
        : [];

    return (
        <ResultCard>
            <ResultHeader>
                <HeaderLabel>분석 결과</HeaderLabel>

                <Confidence>
                    신뢰도 {confidencePercent}%
                </Confidence>
            </ResultHeader>

            <FoodName>
                {result.predicted_food ||
                    "알 수 없는 음식"}
            </FoodName>

            <ReasonBox>
                <BoxTitle>판단 이유</BoxTitle>

                <BoxContent>
                    {result.reason ||
                        "판단 이유를 불러오지 못했습니다."}
                </BoxContent>
            </ReasonBox>

            <DescriptionBox>
                <BoxTitle>음식 특징</BoxTitle>

                <BoxContent>
                    {result.image_description ||
                        "음식 특징을 불러오지 못했습니다."}
                </BoxContent>
            </DescriptionBox>

            {candidates.length > 0 && (
                <CandidateSection>
                    <CandidateTitle>
                        검색된 유사 음식
                    </CandidateTitle>

                    <CandidateList>
                        {candidates.map(
                            (candidate, index) => {
                                const similarity = Number(
                                    candidate?.similarity,
                                );

                                const similarityPercent =
                                    Number.isFinite(similarity)
                                        ? Math.max(
                                            0,
                                            Math.min(
                                                100,
                                                Math.round(
                                                    similarity * 100,
                                                ),
                                            ),
                                        )
                                        : 0;

                                const foodName =
                                    candidate?.food_name ||
                                    "알 수 없는 음식";

                                const candidateKey =
                                    candidate?.object_key ||
                                    `${foodName}-${index}`;

                                return (
                                    <CandidateItem
                                        key={candidateKey}
                                    >
                                        <CandidateRank>
                                            {index + 1}
                                        </CandidateRank>

                                        <CandidateInformation>
                                            <CandidateName>
                                                {foodName}
                                            </CandidateName>

                                            <SimilarityTrack>
                                                <SimilarityBar
                                                    $percent={
                                                        similarityPercent
                                                    }
                                                />
                                            </SimilarityTrack>
                                        </CandidateInformation>

                                        <SimilarityText>
                                            {similarityPercent}%
                                        </SimilarityText>
                                    </CandidateItem>
                                );
                            },
                        )}
                    </CandidateList>
                </CandidateSection>
            )}
        </ResultCard>
    );
}


export default ImageRagResult;


const ResultCard = styled.section`
    width: 100%;
    padding: 28px;
    border: 1px solid #e7e9ef;
    border-radius: 24px;
    background: #ffffff;
    box-shadow: 0 16px 40px
    rgba(33, 43, 77, 0.08);
`;

const ResultHeader = styled.div`
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
`;

const HeaderLabel = styled.span`
    color: #767d91;
    font-size: 14px;
    font-weight: 700;
`;

const Confidence = styled.span`
    flex-shrink: 0;
    padding: 7px 11px;
    border-radius: 999px;
    background: #edf8f1;
    color: #318757;
    font-size: 13px;
    font-weight: 700;
`;

const FoodName = styled.h2`
    margin: 14px 0 24px;
    color: #262d44;
    font-size: 36px;
    letter-spacing: -1px;
    word-break: keep-all;
`;

const ReasonBox = styled.div`
    padding: 18px;
    border-radius: 16px;
    background: #f3f4ff;
`;

const DescriptionBox = styled.div`
    margin-top: 14px;
    padding: 18px;
    border-radius: 16px;
    background: #f7f8fb;
`;

const BoxTitle = styled.h3`
    margin: 0 0 8px;
    color: #424a62;
    font-size: 14px;
`;

const BoxContent = styled.p`
    margin: 0;
    color: #626a7e;
    font-size: 14px;
    line-height: 1.7;
    white-space: pre-line;
    word-break: keep-all;
`;

const CandidateSection = styled.div`
    margin-top: 26px;
`;

const CandidateTitle = styled.h3`
    margin: 0 0 14px;
    color: #353c52;
    font-size: 17px;
`;

const CandidateList = styled.div`
    display: flex;
    flex-direction: column;
    gap: 12px;
`;

const CandidateItem = styled.div`
    display: flex;
    align-items: center;
    gap: 12px;
`;

const CandidateRank = styled.span`
    display: flex;
    width: 28px;
    height: 28px;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    border-radius: 9px;
    background: #eaecf8;
    color: #5969cd;
    font-size: 13px;
    font-weight: 800;
`;

const CandidateInformation = styled.div`
    min-width: 0;
    flex: 1;
`;

const CandidateName = styled.span`
    display: block;
    margin-bottom: 7px;
    overflow: hidden;
    color: #4b5369;
    font-size: 14px;
    font-weight: 700;
    text-overflow: ellipsis;
    white-space: nowrap;
`;

const SimilarityTrack = styled.div`
    height: 7px;
    overflow: hidden;
    border-radius: 999px;
    background: #eceef3;
`;

const SimilarityBar = styled.div`
    width: ${({ $percent }) =>
            `${$percent}%`};
    height: 100%;
    border-radius: inherit;
    background: #6878d6;
    transition: width 0.5s ease;
`;

const SimilarityText = styled.span`
    width: 42px;
    flex-shrink: 0;
    color: #70778b;
    font-size: 13px;
    text-align: right;
`;

const EmptyResult = styled.section`
    display: flex;
    width: 100%;
    min-height: 400px;
    padding: 28px;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 1px solid #e7e9ef;
    border-radius: 24px;
    background: #ffffff;
    box-shadow: 0 16px 40px
    rgba(33, 43, 77, 0.08);
    text-align: center;
`;

const EmptyEmoji = styled.span`
    font-size: 52px;
`;

const EmptyResultTitle = styled.h2`
    margin: 18px 0 8px;
    color: #353c52;
    font-size: 20px;
`;

const EmptyResultText = styled.p`
    margin: 0;
    color: #8b91a2;
    font-size: 14px;
    line-height: 1.6;
`;