#!/usr/bin/env python3
"""Formatting helpers for Telegram delivery."""

from __future__ import annotations

import html


def escape_html(value) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=False)


def sanitize_hashtag(value) -> str:
    normalized = str(value).replace(" ", "_")
    cleaned = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in normalized)
    cleaned = cleaned.strip("_")
    return f"#{cleaned}" if cleaned else ""


def format_gemini_report(report: dict) -> str:
    lines = []
    lines.append("🍎 <b>AppleScout Agent AI 리포트</b>")
    lines.append(f"📅 {escape_html(report['date'])}")
    lines.append("🤖 <i>Powered by Gemini</i>")
    lines.append("")
    stock = report.get("stock", {})
    if stock and stock.get("current_price"):
        price = stock["current_price"]
        change_pct = stock["change_percent"]
        trend_emoji = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
        sign = "+" if change_pct > 0 else ""
        lines.append("💰 <b>주가 정보</b>")
        lines.append(f"AAPL: ${price} ({sign}{change_pct}% {trend_emoji})")
        lines.append(f"5일 트렌드: {escape_html(stock.get('trend_5day', 'N/A'))}")
        lines.append("")
    gemini = report.get("gemini_analysis", {})
    sentiment = gemini.get("overall_sentiment", "중립")
    sentiment_score = gemini.get("sentiment_score", 0.5)
    sentiment_emoji = "😊" if sentiment == "긍정적" else "😐" if sentiment == "중립" else "😟"
    lines.append(f"{sentiment_emoji} <b>AI 감성 분석</b>")
    lines.append(f"{sentiment} ({sentiment_score}/1.0)")
    lines.append("")
    exec_summary = gemini.get("executive_summary", "")
    if exec_summary:
        lines.append("📊 <b>핵심 요약</b>")
        lines.append(escape_html(exec_summary))
        lines.append("")
    insights = gemini.get("key_insights", [])
    if insights:
        lines.append("💡 <b>주요 인사이트</b>")
        for index, insight in enumerate(insights[:5], 1):
            lines.append(f"{index}. {escape_html(insight)}")
        lines.append("")
    topics = gemini.get("top_topics", [])
    if topics:
        hashtags = [sanitize_hashtag(topic) for topic in topics[:8]]
        lines.append("🔑 <b>주요 토픽</b>")
        lines.append(" ".join(tag for tag in hashtags if tag))
        lines.append("")
    outlook = gemini.get("market_outlook", "")
    if outlook:
        lines.append("🔮 <b>시장 전망</b>")
        lines.append(escape_html(outlook))
        lines.append("")
    opportunities = gemini.get("opportunities", [])
    if opportunities:
        lines.append("✅ <b>기회 요인</b>")
        for item in opportunities[:3]:
            lines.append(f"• {escape_html(item)}")
        lines.append("")
    risks = gemini.get("risk_factors", [])
    if risks:
        lines.append("⚠️ <b>리스크 요인</b>")
        for item in risks[:3]:
            lines.append(f"• {escape_html(item)}")
        lines.append("")
    detailed = gemini.get("detailed_analysis", "")
    if detailed:
        lines.append("📝 <b>상세 분석</b>")
        lines.append(escape_html(detailed))
        lines.append("")
    lines.append("📈 <b>데이터 출처</b>")
    lines.append(f"뉴스: {report.get('news_count', 0)}개 | 소셜: {report.get('social_count', 0)}개")
    return "\n".join(lines)
