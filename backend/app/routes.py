from fastapi import APIRouter, HTTPException

from app.models import GenerateRequest, ParseRequest, RewriteRequest, ValidateRequest
from app.services.chapter_parser import parse_chapters
from app.services.generator import generate_script, rewrite_scene
from app.services.validator import load_yaml, validate_script_yaml

router = APIRouter()


@router.post("/parse")
def parse(payload: ParseRequest):
    chapters = parse_chapters(payload.text)
    return {
        "chapters": chapters,
        "is_valid": len(chapters) >= 3,
        "message": "识别到至少 3 个章节，可进入改编流程。" if len(chapters) >= 3 else "题目要求至少输入 3 个章节。",
    }


@router.post("/generate")
async def generate(payload: GenerateRequest):
    chapters = parse_chapters(payload.text)
    if len(chapters) < 3:
        raise HTTPException(status_code=422, detail="请提供至少 3 个章节的小说文本。")
    return await generate_script(chapters, payload.settings)


@router.post("/validate")
def validate(payload: ValidateRequest):
    data = load_yaml(payload.yaml_text)
    return validate_script_yaml(data)


@router.post("/rewrite")
async def rewrite(payload: RewriteRequest):
    return await rewrite_scene(payload.yaml_text, payload.scene_id, payload.instruction)
