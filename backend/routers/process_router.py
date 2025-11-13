# backend/routers/process_router.py

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import tempfile, shutil, os
from services.vlm_service import convert_to_text_and_docx_with_vlm

router = APIRouter()

@router.post("/process")
async def process_file(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    original_stem = os.path.splitext(file.filename)[0]

    txt_path, docx_path = convert_to_text_and_docx_with_vlm(
        tmp_path,
        output_dir="static",
        desired_name=original_stem
    )
    # Docx 다운로드
    return FileResponse(
        docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=os.path.basename(docx_path),
    )
