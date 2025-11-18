# 데이터베이스 파일
# CREATE DATABASE indpro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database

# MySQL 연결 (각자 맞게 root/password 1234 자기 비밀번호로 수정해)
DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/indpro?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
    echo=True,          # SQL 로그 출력 여부(원하면 False)
    pool_pre_ping=True  # 끊어진 연결 자동 복구
)

# DB 없으면 자동 생성
if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# 의존성으로 사용할 DB 세션
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
