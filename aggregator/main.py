import argparse
import logging
import os
import time
from datetime import datetime, timezone

import httpx

from .config import load_feeds
from .fetch import fetch_feed
from .format import format_message
from .models import Article, FeedSource
from .parse import parse_feed
from .state import load_state, save_state, select_new
from .telegram import send_message

log = logging.getLogger("aggregator")

_EPOCH = datetime.min.replace(tzinfo=timezone.utc)


def collect_articles(feeds: list[FeedSource], client: httpx.Client) -> list[Article]:
    articles: list[Article] = []
    for feed in feeds:
        try:
            content = fetch_feed(feed.url, client)
            articles.extend(parse_feed(content, feed))
        except Exception as exc:  # noqa: BLE001 - one bad feed must not stop the run
            log.warning("feed failed: %s (%s)", feed.url, exc)
    return articles


def run(
    *,
    feeds_path: str,
    state_path: str,
    token: str,
    chat_id: str,
    tz: str = "UTC",
    dry_run: bool = False,
    send_delay: float = 3.5,
) -> int:
    if not dry_run and (not token or not chat_id):
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set (or use --dry-run)")
    feeds = load_feeds(feeds_path)
    with httpx.Client() as client:
        articles = collect_articles(feeds, client)

    seen = load_state(state_path)
    if seen is None:
        # First run: seed everything as seen, post nothing.
        if not dry_run:
            save_state(state_path, [a.id for a in articles])
        log.info("first run: seeded %d ids, posted nothing", len(articles))
        return 0

    new = select_new(articles, seen)
    new.sort(key=lambda a: a.published or _EPOCH)

    posted_ids = list(seen)
    sent_count = 0
    with httpx.Client() as client:
        for i, article in enumerate(new):
            text = format_message(article, tz)
            if dry_run:
                print(text)
                print("---")
                sent_count += 1
                continue
            try:
                send_message(text, token, chat_id, client)
            except Exception as exc:  # noqa: BLE001 - isolate a failing send; unsent ids retry next run
                log.warning("send failed for %s (%s); stopping this run", article.url, exc)
                break
            posted_ids.append(article.id)
            sent_count += 1
            if i < len(new) - 1:
                time.sleep(send_delay)

    if not dry_run:
        save_state(state_path, posted_ids)
    log.info("%sposted %d new article(s)", "[dry-run] would have " if dry_run else "", sent_count)
    return sent_count


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="AI news RSS → Telegram aggregator")
    parser.add_argument("--dry-run", action="store_true", help="print messages, do not send or persist")
    parser.add_argument("--feeds", default="feeds.yaml")
    parser.add_argument("--state", default="state.json")
    parser.add_argument("--tz", default="UTC")
    args = parser.parse_args()

    run(
        feeds_path=args.feeds,
        state_path=args.state,
        token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
        tz=args.tz,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
