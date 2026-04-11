# AppleScout Social Sources

Primary sources used by `applescout/scripts/collect_social.py`:

- Reddit RSS
  - `r/apple`
  - `r/stocks`
  - `r/investing`
  - `r/wallstreetbets`
- Google News opinion/discussion RSS searches
  - `Apple stock analysis`
  - `AAPL stock opinion`
  - `Apple earnings discussion`
- Seeking Alpha combined feed
  - `https://seekingalpha.com/api/sa/combined/AAPL.xml`
- Hacker News API
  - `https://hacker-news.firebaseio.com/v0/`

Collection rules:

- Filter to recent posts from the last 24 hours
- Sort by recency, then score
- Continue pipeline even when this stage returns zero items
