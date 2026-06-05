from app.models import AdaptationSettings
from app.services.rule_engine import generate_rule_script
from app.services.chapter_parser import parse_chapters
from app.services.validator import validate_script_yaml


def test_rule_script_matches_schema():
    text = """
第1章 雨夜
林知远在旧书房发现一封信，沈清阻止他继续读下去。
第2章 长街
周启出现在长街尽头，告诉林知远真相并不完整。
第3章 庭院
三人在雨夜庭院摊牌，决定第二天进入城中寻找证据。
"""
    script = generate_rule_script(parse_chapters(text), AdaptationSettings())
    result = validate_script_yaml(script)
    assert result.valid
