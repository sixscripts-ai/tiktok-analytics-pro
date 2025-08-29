from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional

# {{ TikTokPipeline orchestrates scraping, analytics, and data persistence }}
class TikTokPipeline:
    """Coordinate scraping, analytics, and storage operations."""

    def __init__(self, driver_factory: Optional[Callable[[], Any]] = None) -> None:
        self.driver_factory = driver_factory
        self.profile_data: Optional[Dict[str, Any]] = None
        self.video_data: List[Dict[str, Any]] = []
        self.analytics_data: Optional[Dict[str, Any]] = None

    # {{ scraping methods }}
    def scrape_profile(self, username: str) -> Dict[str, Any]:
        from tiktok_scraping_scripts.profile_scraper import scrape_profile as _scrape_profile
        self.profile_data = _scrape_profile(username, driver_factory=self.driver_factory)
        return self.profile_data

    def scrape_videos(self, username: str, limit: int = 200, include_comments: bool = False) -> List[Dict[str, Any]]:
        from tiktok_scraping_scripts.video_data_extractor import run as _scrape_videos
        self.video_data = _scrape_videos(
            username,
            limit=limit,
            include_comments=include_comments,
            driver_factory=self.driver_factory,
        )
        return self.video_data

    # {{ analytics method }}
    def run_analytics(
        self,
        username: str,
        videos_file: Optional[str] = None,
        tz: str = "UTC",
        window_days: int = 60,
    ) -> Dict[str, Any]:
        from tiktok_scraping_scripts.engagement_analyzer import run as _run
        self.analytics_data = _run(
            username,
            videos_file=videos_file,
            tz=tz,
            window_days=window_days,
        )
        return self.analytics_data

    # {{ persistence method }}
    def persist_results(self, output_path: str, fmt: Optional[str] = None) -> None:
        from tiktok_scraping_scripts.data_processor import export as _export
        if not self.video_data:
            raise ValueError("No video data to persist")
        _export(self.video_data, output_path, fmt=fmt)
