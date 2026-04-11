import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from applescout.scripts.collect_stock import fetch_stock_data


def test_fetch_stock_placeholder(monkeypatch):
    def always_fail(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr("applescout.scripts.collect_stock._fetch_from_stooq", always_fail)
    monkeypatch.setattr("applescout.scripts.collect_stock._fetch_from_yahoo_chart", always_fail)
    monkeypatch.setattr("applescout.scripts.collect_stock._fetch_from_google_finance", always_fail)

    result = fetch_stock_data("AAPL")

    assert result["symbol"] == "AAPL"
    assert result["source"] == "none"
    assert result["current_price"] == 0
