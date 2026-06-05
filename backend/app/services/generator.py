from typing import Any

from app.models import AdaptationSettings, Chapter, GenerateResponse
from app.services.ai_client import AiClient
from app.services.prompts import generation_prompt, rewrite_prompt
from app.services.rule_engine import apply_rule_rewrite, build_blueprint, generate_rule_script
from app.services.validator import dump_yaml, load_yaml, validate_script_yaml


async def generate_script(chapters: list[Chapter], settings: AdaptationSettings) -> GenerateResponse:
    client = AiClient()
    provider = "rule-engine"
    script: dict[str, Any]

    if client.enabled:
        try:
            content = await client.chat(generation_prompt(chapters, settings))
            script = load_yaml(_strip_fences(content))
            validation = validate_script_yaml(script)
            if validation.valid:
                provider = client.model
            else:
                script = generate_rule_script(chapters, settings)
        except Exception:
            script = generate_rule_script(chapters, settings)
    else:
        script = generate_rule_script(chapters, settings)

    validation = validate_script_yaml(script)
    yaml_text = dump_yaml(script)
    return GenerateResponse(
        chapters=chapters,
        blueprint=build_blueprint(chapters),
        yaml_text=yaml_text,
        script=script,
        validation=validation,
        provider=provider,
    )


async def rewrite_scene(yaml_text: str, scene_id: str, instruction: str):
    client = AiClient()
    script = load_yaml(yaml_text)
    provider = "rule-engine"

    if client.enabled:
        try:
            content = await client.chat(rewrite_prompt(yaml_text, scene_id, instruction))
            candidate = load_yaml(_strip_fences(content))
            validation = validate_script_yaml(candidate)
            if validation.valid:
                script = candidate
                provider = client.model
            else:
                script = apply_rule_rewrite(script, scene_id, instruction)
        except Exception:
            script = apply_rule_rewrite(script, scene_id, instruction)
    else:
        script = apply_rule_rewrite(script, scene_id, instruction)

    validation = validate_script_yaml(script)
    return {
        "yaml_text": dump_yaml(script),
        "script": script,
        "validation": validation,
        "provider": provider,
    }


def _strip_fences(text: str) -> str:
    clean = text.strip()
    if clean.startswith("```"):
        clean = clean.strip("`")
        if clean.lower().startswith("yaml"):
            clean = clean[4:]
    return clean.strip()

