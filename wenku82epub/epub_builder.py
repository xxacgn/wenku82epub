import html
from pathlib import Path

from ebooklib import epub

from .models import BookMeta, Chapter, Volume


def chapter_to_html(chapter: Chapter) -> str:
    paragraphs: list[str] = []
    buffer: list[str] = []
    for line in chapter.content_lines:
        if not line.strip():
            if buffer:
                paragraphs.append("\n".join(buffer).strip())
                buffer.clear()
            continue
        buffer.append(line)
    if buffer:
        paragraphs.append("\n".join(buffer).strip())

    if not paragraphs:
        body = ""
    else:
        body = "".join(
            f"<p>{html.escape(p).replace('\n', '<br/>')}</p>" for p in paragraphs
        )

    images = "".join(
        (
            f"<div class='illustration'><img src='{img.external_url}' alt='' /></div>"
            if img.external_url
            else f"<div class='illustration'><img src='{img.file_name}' alt='' /></div>"
        )
        for img in chapter.images
        if img.external_url or img.file_name
    )
    if not body and not images:
        body = "<p></p>"
    return f"<h1>{html.escape(chapter.title)}</h1>{images}{body}"


def build_epub(
    volumes: list[Volume],
    meta: BookMeta,
    output_path: Path,
    cover_bytes: bytes | None,
    cover_name: str | None,
) -> None:
    book = epub.EpubBook()
    book.set_identifier(meta.identifier)
    book.set_title(meta.title)
    book.set_language(meta.language)
    if meta.author:
        book.add_author(meta.author)
    if meta.publisher:
        book.add_metadata("DC", "publisher", meta.publisher)

    if cover_bytes and cover_name:
        book.set_cover(cover_name, cover_bytes)

    toc_entries: list[tuple[epub.Section, list[epub.EpubHtml]]] = []
    all_chapters: list[epub.EpubHtml] = []
    chapter_index = 1

    for volume in volumes:
        section = epub.Section(volume.title)
        section_chapters: list[epub.EpubHtml] = []
        for chapter in volume.chapters:
            for image_index, image in enumerate(chapter.images, start=1):
                if image.external_url or not image.content or not image.file_name:
                    continue
                image_id = f"img_{chapter_index}_{image_index}"
                book.add_item(
                    epub.EpubItem(
                        uid=image_id,
                        file_name=image.file_name,
                        media_type=image.media_type or "image/jpeg",
                        content=image.content,
                    )
                )
            file_name = f"chapter_{chapter_index}.xhtml"
            chapter_index += 1
            epub_chapter = epub.EpubHtml(
                title=chapter.title,
                file_name=file_name,
                lang=meta.language,
            )
            epub_chapter.content = chapter_to_html(chapter)
            book.add_item(epub_chapter)
            section_chapters.append(epub_chapter)
            all_chapters.append(epub_chapter)

        toc_entries.append((section, section_chapters))

    book.toc = toc_entries
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav", *all_chapters]

    epub.write_epub(str(output_path), book)
