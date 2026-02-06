import time

import httpx

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def fetch_html(url: str, encoding: str = "gbk") -> str:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    with httpx.Client(
        http2=True,
        headers=headers,
        timeout=10,
        follow_redirects=True,
    ) as client:
        resp = client.get(url)
        resp.raise_for_status()
        resp.encoding = encoding
        return resp.text


def fetch_bytes(url: str, retries: int = 3, backoff: float = 0.5) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    with httpx.Client(
        http2=True,
        headers=headers,
        timeout=10,
        follow_redirects=True,
    ) as client:
        for attempt in range(1, retries + 1):
            try:
                resp = client.get(url)
                resp.raise_for_status()
                return resp.content
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status not in {429, 500, 502, 503, 504} or attempt == retries:
                    raise
            except httpx.RequestError:
                if attempt == retries:
                    raise
            time.sleep(backoff * (2 ** (attempt - 1)))
        raise RuntimeError("Failed to fetch bytes after retries")


def fetch_txt(url: str, encoding: str = "utf-8") -> str:
    return fetch_html(url, encoding)
