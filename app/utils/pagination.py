
from typing import List, Tuple
from urllib.parse import urlencode
def paginate(items: List[dict], page: int = 1, per_page: int = 100) -> Tuple[List[dict], int]:
    if page < 1: page = 1
    if per_page < 1: per_page = 100
    start = (page - 1) * per_page; end = start + per_page
    return items[start:end], len(items)
def build_link_header(base_url: str, page: int, per_page: int, total: int, query: dict) -> str:
    last_page = max(1, (total + per_page - 1) // per_page)
    def url(p: int) -> str:
        q = {**query, "page": p, "per_page": per_page}
        return f"<{base_url}?{urlencode(q, doseq=True)}>; rel=\"%s\""
    links = [url(1) % "first", url(last_page) % "last"]
    if page > 1 and page <= last_page: links.append(url(page - 1) % "prev")
    if page < last_page: links.append(url(page + 1) % "next")
    return ", ".join(links)
