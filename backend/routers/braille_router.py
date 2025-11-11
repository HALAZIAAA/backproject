# backend/routers/braille_router.py

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import tempfile, shutil, os
from services.braille_service import convert_docx_to_brf

router = APIRouter()

@router.post("/braille")
async def convert_braille(file: UploadFile = File(...)):
    # DOCX 파일만 허용
    if not file.filename.lower().endswith(".docx"):
        return {"error": "DOCX 파일만 업로드 가능합니다."}

    # 임시 파일 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # 파일 이름에서 확장자 제외
    base_name = os.path.splitext(os.path.basename(file.filename))[0]

    # 원본 이름 유지한 상태로 변환 수행
    brf_path = convert_docx_to_brf(tmp_path, output_dir="static", desired_name=base_name)

    return FileResponse(
        brf_path,
        media_type="text/plain",
        filename=os.path.basename(brf_path),
    )
