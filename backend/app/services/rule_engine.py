import re
from collections import Counter
from typing import Any

from app.models import AdaptationSettings, Chapter


COMMON_LOCATIONS = ["客栈", "庭院", "书房", "街", "城", "门", "屋", "桥", "车站", "大厅", "森林", "河岸", "office", "room"]


def build_blueprint(chapters: list[Chapter]) -> dict[str, Any]:
    names = _extract_names("".join(chapter.content for chapter in chapters))
    locations = _extract_locations("".join(chapter.content for chapter in chapters))
    return {
        "theme": "人物在外部压力下做出选择，并推动关系与目标发生变化。",
        "characters": names,
        "locations": locations,
        "chapter_summaries": [
            {
                "chapter": chapter.index,
                "title": chapter.title,
                "summary": _summary(chapter.content),
                "turning_point": _turning_point(chapter.content),
            }
            for chapter in chapters
        ],
    }


def generate_rule_script(chapters: list[Chapter], settings: AdaptationSettings) -> dict[str, Any]:
    blueprint = build_blueprint(chapters)
    character_names = blueprint["characters"] or ["林知远", "沈清", "周启"]
    characters = [
        {
            "id": f"char_{idx + 1}",
            "name": name,
            "role": role,
            "motivation": motivation,
            "voice": voice,
        }
        for idx, (name, role, motivation, voice) in enumerate(_character_profiles(character_names))
    ]
    locations = [
        {"id": f"loc_{idx + 1}", "name": name, "description": f"{name}承载了本段剧情的行动压力与人物关系变化。"}
        for idx, name in enumerate(blueprint["locations"] or ["临时会议室", "旧街巷", "雨夜门廊"])
    ]

    scenes = []
    scene_count = max(settings.target_scene_count, len(chapters))
    for idx in range(scene_count):
        chapter = chapters[idx % len(chapters)]
        main = characters[idx % len(characters)]
        partner = characters[(idx + 1) % len(characters)]
        location = locations[idx % len(locations)]
        source_summary = _summary(chapter.content)
        beats = [
            {"type": "action", "content": f"{location['name']}里，{main['name']}带着上一场留下的问题进入新的局面。"},
            {
                "type": "dialogue",
                "speaker": main["id"],
                "content": _dialogue_line(main["name"], source_summary, settings.style),
            },
            {
                "type": "dialogue",
                "speaker": partner["id"],
                "content": _reply_line(partner["name"], settings.dialogue_density),
            },
            {"type": "action", "content": _turning_point(chapter.content)},
        ]
        if settings.narration_level != "none":
            beats.insert(1, {"type": "narration", "content": f"这一场来自第 {chapter.index} 章，保留原文的情绪重心并压缩叙述。"})
        beats.append({"type": "transition", "content": "切至下一场。"})
        scenes.append(
            {
                "id": f"SC{idx + 1:03d}",
                "heading": f"内景/外景 - {location['name']} - {'夜' if idx % 2 else '日'}",
                "time": "夜" if idx % 2 else "日",
                "location": location["id"],
                "characters": [main["id"], partner["id"]],
                "source_chapters": [chapter.index],
                "objective": f"{main['name']}试图确认真相并迫使对方表态。",
                "conflict": "角色目标并不一致，信息差让对话持续升级。",
                "beats": beats,
            }
        )

    return {
        "metadata": {
            "title": "未命名小说改编剧本",
            "script_type": settings.script_type,
            "language": "zh-CN",
            "source_chapters": len(chapters),
            "logline": "主角在连续事件中追索真相，关系裂变迫使所有人面对真正的选择。",
        },
        "characters": characters,
        "locations": locations,
        "episodes": [{"id": "EP01", "title": "第一集：选择的代价", "scenes": scenes}],
        "adaptation_notes": [
            "采用故事蓝图先行策略，先抽取人物、场景和章节转折，再生成可编辑剧本。",
            "每场戏保留 source_chapters，便于作者追溯原文来源。",
            f"本稿使用 {settings.style} 风格，并控制旁白等级为 {settings.narration_level}。",
        ],
    }


def apply_rule_rewrite(script: dict[str, Any], scene_id: str, instruction: str) -> dict[str, Any]:
    suffix = {
        "intensify_conflict": "两人的潜台词被推到明面，沉默比争吵更让局势紧张。",
        "add_dialogue": "新增一轮对白，让角色把需求、顾虑和底线说得更清楚。",
        "compress_pace": "删去重复动作，场面直接进入关键选择。",
        "more_cinematic": "用可拍摄的动作和视线调度替代抽象心理描写。",
    }[instruction]
    for episode in script.get("episodes", []):
        for scene in episode.get("scenes", []):
            if scene.get("id") == scene_id:
                scene["beats"].insert(-1, {"type": "action", "content": suffix})
                scene["conflict"] = f"{scene.get('conflict', '')} {suffix}".strip()
    return script


def _extract_names(text: str) -> list[str]:
    candidates = re.findall(r"[\u4e00-\u9fff]{2,4}", text)
    stop = {"他们", "她们", "我们", "你们", "这个", "那个", "时候", "声音", "眼前", "已经", "没有", "自己", "一句"}
    names = [item for item in candidates if item not in stop and len(set(item)) > 1]
    return [name for name, _ in Counter(names).most_common(4)]


def _extract_locations(text: str) -> list[str]:
    found = []
    for keyword in COMMON_LOCATIONS:
        if keyword.lower() in text.lower():
            found.append(keyword if re.search(r"[\u4e00-\u9fff]", keyword) else keyword.title())
    return found[:4] or ["旧书房", "长街", "雨夜庭院"]


def _summary(text: str) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    return clean[:90] + ("..." if len(clean) > 90 else "")


def _turning_point(text: str) -> str:
    sentences = re.split(r"[。！？!?]\s*", text)
    candidates = [item.strip() for item in sentences if len(item.strip()) > 12]
    return (candidates[-1] if candidates else _summary(text))[:120]


def _character_profiles(names: list[str]):
    roles = ["主角", "关键盟友", "对立者", "秘密持有者"]
    motivations = ["想找到真相", "想守住承诺", "想阻止计划失控", "想隐藏过去"]
    voices = ["克制、观察细致", "直接、情绪外露", "锋利、善于试探", "平静但有所保留"]
    return [(name, roles[i % 4], motivations[i % 4], voices[i % 4]) for i, name in enumerate(names[:4])]


def _dialogue_line(name: str, summary: str, style: str) -> str:
    if style == "conflict_plus":
        return f"{name}：如果这就是你隐瞒的答案，那我需要你现在说清楚。"
    if style == "compressed":
        return f"{name}：别绕了，答案是什么？"
    return f"{name}：我一直在想，{summary[:24]}这件事不该就这样过去。"


def _reply_line(name: str, density: str) -> str:
    if density == "high":
        return f"{name}：我不是不说，是说出来以后，我们都没有退路。"
    return f"{name}：你确定自己承受得住吗？"

