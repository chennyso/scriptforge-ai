import re

from app.models import Chapter

TITLE_RE = re.compile(r"(?m)^\s*((第[一二三四五六七八九十百千万\d]+[章节回幕].*)|(Chapter\s+\d+.*)|(\d+[\.、]\s*.+))\s*$", re.I)


def parse_chapters(text: str) -> list[Chapter]:
    normalized = text.replace("\r\n", "\n").strip()
    matches = list(TITLE_RE.finditer(normalized))
    chapters: list[Chapter] = []

    if matches:
        for idx, match in enumerate(matches):
            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(normalized)
            content = normalized[start:end].strip()
            title = match.group(1).strip()
            if content:
                chapters.append(_chapter(len(chapters) + 1, title, content))
        return chapters

    blocks = [block.strip() for block in re.split(r"\n\s*\n", normalized) if block.strip()]
    if len(blocks) >= 3:
        return [_chapter(i + 1, f"自动分章 {i + 1}", block) for i, block in enumerate(blocks)]

    chunk_size = max(800, len(normalized) // 3)
    chunks = [normalized[i : i + chunk_size].strip() for i in range(0, len(normalized), chunk_size) if normalized[i : i + chunk_size].strip()]
    return [_chapter(i + 1, f"自动分章 {i + 1}", chunk) for i, chunk in enumerate(chunks)]


def _chapter(index: int, title: str, content: str) -> Chapter:
    return Chapter(index=index, title=title, content=content, word_count=len(re.findall(r"\w+|[\u4e00-\u9fff]", content)))

