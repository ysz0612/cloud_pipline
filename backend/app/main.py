from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.imageRag.web import router as image_rag_router


app = FastAPI(
    title="Image RAG API",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(image_rag_router)


@app.get("/")
def root():
    return {
        "message": "Image RAG API 실행 중"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }