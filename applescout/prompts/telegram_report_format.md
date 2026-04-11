# AppleScout Telegram Report Format

This prompt-style reference captures the delivery shape expected by the Telegram formatter.

Sections, in order:

1. Header with date and Gemini attribution
2. Stock snapshot
3. Overall AI sentiment
4. Executive summary
5. Key insights
6. Top topic hashtags
7. Market outlook
8. Opportunities
9. Risks
10. Detailed analysis
11. Source counts

Formatting rules:

- Telegram HTML parse mode
- Escape user/model-provided text
- Split messages above 4096 characters on section boundaries
- Preserve a concise analyst-report tone

Rationale:

- This belongs in `prompts/` because it defines the report presentation contract for AI-derived output.
