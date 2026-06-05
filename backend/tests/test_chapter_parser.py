from app.services.chapter_parser import parse_chapters


def test_parse_chinese_chapters():
    text = """
第1章 雨夜
林知远推开门，看见沈清站在灯下。

第2章 旧信
周启把信递过去，没有解释。

第3章 选择
沉默之后，所有人都知道答案已经出现。
"""
    chapters = parse_chapters(text)
    assert len(chapters) == 3
    assert chapters[0].title.startswith("第1章")

