from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.models import GenerateRequest, ParseRequest, RewriteRequest, ValidateRequest
from app.services.chapter_parser import parse_chapters
from app.services.generator import generate_script, rewrite_scene
from app.services.validator import load_yaml, validate_script_yaml
from app.services.ai_client import AiClient

router = APIRouter()
ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = ROOT / "examples"


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


@router.get("/samples")
def samples():
    return [
        {
            "id": "christmas-carol",
            "title": "A Christmas Carol 中文改写样例",
            "path": "public-domain-novel.md",
            "source": "Charles Dickens, public domain",
        },
        {
            "id": "alice-wonderland",
            "title": "Alice's Adventures in Wonderland 长篇英文样例",
            "path": "alice-wonderland-gutenberg.txt",
            "source": "Project Gutenberg ebook #11, public domain in the United States",
        },
        {
            "id": "journey-west",
            "title": "《西游记》中文长篇样例",
            "path": "journey-to-the-west-gutenberg.txt",
            "source": "Project Gutenberg ebook #23962, public domain in the United States",
        },
        {
            "id": "guofeng-webnovel",
            "title": "GuoFeng 公开网文测试集样例",
            "path": "guofeng-webnovel-sample.md",
            "source": "longyuewangdcu/GuoFeng-Webnovel WMT2024_Testset",
        },
    ]


@router.get("/samples/{sample_id}")
def sample_text(sample_id: str):
    mapping = {
        "christmas-carol": "public-domain-novel.md",
        "alice-wonderland": "alice-wonderland-gutenberg.txt",
        "journey-west": "journey-to-the-west-gutenberg.txt",
        "guofeng-webnovel": "guofeng-webnovel-sample.md",
    }
    filename = mapping.get(sample_id)
    if not filename:
        raise HTTPException(status_code=404, detail="样例不存在。")
    path = EXAMPLES_DIR / filename
    return {"id": sample_id, "text": path.read_text(encoding="utf-8")}


@router.get("/config")
def config():
    client = AiClient()
    return {
        "model": client.model,
        "base_url": client.base_url,
        "ai_enabled": client.enabled,
        "api_key_configured": bool(client.api_key),
        "mock_mode": client.use_mock,
    }
