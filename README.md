# AI News RSS Aggregator → Telegram

Fetches AI-news RSS/Atom feeds and posts each new article as a structured
message to a Telegram channel, twice a day, via GitHub Actions. Dedup state
lives in `state.json`, committed back to the repo each run.

## Sources

Edit `feeds.yaml` — one `{ name, url, tag, tier }` entry per feed. No code change needed.
`tier` is a required integer matching the source's tier: `1` = core news, `2` = labs/primary,
`3` = analysis.

## One-time setup

1. **Create a Telegram bot:** message [@BotFather](https://t.me/BotFather),
   send `/newbot`, follow prompts, copy the **bot token**.
2. **Create a channel** (or use an existing one) and **add the bot as an admin**
   with permission to post messages.
3. **Get the channel chat id:** post any message in the channel, then open
   `https://api.telegram.org/bot<TOKEN>/getUpdates` and read
   `channel_post.chat.id` (a negative number like `-1001234567890`), or use the
   channel's public `@username`.
4. **Add repository secrets** (Settings → Secrets and variables → Actions):
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
5. **Keep the repo private** (recommended) — scheduled workflows in *public*
   repos are auto-disabled after 60 days of inactivity.

## Schedule

Runs at **07:17 and 18:17 UTC** (`.github/workflows/aggregate.yml`). Scheduled
runs can be delayed at high load, so treat times as approximate. Use the
**Run workflow** button (workflow_dispatch) to trigger manually.

> **First run** seeds every current feed item as "already seen" and posts
> nothing — this avoids dumping the backlog. Only items published after the
> first run are posted thereafter.

## Local development

```bash
pip install -r requirements-dev.txt
pytest -v                          # run the test suite
python -m aggregator.main --dry-run   # print messages without sending or persisting
```
