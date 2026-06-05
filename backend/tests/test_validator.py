from app.models import AdaptationSettings
from app.services.chapter_parser import parse_chapters
from app.services.rule_engine import generate_rule_script
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


def test_rule_engine_extracts_real_character_names():
    text = """
第1章 雨夜
雨从傍晚下到深夜，林知远回到旧书房。沈清站在灯下，阻止他打开那封信。
第2章 长街
周启拦住林知远，告诉他真相并不完整。沈清追来时，三个人都明白过去没有结束。
第3章 庭院
周启逼沈清说出名单下落，林知远发现名单上第一个名字正是自己的父亲。
"""
    script = generate_rule_script(parse_chapters(text), AdaptationSettings())
    names = [character["name"] for character in script["characters"]]
    assert "林知远" in names
    assert "沈清" in names
    assert "周启" in names
    assert "雨从傍晚" not in names


def test_rule_engine_avoids_sentence_fragments_for_transliterated_names():
    text = """
第1章 马利的影子
斯克鲁奇的办公室里只有一点微弱的火光。克拉奇特在外间搓着手。门外站着他的外甥。
第2章 第一位访客
马利的幽灵走进房间，告诉斯克鲁奇今夜会有三位灵体来访。
第3章 过去的圣诞
第一位灵体带着斯克鲁奇穿过记忆。斯克鲁奇看见年轻的自己曾经渴望被人接走。
"""
    script = generate_rule_script(parse_chapters(text), AdaptationSettings())
    names = [character["name"] for character in script["characters"]]
    assert "斯克鲁奇" in names
    assert "马利" in names
    assert "鲁奇" not in names
    assert "任何让" not in names
