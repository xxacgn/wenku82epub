from typing import TypedDict

from lxml import html


class TocChapter(TypedDict):
    title: str
    href: str | None


class TocVolume(TypedDict):
    title: str
    chapters: list[TocChapter]


def parse_toc(html_text: str) -> list[TocVolume]:
    root = html.fromstring(html_text)

    table = root.xpath('//table[contains(@class,"css")]')
    if not table:
        return []
    table = table[0]

    toc: list[TocVolume] = []
    current_volume: TocVolume | None = None

    for tr in table.xpath(".//tr"):
        vcell = tr.xpath('.//td[contains(@class,"vcss")]')
        if vcell:
            title = "".join(vcell[0].itertext()).strip()
            if title:
                current_volume = {"title": title, "chapters": []}
                toc.append(current_volume)
            continue

        if current_volume is None:
            continue

        for td in tr.xpath('.//td[contains(@class,"ccss")]'):
            link = td.xpath(".//a[normalize-space()]")
            if not link:
                continue
            a = link[0]
            name = "".join(a.itertext()).strip()
            href = a.get("href")
            if name:
                current_volume["chapters"].append({"title": name, "href": href})

    return toc
