# backend/routers/process_router.py

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import tempfile, shutil, os
from services.convert_service import convert_to_text_and_docx

router = APIRouter()

@router.post("/process")
async def process_file(file: UploadFile = File(...)):
    # 임시 저장
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # 원본 파일명(확장자 제외) 추출 → 원하는 저장 이름으로 사용
    original_stem = os.path.splitext(os.path.basename(file.filename))[0]

    txt_path, docx_path = convert_to_text_and_docx(
        tmp_path,
        output_dir="static",
        desired_name=original_stem
    )

    # 원하는 파일명으로 다운로드되도록 헤더 지정
    return FileResponse(
        docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=os.path.basename(docx_path),
    )
