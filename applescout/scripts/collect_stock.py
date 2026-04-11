#!/usr/bin/env python3
"""Collect AAPL stock data into `.tmp/stock_data.json`."""

from __future__ import annotations

import csv
import io
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from applescout.scripts.utils_io import write_json_atomic
from applescout.scripts.utils_paths import tmp_file


def _fetch_from_stooq(symbol: str) -> dict:
    print(f"  📡 Trying Stooq for {symbol}...")
    stooq_symbol = f"{symbol}.US"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=14)
    url = (
        "https://stooq.com/q/d/l/"
        f"?s={stooq_symbol}"
        f"&d1={start_date.strftime('%Y%m%d')}"
        f"&d2={end_date.strftime('%Y%m%d')}"
        "&i=d"
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    reader = csv.DictReader(io.StringIO(resp.text))
    rows = list(reader)
    if not rows:
        raise ValueError("No data returned from Stooq")
    first_row = rows[0]
    if "Close" not in first_row and "close" not in first_row:
        raise ValueError(f"Invalid data format from Stooq: {first_row}")

    def get_val(row: dict, key: str) -> float:
        return float(row.get(key, row.get(key.lower(), row.get(key.upper(), 0))))

    latest = rows[-1]
    current_price = get_val(latest, "Close")
    if current_price == 0:
        raise ValueError("Got zero price from Stooq")
    if len(rows) > 1:
        prev_price = get_val(rows[-2], "Close")
        change = current_price - prev_price
        change_percent = (change / prev_price) * 100 if prev_price else 0
    else:
        change = 0
        change_percent = 0
    if len(rows) >= 5:
        first_price = get_val(rows[-5], "Close")
        trend_change = ((current_price - first_price) / first_price) * 100 if first_price else 0
        trend = "상승" if trend_change > 1 else "하락" if trend_change < -1 else "보합"
    else:
        trend = "데이터 부족"
    volume = int(get_val(latest, "Volume")) if get_val(latest, "Volume") else 0
    return {
        "symbol": symbol,
        "current_price": round(current_price, 2),
        "change": round(change, 2),
        "change_percent": round(change_percent, 2),
        "volume": volume,
        "market_cap": 0,
        "52_week_high": 0,
        "52_week_low": 0,
        "trend_5day": trend,
        "last_updated": datetime.now().isoformat(),
        "source": "stooq",
    }


def _fetch_from_yahoo_chart(symbol: str) -> dict:
    print(f"  📡 Trying Yahoo Finance Chart API for {symbol}...")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": "5d", "interval": "1d", "includePrePost": "false"}
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    chart = data.get("chart", {})
    result = chart.get("result", [])
    if not result:
        raise ValueError(f"Yahoo Chart API error: {chart.get('error', {})}")
    result = result[0]
    meta = result.get("meta", {})
    quotes = result.get("indicators", {}).get("quote", [{}])[0]
    valid_closes = [close for close in quotes.get("close", []) if close is not None]
    if not valid_closes:
        raise ValueError("No valid close prices from Yahoo Chart API")
    current_price = valid_closes[-1]
    if len(valid_closes) > 1:
        prev_price = valid_closes[-2]
        change = current_price - prev_price
        change_percent = (change / prev_price) * 100 if prev_price else 0
    else:
        change = 0
        change_percent = 0
    if len(valid_closes) >= 5:
        first_price = valid_closes[-5]
        trend_change = ((current_price - first_price) / first_price) * 100 if first_price else 0
        trend = "상승" if trend_change > 1 else "하락" if trend_change < -1 else "보합"
    else:
        trend = "데이터 부족"
    valid_volumes = [volume for volume in quotes.get("volume", []) if volume is not None]
    return {
        "symbol": symbol,
        "current_price": round(current_price, 2),
        "change": round(change, 2),
        "change_percent": round(change_percent, 2),
        "volume": int(valid_volumes[-1]) if valid_volumes else 0,
        "market_cap": meta.get("marketCap", 0) or 0,
        "52_week_high": meta.get("fiftyTwoWeekHigh", 0) or 0,
        "52_week_low": meta.get("fiftyTwoWeekLow", 0) or 0,
        "trend_5day": trend,
        "last_updated": datetime.now().isoformat(),
        "source": "yahoo_chart",
    }


def _fetch_from_google_finance(symbol: str) -> dict:
    print(f"  📡 Trying Google Finance scraping for {symbol}...")
    url = f"https://www.google.com/finance/quote/{symbol}:NASDAQ"
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    html = resp.text
    price_match = re.search(r'data-last-price="([\d.]+)"', html)
    if not price_match:
        raise ValueError("Could not find price in Google Finance page")
    current_price = float(price_match.group(1))
    pct_match = re.search(r'data-last-normal-market-change-percent="([-\d.]+)"', html)
    change_pct = float(pct_match.group(1)) if pct_match else 0
    change_val_match = re.search(r'data-last-normal-market-change="([-\d.]+)"', html)
    change_val = float(change_val_match.group(1)) if change_val_match else 0
    return {
        "symbol": symbol,
        "current_price": round(current_price, 2),
        "change": round(change_val, 2),
        "change_percent": round(change_pct, 2),
        "volume": 0,
        "market_cap": 0,
        "52_week_high": 0,
        "52_week_low": 0,
        "trend_5day": "데이터 없음",
        "last_updated": datetime.now().isoformat(),
        "source": "google_finance",
    }


def fetch_stock_data(symbol: str = "AAPL") -> dict:
    print(f"📈 Fetching stock data for {symbol}...")
    sources = [
        ("Stooq", _fetch_from_stooq),
        ("Yahoo Chart API", _fetch_from_yahoo_chart),
        ("Google Finance", _fetch_from_google_finance),
    ]
    last_error = None
    for source_name, fetch_func in sources:
        try:
            stock_data = fetch_func(symbol)
            print(f"  ✓ Success via {source_name}")
            print(f"  ✓ Current price: ${stock_data['current_price']} ({stock_data['change_percent']:+.2f}%)")
            print(f"  ✓ 5-day trend: {stock_data.get('trend_5day', 'N/A')}")
            print(f"  ✓ Volume: {stock_data['volume']:,}")
            return stock_data
        except Exception as exc:
            print(f"  ✗ {source_name} failed: {exc}")
            last_error = exc
    print(f"✗ All sources failed. Last error: {last_error}")
    print("⚠️  Returning placeholder data...")
    return {
        "symbol": symbol,
        "current_price": 0,
        "change": 0,
        "change_percent": 0,
        "volume": 0,
        "market_cap": 0,
        "52_week_high": 0,
        "52_week_low": 0,
        "trend_5day": "데이터 없음",
        "last_updated": datetime.now().isoformat(),
        "source": "none",
        "error": str(last_error),
    }


def main() -> bool:
    print("💰 Starting stock data collection...")
    stock_data = fetch_stock_data("AAPL")
    if not stock_data or stock_data.get("current_price", 0) == 0:
        print("⚠️  Warning: Could not fetch real stock data")
    output_file = tmp_file("stock_data.json")
    write_json_atomic(output_file, stock_data)
    print(f"✅ Saved stock data to {output_file}")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
