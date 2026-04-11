# AppleScout News Sources

Primary sources used by `applescout/scripts/collect_news.py`:

- Google News RSS
  - `https://news.google.com/rss/search?q=Apple+OR+AAPL&hl=en-US&gl=US&ceid=US:en`
- Apple Newsroom RSS
  - `https://www.apple.com/newsroom/rss-feed.rss`
- MacRumors RSS
  - `https://www.macrumors.com/feed/`
- 9to5Mac RSS
  - `https://9to5mac.com/feed/`
- AppleInsider RSS
  - `https://appleinsider.com/rss/news/`

Collection rules:

- Keep only articles from the last 24 hours by parseable published timestamp
- Deduplicate by URL
- Cap output to 50 recent items
