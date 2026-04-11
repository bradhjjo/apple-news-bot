# AppleScout Skill

AppleScout is an OpenClaw-style skill for collecting Apple news, social discussion, and AAPL market context, then producing a Gemini-backed Telegram report.

## When To Use

- Daily Apple intelligence briefs
- Dry-run validation of the reporting pipeline
- Cron-driven automation from OpenClaw or another external scheduler

## Structure

- `scripts/run_applescout.py`: end-to-end orchestration
- `scripts/collect_news.py`: RSS/news collection
- `scripts/collect_social.py`: Reddit, Hacker News, and discussion feed collection
- `scripts/collect_stock.py`: AAPL market snapshot collection
- `scripts/analyze_gemini.py`: Gemini analysis and report JSON generation
- `scripts/format_report.py`: Telegram-safe report formatting
- `scripts/send_report.py`: Telegram delivery or dry-run preview
- `prompts/`: analysis and formatting prompt contracts
- `references/`: source inventories and migration notes

## Inputs

- Environment variables from `.env`
- Optional namespaced fallbacks:
  - `APPLESCOUT_TELEGRAM_BOT_TOKEN`
  - `APPLESCOUT_TELEGRAM_CHAT_ID`
  - `APPLESCOUT_GEMINI_API_KEY`
  - `APPLESCOUT_DRY_RUN`
- Intermediate JSON files in `.tmp/`

## Outputs

- `.tmp/news_articles.json`
- `.tmp/social_posts.json`
- `.tmp/stock_data.json`
- `.tmp/gemini_report.json`
- `.tmp/telegram_message_preview.txt` when dry-run is enabled

## Run

Manual full run:

```bash
python applescout/scripts/run_applescout.py
```

Dry-run without Telegram delivery:

```bash
python applescout/scripts/run_applescout.py --dry-run
```

Single-stage examples:

```bash
python applescout/scripts/collect_news.py
python applescout/scripts/analyze_gemini.py
python applescout/scripts/send_report.py --dry-run
```

## Notes

- Existing `execution/*.py` files remain as compatibility entrypoints and delegate into the skill-oriented scripts.
- `execution/scheduler.py` is deprecated. Prefer OpenClaw cron or another external scheduler invoking `applescout/scripts/run_applescout.py`.
- Direct Telegram delivery remains in place for now. OpenClaw message-tool integration is intentionally out of scope for this migration.
