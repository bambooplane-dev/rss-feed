import time

import httpx

_API = "https://api.telegram.org/bot{token}/sendMessage"


def send_message(
    text: str,
    token: str,
    chat_id: str,
    client: httpx.Client,
    *,
    max_retries: int = 3,
    sleep=time.sleep,
) -> None:
    url = _API.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    for _ in range(max_retries):
        resp = client.post(url, json=payload, timeout=20.0)
        if resp.status_code == 429:
            retry_after = resp.json().get("parameters", {}).get("retry_after", 1)
            sleep(retry_after)
            continue
        resp.raise_for_status()
        return
    raise RuntimeError(f"Telegram send failed after {max_retries} attempts")
