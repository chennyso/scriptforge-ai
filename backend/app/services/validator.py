from pathlib import Path
from typing import Any

import jsonschema
import yaml

from app.models import ValidationIssue, ValidationResult

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "script_schema.json"


def load_yaml(yaml_text: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML 语法错误：{exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("YAML 顶层必须是对象。")
    return data


def validate_script_yaml(data: dict[str, Any]) -> ValidationResult:
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    issues = [
        ValidationIssue(path="/".join(str(part) for part in error.absolute_path) or "$", message=error.message)
        for error in sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path))
    ]
    issues.extend(_semantic_issues(data))
    return ValidationResult(valid=not issues, issues=issues)


def _semantic_issues(data: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    characters = {item.get("id") for item in data.get("characters", []) if isinstance(item, dict)}
    for episode in data.get("episodes", []):
        for scene in episode.get("scenes", []):
            scene_id = scene.get("id", "unknown")
            for beat in scene.get("beats", []):
                speaker = beat.get("speaker")
                if speaker and speaker not in characters:
                    issues.append(ValidationIssue(path=f"scene:{scene_id}/speaker:{speaker}", message="对白角色未在 characters 中定义。"))
            for character_id in scene.get("characters", []):
                if character_id not in characters:
                    issues.append(ValidationIssue(path=f"scene:{scene_id}/characters", message=f"场景角色 {character_id} 未在 characters 中定义。"))
    return issues


def dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120)

