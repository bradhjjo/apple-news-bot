# AppleScout Stock Sources

Primary sources used by `applescout/scripts/collect_stock.py`:

1. Stooq daily CSV
2. Yahoo Finance Chart API
3. Google Finance page scrape

Collection rules:

- Prefer free sources with no API key
- Attempt sources in order and stop on first usable result
- Return placeholder stock data instead of hard-failing the pipeline
