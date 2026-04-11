#!/usr/bin/env python3
"""Analyze collected inputs with Gemini and persist `.tmp/gemini_report.json`."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from applescout.scripts.utils_io import env_first, load_json, write_json_atomic
from applescout.scripts.utils_paths import repo_root, tmp_file


def configure_gemini():
    from google import genai

    api_key = env_first("APPLESCOUT_GEMINI_API_KEY", "GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)
    return client


def build_prompt(news_articles: List[Dict], social_posts: List[Dict], stock_data: Dict) -> str:
    prompt = f"""당신은 애플(Apple Inc.) 전문 애널리스트입니다. 다음 데이터를 분석하여 한국어로 종합 리포트를 작성해주세요.

## 주가 정보
- 현재가: ${stock_data.get('current_price', 'N/A')}
- 변동률: {stock_data.get('change_percent', 'N/A')}%
- 5일 트렌드: {stock_data.get('trend_5day', 'N/A')}

## 최신 뉴스 ({len(news_articles)}개)
"""
    for index, article in enumerate(news_articles[:10], 1):
        prompt += f"{index}. {article['title']} (출처: {article['source']})\n"
    prompt += f"\n## 소셜 미디어 반응 ({len(social_posts)}개)\n"
    for index, post in enumerate(social_posts[:5], 1):
        prompt += f"{index}. {post['title']} (점수: {post.get('score', 0)})\n"
    prompt += """

다음 형식으로 JSON 응답을 작성해주세요:

{
  "overall_sentiment": "긍정적|중립|부정적",
  "sentiment_score": 0.0-1.0 사이의 숫자,
  "key_insights": [
    "핵심 인사이트 1",
    "핵심 인사이트 2",
    "핵심 인사이트 3"
  ],
  "executive_summary": "200자 이내의 전체 요약",
  "detailed_analysis": "500자 이내의 상세 분석",
  "market_outlook": "향후 전망 (100자 이내)",
  "top_topics": ["주요 토픽1", "주요 토픽2", "주요 토픽3"],
  "risk_factors": ["리스크 요인1", "리스크 요인2"],
  "opportunities": ["기회 요인1", "기회 요인2"]
}

JSON만 반환하고 다른 텍스트는 포함하지 마세요."""
    return prompt


def analyze_with_gemini(news_articles: List[Dict], social_posts: List[Dict], stock_data: Dict) -> Dict:
    print("🤖 Starting Gemini AI analysis...")
    try:
        client = configure_gemini()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=build_prompt(news_articles, social_posts, stock_data)
        )
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        analysis = json.loads(response_text.strip())
        print("✓ Gemini analysis completed")
        print(f"✓ Sentiment: {analysis.get('overall_sentiment')}")
        print(f"✓ Key insights: {len(analysis.get('key_insights', []))}")
        return analysis
    except Exception as exc:
        print(f"✗ Gemini analysis failed: {exc}")
        print("⚠️  Falling back to basic analysis...")
        return {
            "overall_sentiment": "중립",
            "sentiment_score": 0.5,
            "key_insights": [
                f"{len(news_articles)}개의 뉴스 기사 수집됨",
                f"{len(social_posts)}개의 소셜 미디어 포스트 분석됨",
                "AI 분석을 사용할 수 없어 기본 분석 제공",
            ],
            "executive_summary": f"애플 관련 {len(news_articles)}개 뉴스와 {len(social_posts)}개 소셜 포스트를 수집했습니다.",
            "detailed_analysis": "Gemini API를 사용할 수 없어 상세 분석을 제공할 수 없습니다. API 키를 확인해주세요.",
            "market_outlook": "데이터 부족으로 전망 제공 불가",
            "top_topics": ["Apple", "iPhone", "Technology"],
            "risk_factors": ["API 연결 실패"],
            "opportunities": ["AI 분석 활성화 시 더 나은 인사이트 제공 가능"],
        }


def load_inputs() -> Dict:
    return {
        "news": load_json(tmp_file("news_articles.json"), []),
        "social": load_json(tmp_file("social_posts.json"), []),
        "stock": load_json(tmp_file("stock_data.json"), {}),
    }


def main() -> bool:
    print("🤖 Starting Gemini AI content analysis...")
    data = load_inputs()
    if not data["news"] and not data["social"]:
        print("❌ No data to analyze")
        return False
    print(f"✓ Loaded {len(data['news'])} news articles")
    print(f"✓ Loaded {len(data['social'])} social posts")
    gemini_analysis = analyze_with_gemini(data["news"], data["social"], data["stock"])
    sentiment_score = gemini_analysis.get("sentiment_score", 0)
    try:
        sentiment_score = float(sentiment_score)
    except (TypeError, ValueError):
        sentiment_score = 0

    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "stock": data["stock"],
        "gemini_analysis": gemini_analysis,
        "textblob_sentiment_score": round(sentiment_score, 2),
        "news_count": len(data["news"]),
        "social_count": len(data["social"]),
        "top_news": data["news"][:5],
        "top_social": data["social"][:5],
    }
    output_file = tmp_file("gemini_report.json")
    write_json_atomic(output_file, report)
    print(f"✅ Saved Gemini analysis report to {output_file}")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
