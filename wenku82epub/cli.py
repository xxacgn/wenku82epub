import argparse
import mimetypes
import time
from pathlib import Path
from urllib.parse import urljoin

from tqdm import tqdm

from .book_page import parse_book_page
from .epub_builder import build_epub
from .http_client import fetch_bytes, fetch_html
from .illustrations import extract_image_urls
from .models import ImageItem
from .toc import parse_toc
from .txt_parser import find_missing_titles, parse_txt_with_toc, print_outline


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert TXT to EPUB.")
    parser.add_argument("input", help="Path to input TXT file")
    parser.add_argument("-u", "--book-url", required=True, help="Book page URL")
    parser.add_argument("-o", "--output", help="Path to output EPUB file")
    parser.add_argument("--dry-run", action="store_true", help="Only print outline")
    parser.add_argument(
        "-f",
        "--fetch-illustrations",
        action="store_true",
        help='Fetch images for chapters named "插图"',
    )
    args = parser.parse_args()
    input_path = Path(args.input)

    book_html = fetch_html(args.book_url)
    meta = parse_book_page(book_html, args.book_url)

    toc_html = fetch_html(meta.toc_url)
    toc = parse_toc(toc_html)
    text = input_path.read_text(encoding="utf-8")

    missing = find_missing_titles(text, toc)
    if missing:
        print("以下目录章节在 TXT 中未找到对应标题：")
        for title in missing:
            print(f"  - {title}")
        raise SystemExit("请检查 TXT 或目录来源是否一致。")

    volumes = parse_txt_with_toc(text, toc)

    print_outline(volumes)
    if args.dry_run:
        return

    if args.fetch_illustrations:
        for volume in volumes:
            for chapter in volume.chapters:
                if chapter.title.strip() != "插图":
                    continue
                if not chapter.href:
                    continue
                chapter_url = urljoin(meta.toc_url, chapter.href)
                chapter_html = fetch_html(chapter_url)
                image_urls = extract_image_urls(chapter_html, chapter_url)
                delay = 0.3
                for index, image_url in enumerate(
                    tqdm(image_urls, desc=f"插图下载: {volume.title}"), start=1
                ):
                    time.sleep(delay)
                    suffix = Path(image_url).suffix or ".jpg"
                    media_type = mimetypes.guess_type(image_url)[0] or "image/jpeg"
                    file_name = (
                        f"images/{meta.identifier}_{volume.title}_{index}{suffix}"
                    )
                    image_bytes = fetch_bytes(image_url)
                    chapter.images.append(
                        ImageItem(
                            file_name=file_name,
                            media_type=media_type,
                            content=image_bytes,
                        )
                    )
                    delay = min(delay * 1.5, 2.0)

    cover_bytes = None
    cover_name = None
    if meta.cover_url:
        cover_name = Path(meta.cover_url).name
        cover_bytes = fetch_bytes(meta.cover_url)

    output_path = Path(args.output) if args.output else Path(f"{meta.title}.epub")
    build_epub(volumes, meta, output_path, cover_bytes, cover_name)
