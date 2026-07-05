import html
from zoneinfo import ZoneInfo

from .models import Article


def format_message(article: Article, tz: str = "UTC") -> str:
    title = html.escape(article.title)
    source = html.escape(article.source)
    if article.published:
        when = article.published.astimezone(ZoneInfo(tz)).strftime("%H:%M, %d %b")
    else:
        when = "—"

    parts = [f"🔹 <b>{title}</b>", f"{source} · {when}"]
    if article.summary:
        parts += ["", html.escape(article.summary)]
    parts += ["", article.url, f"#{article.tag}"]
    return "\n".join(parts)
