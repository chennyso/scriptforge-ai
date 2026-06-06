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


def test_parse_english_roman_chapters():
    text = """
CHAPTER I.
Down the Rabbit-Hole
Alice was beginning to get very tired of sitting by her sister.

CHAPTER II.
The Pool of Tears
Alice grew and shrank and wondered what would happen next.

CHAPTER III.
A Caucus-Race and a Long Tale
Everyone spoke at once, and Alice tried to understand the rules.
"""
    chapters = parse_chapters(text)
    assert len(chapters) == 3
    assert chapters[0].title == "CHAPTER I."


def test_parse_chinese_hui_chapters():
    text = """
第一回 靈根育孕源流出　心性修持大道生
詩曰：混沌未分天地亂，茫茫渺渺無人見。

第二回 悟徹菩提真妙理　斷魔歸本合元神
話表美猴王得了姓名，怡然踴躍，對菩提前作禮啟謝。

第三回 四海千山皆拱伏　九幽十類盡除名
卻說美猴王榮歸故里，自剿了混世魔王。
"""
    chapters = parse_chapters(text)
    assert len(chapters) == 3
    assert chapters[0].title.startswith("第一回")
