import httpx
import pytest

from aggregator.telegram import send_message


def _client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_send_message_posts_expected_payload():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        import json
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"ok": True})

    with _client(handler) as client:
        send_message("hello", "TOKEN", "123", client)

    assert "/botTOKEN/sendMessage" in seen["url"]
    assert seen["body"]["chat_id"] == "123"
    assert seen["body"]["text"] == "hello"
    assert seen["body"]["parse_mode"] == "HTML"


def test_send_message_retries_on_429_then_succeeds():
    calls = {"n": 0}
    slept = []

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, json={"ok": False, "parameters": {"retry_after": 7}})
        return httpx.Response(200, json={"ok": True})

    with _client(handler) as client:
        send_message("hi", "T", "1", client, sleep=slept.append)

    assert calls["n"] == 2
    assert slept == [7]


def test_send_message_raises_on_400():
    def handler(request):
        return httpx.Response(400, json={"ok": False})

    with _client(handler) as client:
        with pytest.raises(httpx.HTTPStatusError):
            send_message("x", "T", "1", client)
