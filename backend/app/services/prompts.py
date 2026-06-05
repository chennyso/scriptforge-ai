from app.models import AdaptationSettings, Chapter


def generation_prompt(chapters: list[Chapter], settings: AdaptationSettings) -> list[dict[str, str]]:
    chapter_text = "\n\n".join(
        f"## 第{chapter.index}章：{chapter.title}\n{chapter.content[:2600]}" for chapter in chapters
    )
    return [
        {
            "role": "system",
            "content": (
                "你是专业编剧和剧本统筹。请把小说章节改编成符合 ScriptForge YAML Schema 的中文结构化剧本。"
                "只输出 YAML，不要输出 Markdown 代码块，不要解释。必须包含 metadata、characters、locations、episodes、adaptation_notes。"
                "beats 中 type 只能是 action/dialogue/narration/transition；dialogue 必须有 speaker，speaker 必须引用 characters.id。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"改编设置：剧本类型={settings.script_type}，风格={settings.style}，目标场景数={settings.target_scene_count}，"
                f"旁白={settings.narration_level}，对白密度={settings.dialogue_density}。\n\n小说章节：\n{chapter_text}"
            ),
        },
    ]


def rewrite_prompt(yaml_text: str, scene_id: str, instruction: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "你是剧本医生。请只修改指定 scene，保持 YAML Schema 合法。只输出完整 YAML，不要解释。",
        },
        {
            "role": "user",
            "content": f"目标 scene_id={scene_id}，修改指令={instruction}。\n\n当前 YAML：\n{yaml_text}",
        },
    ]

