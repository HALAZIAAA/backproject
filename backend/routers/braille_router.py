from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import FileResponse
import tempfile, shutil, os, uuid

from services.braille_service import convert_docx_to_brf

from models.database import get_db
from models.file_record import FileRecord
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/braille")
async def convert_braille(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1) DOCX 파일만 허용
    if not file.filename.lower().endswith(".docx"):
        return {"error": "DOCX 파일만 업로드 가능합니다."}

    # 2) file_id 생성 & DB에 기록 생성 (processing 상태)
    file_id = uuid.uuid4().hex

    record = FileRecord(
        file_id=file_id,
        original_name=file.filename,
        status="processing",
        result_path=""  # 아직 결과 없음
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # 3) 업로드 파일을 임시 경로에 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # 4) 점자 변환 실행 (static 폴더에 .brf 생성)
    base_name = os.path.splitext(os.path.basename(file.filename))[0]
    brf_path = convert_docx_to_brf(
        tmp_path,
        output_dir="static",
        desired_name=base_name
    )

    # 5) DB에 결과 경로와 상태 업데이트
    record.status = "done"
    record.result_path = brf_path  # 예: "static/파일명.brf"
    db.commit()

    # 6) 최종 결과 파일 다운로드 응답
    return FileResponse(
        brf_path,
        media_type="text/plain",
        filename=os.path.basename(brf_path),
    )
