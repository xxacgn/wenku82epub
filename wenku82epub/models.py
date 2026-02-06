from dataclasses import dataclass, field


@dataclass
class ImageItem:
    file_name: str
    media_type: str
    content: bytes


@dataclass
class Chapter:
    title: str
    href: str | None = None
    content_lines: list[str] = field(default_factory=list)
    images: list[ImageItem] = field(default_factory=list)


@dataclass
class Volume:
    title: str
    chapters: list[Chapter] = field(default_factory=list)


@dataclass
class BookMeta:
    identifier: str
    title: str
    author: str
    publisher: str | None
    language: str
    cover_url: str | None
    toc_url: str
