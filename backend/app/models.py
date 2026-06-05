from typing import Any, Literal

from pydantic import BaseModel, Field


class Chapter(BaseModel):
    index: int
    title: str
    content: str
    word_count: int


class ParseRequest(BaseModel):
    text: str = Field(min_length=100)


class ParseResponse(BaseModel):
    chapters: list[Chapter]
    is_valid: bool
    message: str


class AdaptationSettings(BaseModel):
    script_type: Literal["screenplay", "short_drama", "stage_play", "audio_drama"] = "screenplay"
    style: Literal["faithful", "conflict_plus", "compressed", "dialogue_plus"] = "conflict_plus"
    target_scene_count: int = Field(default=6, ge=3, le=24)
    narration_level: Literal["none", "light", "balanced"] = "light"
    dialogue_density: Literal["low", "medium", "high"] = "medium"


class GenerateRequest(BaseModel):
    text: str = Field(min_length=100)
    settings: AdaptationSettings = Field(default_factory=AdaptationSettings)


class ValidationIssue(BaseModel):
    path: str
    message: str


class ValidationResult(BaseModel):
    valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)


class GenerateResponse(BaseModel):
    chapters: list[Chapter]
    blueprint: dict[str, Any]
    yaml_text: str
    script: dict[str, Any]
    validation: ValidationResult
    provider: str
    provider_note: str = ""


class ValidateRequest(BaseModel):
    yaml_text: str


class RewriteRequest(BaseModel):
    yaml_text: str
    scene_id: str
    instruction: Literal["intensify_conflict", "add_dialogue", "compress_pace", "more_cinematic"]
