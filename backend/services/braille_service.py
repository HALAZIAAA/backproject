# backend/services/braille_service.py

import re, unicodedata, os
from docx import Document
from braillify import translate_to_unicode  # pip install braillify

def sanitize_filename(name: str) -> str:
    # 확장자 제거된 기본 이름만 받는다고 가정
    name = unicodedata.normalize("NFKC", name)
    # 윈도우 금지문자 제거: \ / : * ? " < > |
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    # 앞뒤 공백/점 제거
    return name.strip(" .")

def clean_text_for_braille(text: str) -> str:
    """점자 변환을 위해 허용 문자만 남기고 나머지 제거"""
    allowed = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        " .,;:-!?\"'()[]{}<>/\\+=_*#%&$@"
        "가나다라마바사아자차카타파하"
        "거너더러머버서어저처커터퍼허"
        "고노도로모보소오조초코토포호"
        "구누두루무부수우주추쿠투푸후"
        "규뉴듀류뮤뷰수유쥬츄큐튜퓨휴"
        "각낙닥락막박삭악작착칵탁팍학"
        "…·—–"
    )
    return ''.join(ch for ch in text if ch in allowed or ch == "\n")

def docx_to_text(path: str) -> str:
    """docx 문서에서 텍스트만 추출"""
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def convert_docx_to_brf(input_path: str, output_dir="static", desired_name: str | None = None):
    """DOCX → BRF 점자 변환"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 파일명 결정
    if desired_name:
        base_name = sanitize_filename(desired_name)
    else:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, base_name + ".brf")
    
    # 텍스트 정제
    text = docx_to_text(input_path)
    text = clean_text_for_braille(text)

    text = unicodedata.normalize("NFKC", text)
    text = text.replace("…", "...")
    text = re.sub(r'https?://\S+', '(링크)', text)
    text = text.replace("＠", "(at)")
    text = text.replace("@", "(at)")
    text = text.replace("&", "(and)")
    text = ''.join(ch for ch in text if ch.strip() != '' or ch == '\n')
    text = ''.join(ch for ch in text if (ord(ch) >= 32 and ord(ch) != 127) or ch == "\n")

    # BAD 문자 제거 + 점자 불가 문자는 공백으로 치환
    cleaned_chars = []
    for ch in text:
        try:
            translate_to_unicode(ch)   # 점자 변환 가능 여부 검사
            cleaned_chars.append(ch)
        except Exception:
            cleaned_chars.append(" ")  # 점자 불가 문자는 공백으로 대체

    text = "".join(cleaned_chars)

    # 안전하게 최종 점자 변환
    brf = translate_to_unicode(text)

    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(brf)

    print("BRF 생성 완료:", output_path)
    return output_path
