import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tiktok.unified_analyzer import UnifiedTikTokAnalyzer


def test_basic_mode(monkeypatch):
    analyzer = UnifiedTikTokAnalyzer(depth="basic")
    monkeypatch.setattr(analyzer, "scrape_tiktok_profile", lambda username: {"followers": "1K"})
    report = analyzer.analyze("https://www.tiktok.com/@tester")
    assert report["follower_count"] == 1000
    assert report["follower_source"] == "TikTok Profile"


def test_advanced_mode(monkeypatch):
    analyzer = UnifiedTikTokAnalyzer(depth="advanced")
    monkeypatch.setattr(analyzer, "scrape_tiktok_profile", lambda username: {"followers": "1K"})
    monkeypatch.setattr(analyzer, "scrape_socialblade", lambda username: {"followers": "2K"})
    report = analyzer.analyze("https://www.tiktok.com/@tester")
    assert report["follower_count"] == 2000
    assert report["follower_source"] == "SocialBlade"


def test_deep_mode(monkeypatch):
    analyzer = UnifiedTikTokAnalyzer(depth="deep")
    monkeypatch.setattr(analyzer, "scrape_tiktok_profile", lambda username: {"followers": "1K"})
    monkeypatch.setattr(analyzer, "scrape_socialblade", lambda username: None)
    monkeypatch.setattr(analyzer, "scrape_tiktokmetrics", lambda username: {"followers": "3K"})
    report = analyzer.analyze("https://www.tiktok.com/@tester")
    assert report["follower_count"] == 3000
    assert report["follower_source"] == "TikTokMetrics"
