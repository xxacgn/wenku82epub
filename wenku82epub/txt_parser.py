import html

from .models import Chapter, Volume
from .toc import TocVolume


_EQUIVALENT_CHARS = str.maketrans(
    {
        "•": "·",
    }
)


def normalize_title(text: str) -> str:
    normalized = html.unescape(text).translate(_EQUIVALENT_CHARS)
    return " ".join(normalized.split())


def parse_txt_with_toc(text: str, toc: list[TocVolume]) -> list[Volume]:
    volumes: list[Volume] = [
        Volume(
            title=vol["title"],
            chapters=[
                Chapter(title=ch["title"], href=ch.get("href"))
                for ch in vol["chapters"]
            ],
        )
        for vol in toc
    ]

    chapter_by_title: dict[str, Chapter] = {}
    for volume in volumes:
        for chapter in volume.chapters:
            full_title = normalize_title(f"{volume.title} {chapter.title}")
            chapter_by_title[full_title] = chapter

    current_chapter: Chapter | None = None
    preface_lines: list[str] = []
    matched_any = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current_chapter is not None:
                current_chapter.content_lines.append("")
            elif preface_lines:
                preface_lines.append("")
            continue

        normalized = normalize_title(line)
        if normalized in chapter_by_title:
            current_chapter = chapter_by_title[normalized]
            matched_any = True
            continue

        if current_chapter is None:
            preface_lines.append(line)
        else:
            current_chapter.content_lines.append(line)

    if not volumes:
        if not preface_lines:
            preface_lines = [""]
        volumes.append(
            Volume(
                title="未分卷",
                chapters=[Chapter(title="正文", content_lines=preface_lines)],
            )
        )
    else:
        if preface_lines:
            preface_volume = Volume(
                title="未分卷",
                chapters=[Chapter(title="前言", content_lines=preface_lines)],
            )
            volumes.insert(0, preface_volume)
        if not matched_any:
            volumes.append(
                Volume(
                    title="未分卷",
                    chapters=[Chapter(title="正文", content_lines=text.splitlines())],
                )
            )

    return volumes


def find_missing_titles(text: str, toc: list[TocVolume]) -> list[str]:
    lines = {normalize_title(line) for line in text.splitlines() if line.strip()}
    missing: list[str] = []
    for vol in toc:
        for ch in vol["chapters"]:
            expected = normalize_title(f"{vol['title']} {ch['title']}")
            if expected not in lines:
                missing.append(f"{vol['title']} {ch['title']}")
    return missing


def print_outline(volumes: list[Volume]) -> None:
    for volume in volumes:
        print(volume.title)
        for chapter in volume.chapters:
            print(f"  {chapter.title}")
