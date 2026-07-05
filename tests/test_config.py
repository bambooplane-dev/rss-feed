from aggregator.models import FeedSource
from aggregator.config import load_feeds


def test_load_feeds_parses_yaml(tmp_path):
    p = tmp_path / "feeds.yaml"
    p.write_text(
        "feeds:\n"
        "  - name: Example\n"
        "    url: https://ex.com/feed\n"
        "    tag: ex\n"
        "    tier: 1\n"
    )
    feeds = load_feeds(str(p))
    assert feeds == [FeedSource(name="Example", url="https://ex.com/feed", tag="ex", tier=1)]


def test_load_real_feeds_file_has_expected_shape():
    feeds = load_feeds("feeds.yaml")
    assert len(feeds) >= 14
    assert all(f.name and f.url and f.tag for f in feeds)
    assert all(f.tier in (1, 2, 3) for f in feeds)
