from __future__ import annotations

import random
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup


class UnifiedTikTokAnalyzer:
    """Configurable TikTok analytics engine."""

    DEFAULT_SOURCES = {
        "basic": ["tiktok"],
        "advanced": ["tiktok", "socialblade"],
        "deep": ["tiktok", "socialblade", "tiktokmetrics"],
    }

    def __init__(
        self,
        depth: str = "basic",
        data_sources: Optional[List[str]] = None,
        earnings_model: str = "detailed",
    ) -> None:
        self.depth = depth
        self.data_sources = data_sources if data_sources is not None else self.DEFAULT_SOURCES.get(depth, ["tiktok"])
        self.earnings_model = earnings_model
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        self.setup_session()

    def setup_session(self) -> None:
        self.session.headers.update(
            {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
            }
        )

    def extract_username(self, url: str) -> Optional[str]:
        try:
            if "?" in url:
                url = url.split("?")[0]
            patterns = [
                r"@([a-zA-Z0-9._]+)",
                r"tiktok\\.com/@([a-zA-Z0-9._]+)",
                r"/([a-zA-Z0-9._]+)\\?'",
            ]
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            return None
        except Exception:
            return None

    def scrape_tiktok_profile(self, username: str) -> Optional[Dict[str, str]]:
        try:
            url = f"https://www.tiktok.com/@{username}"
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                page_text = soup.get_text()
                match = re.search(r"(\d+(?:\.\d+)?[KMB]?)\s*followers", page_text, re.IGNORECASE)
                if match:
                    return {"followers": match.group(1)}
            return None
        except Exception:
            return None

    def scrape_socialblade(self, username: str) -> Optional[Dict[str, str]]:
        try:
            url = f"https://socialblade.com/tiktok/user/{username}/monthly"
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                follower_elements = soup.find_all("span", class_="YouTubeUserTopHeader")
                for element in follower_elements:
                    text = element.get_text()
                    if any(char.isdigit() for char in text) and any(unit in text.upper() for unit in ["K", "M", "B"]):
                        return {"followers": text.strip()}
            return None
        except Exception:
            return None

    def scrape_tiktokmetrics(self, username: str) -> Optional[Dict[str, str]]:
        try:
            url = f"https://tiktokmetrics.com/@{username}"
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                metric_elements = soup.find_all(["div", "span"], class_=["metric", "stat", "number"])
                for element in metric_elements:
                    text = element.get_text().strip()
                    if text and any(char.isdigit() for char in text):
                        if "followers" in text.lower():
                            return {"followers": text}
            return None
        except Exception:
            return None

    def convert_count_to_number(self, count_text: Optional[str]) -> float:
        try:
            if not count_text:
                return 0
            count_text = count_text.strip().upper()
            if "B" in count_text:
                return float(count_text.replace("B", "")) * 1_000_000_000
            if "M" in count_text:
                return float(count_text.replace("M", "")) * 1_000_000
            if "K" in count_text:
                return float(count_text.replace("K", "")) * 1_000
            return float(count_text.replace(",", ""))
        except Exception:
            return 0.0

    def calculate_earnings(self, follower_count: float) -> Dict[str, Any]:
        if self.earnings_model == "basic":
            monthly = follower_count * 0.02
            return {"monthly": round(monthly, 2), "yearly": round(monthly * 12, 2), "breakdown": {}}

        cpm_earnings = follower_count * 0.1 * 1.25 / 1000
        engagement_earnings = follower_count * 0.035 * 0.01
        brand_deals = follower_count * 0.025
        live_stream = follower_count * 0.01 * 1
        merchandise = follower_count * 0.005 * 10

        total_monthly = cpm_earnings + engagement_earnings + brand_deals + live_stream + merchandise

        return {
            "monthly": round(total_monthly, 2),
            "yearly": round(total_monthly * 12, 2),
            "breakdown": {
                "cpm": round(cpm_earnings, 2),
                "engagement": round(engagement_earnings, 2),
                "brand_deals": round(brand_deals, 2),
                "live_stream": round(live_stream, 2),
                "merchandise": round(merchandise, 2),
            },
        }

    def analyze(self, tiktok_url: str) -> Optional[Dict[str, Any]]:
        username = self.extract_username(tiktok_url)
        if not username:
            return None

        tiktok_data: Optional[Dict[str, str]] = None
        socialblade_data: Optional[Dict[str, str]] = None
        metrics_data: Optional[Dict[str, str]] = None

        if "tiktok" in self.data_sources:
            tiktok_data = self.scrape_tiktok_profile(username)
        if "socialblade" in self.data_sources:
            socialblade_data = self.scrape_socialblade(username)
        if "tiktokmetrics" in self.data_sources:
            metrics_data = self.scrape_tiktokmetrics(username)

        follower_count = 0.0
        follower_source = "estimated"

        if socialblade_data and "followers" in socialblade_data:
            follower_count = self.convert_count_to_number(socialblade_data["followers"])
            follower_source = "SocialBlade"
        elif metrics_data and "followers" in metrics_data:
            follower_count = self.convert_count_to_number(metrics_data["followers"])
            follower_source = "TikTokMetrics"
        elif tiktok_data and "followers" in tiktok_data:
            follower_count = self.convert_count_to_number(tiktok_data["followers"])
            follower_source = "TikTok Profile"

        earnings = self.calculate_earnings(follower_count)

        return {
            "username": username,
            "url": tiktok_url,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "follower_count": follower_count,
            "follower_source": follower_source,
            "tiktok_data": tiktok_data,
            "socialblade_data": socialblade_data,
            "metrics_data": metrics_data,
            "earnings_estimate": earnings,
        }
