import yaml

from .models import FeedSource


def load_feeds(path: str) -> list[FeedSource]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    feeds = []
    for i, s in enumerate(data["feeds"]):
        missing = [k for k in ("name", "url", "tag", "tier") if k not in s]
        if missing:
            raise ValueError(
                f"feed #{i} in {path} is missing required field(s): {', '.join(missing)}"
            )
        feeds.append(FeedSource(name=s["name"], url=s["url"], tag=s["tag"], tier=s["tier"]))
    return feeds
