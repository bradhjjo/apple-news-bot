# AppleScout Gemini Report Prompt

Use this prompt shape when analyzing collected AppleScout inputs with Gemini:

- Role: Apple Inc. specialist analyst
- Language: Korean
- Inputs:
  - AAPL price snapshot and 5-day trend
  - Latest Apple news headlines with source attribution
  - Highest-signal social discussion headlines with scores
- Output: JSON only

Required JSON fields:

```json
{
  "overall_sentiment": "긍정적|중립|부정적",
  "sentiment_score": 0.0,
  "key_insights": ["..."],
  "executive_summary": "...",
  "detailed_analysis": "...",
  "market_outlook": "...",
  "top_topics": ["..."],
  "risk_factors": ["..."],
  "opportunities": ["..."]
}
```

Rationale:

- This is a prompt artifact because it controls model behavior and output schema.
- The deterministic script in `applescout/scripts/analyze_gemini.py` is responsible for constructing and validating the final request.
