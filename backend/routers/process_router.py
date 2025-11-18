from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import FileResponse
import tempfile, shutil, os

from services.vlm_service import convert_to_text_and_docx_with_vlm
from models.file_record import FileRecord
from models.database import get_db
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
import uuid

router = APIRouter()

# -------------------------------
# 1) 파일 변환 API (기존)
# -------------------------------
@router.post("/process")
async def process_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_id = uuid.uuid4().hex

    record = FileRecord(
        file_id=file_id,
        original_name=file.filename,
        status="processing",
        result_path=""
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    docx_path = convert_to_text_and_docx_with_vlm(
        tmp_path,
        output_dir="static",
        desired_name=os.path.splitext(file.filename)[0]
    )

    record.status = "done"
    record.result_path = docx_path
    db.commit()

    return FileResponse(
        docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=os.path.basename(docx_path),
    )

# -------------------------------
# 2) 상태 조회 API (추가)
# -------------------------------
@router.get("/status/{file_id}")
def check_status(file_id: str, db: Session = Depends(get_db)):
    record = db.query(FileRecord).filter(FileRecord.file_id == file_id).first()
    if not record:
        return {"error": "File not found"}

    return {
        "file_id": record.file_id,
        "status": record.status,
        "path": record.result_path
    }

    