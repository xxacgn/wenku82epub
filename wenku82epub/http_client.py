import time
from datetime import datetime
from email.utils import parsedate_to_datetime

import httpx

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def _sleep_with_backoff(
    attempt: int,
    backoff: float,
    retry_after: str | None,
) -> None:
    if retry_after:
        try:
            seconds = int(retry_after)
            time.sleep(max(seconds, backoff))
            return
        except ValueError:
            try:
                target = parsedate_to_datetime(retry_after)
                delay = (target - datetime.now(target.tzinfo)).total_seconds()
                if delay > 0:
                    time.sleep(max(delay, backoff))
                    return
            except (TypeError, ValueError):
                pass
    time.sleep(backoff * (2 ** (attempt - 1)))


def fetch_html(
    url: str,
    encoding: str = "gbk",
    retries: int = 6,
    backoff: float = 1.0,
) -> str:
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
        for attempt in range(1, retries + 1):
            try:
                resp = client.get(url)
                resp.raise_for_status()
                resp.encoding = encoding
                return resp.text
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status not in {429, 500, 502, 503, 504} or attempt == retries:
                    raise
                retry_after = exc.response.headers.get("Retry-After")
            except httpx.RequestError:
                if attempt == retries:
                    raise
                retry_after = None
            _sleep_with_backoff(attempt, backoff, retry_after)
        raise RuntimeError("Failed to fetch html after retries")


def fetch_bytes(
    url: str,
    retries: int = 6,
    backoff: float = 1.0,
) -> bytes:
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
                retry_after = exc.response.headers.get("Retry-After")
            except httpx.RequestError:
                if attempt == retries:
                    raise
                retry_after = None
            _sleep_with_backoff(attempt, backoff, retry_after)
        raise RuntimeError("Failed to fetch bytes after retries")


def fetch_txt(
    url: str,
    encoding: str = "utf-8",
    retries: int = 6,
    backoff: float = 1.0,
) -> str:
    return fetch_html(url, encoding, retries=retries, backoff=backoff)
