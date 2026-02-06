import re
from urllib.parse import urljoin

from lxml import html as lxml_html

from .models import BookMeta


def parse_book_page(html_text: str, base_url: str) -> BookMeta:
    root = lxml_html.fromstring(html_text)

    title_text = root.xpath("string(//title)").strip()
    title = ""
    author = ""
    publisher = None
    if title_text:
        parts = [part.strip() for part in title_text.split(" - ") if part.strip()]
        if len(parts) >= 3:
            title = parts[0]
            author = parts[1]
            publisher = parts[2]

    if not author:
        author_text = root.xpath("string(//td[contains(text(),'小说作者')])").strip()
        if "：" in author_text:
            author = author_text.split("：", 1)[1].strip()

    if not publisher:
        pub_text = root.xpath("string(//td[contains(text(),'文库分类')])").strip()
        if "：" in pub_text:
            publisher = pub_text.split("：", 1)[1].strip() or None

    if not title:
        title = root.xpath("string(//span//b)").strip()

    toc_href = root.xpath("//a[normalize-space()='小说目录']/@href")
    if not toc_href:
        raise ValueError("无法在书籍页面找到目录链接")
    toc_url = urljoin(base_url, toc_href[0])

    cover_href = root.xpath("//img[contains(@src,'/image/')]/@src")
    cover_url = urljoin(base_url, cover_href[0]) if cover_href else None

    book_id_match = re.search(r"/book/(\d+)\.htm", base_url)
    identifier = book_id_match.group(1) if book_id_match else base_url

    return BookMeta(
        identifier=identifier,
        title=title or identifier,
        author=author or "",
        publisher=publisher,
        language="zh",
        cover_url=cover_url,
        toc_url=toc_url,
    )
