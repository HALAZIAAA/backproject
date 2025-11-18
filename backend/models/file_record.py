# backend/models/file_record.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from models.database import Base 

class FileRecord(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(100), unique=True, index=True)
    original_name = Column(String(255))
    status = Column(String(50))          # pending, processing, done, failed
    result_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

