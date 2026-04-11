# AppleScout OpenClaw Notes

This repo is now organized so AppleScout can be consumed as an OpenClaw/AppleScout skill from `applescout/`.

Current status:

- Skill docs live in `applescout/SKILL.md`
- Executable skill scripts live in `applescout/scripts/`
- Existing `execution/` entrypoints remain for backward compatibility
- Telegram delivery remains direct and is intentionally not migrated to an OpenClaw message tool yet

Scheduling:

- `execution/scheduler.py` is deprecated
- Prefer OpenClaw cron/job scheduling around `applescout/scripts/run_applescout.py`
