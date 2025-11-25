# backend/main.py

from fastapi import FastAPI
from routers import process_router
from fastapi.middleware.cors import CORSMiddleware
from routers import process_router, braille_router
from fastapi.staticfiles import StaticFiles
import os
from models.database import Base, engine
from models import file_record

app = FastAPI(title="Lecture Material Converter")

# static 폴더 자동 생성
if not os.path.exists("static"):
    os.makedirs("static")

# /static 경로로 정적 파일 제공
app.mount("/static", StaticFiles(directory="static"), name="static")

# React와 연결용 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중에는 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 테이블 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(process_router.router)
app.include_router(braille_router.router)

@app.get("/")
def root():
    return {"message": "Backend server is running!"}
