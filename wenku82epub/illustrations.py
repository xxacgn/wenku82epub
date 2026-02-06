from urllib.parse import urljoin

from lxml import html as lxml_html


def extract_image_urls(html_text: str, base_url: str) -> list[str]:
    root = lxml_html.fromstring(html_text)
    urls: list[str] = []

    for src in root.xpath("//div[contains(@class,'divimage')]//img/@src"):
        full = urljoin(base_url, src)
        if full not in urls:
            urls.append(full)

    for href in root.xpath("//div[contains(@class,'divimage')]//a/@href"):
        full = urljoin(base_url, href)
        if full not in urls:
            urls.append(full)

    return urls
