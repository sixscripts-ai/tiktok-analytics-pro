from __future__ import annotations
import asyncio
from typing import Any, Callable, Dict, List, Optional

# {{ TikTokPipeline orchestrates scraping, analytics, and data persistence }}
class TikTokPipeline:
    """Coordinate scraping, analytics, and storage operations."""

    def __init__(self, driver_factory: Optional[Callable[[], Any]] = None, enable_async: bool = False) -> None:
        self.driver_factory = driver_factory
        self.enable_async = enable_async
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

    # {{ async pipeline methods }}
    async def scrape_profile_async(self, username: str) -> Dict[str, Any]:
        """Async version of profile scraping using AsyncPipeline for faster fetching."""
        if not self.enable_async:
            return self.scrape_profile(username)
        
        from tiktok_scraping_scripts.async_pipeline import AsyncPipeline
        # For now, delegate to sync method but could be enhanced for true async scraping
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.scrape_profile, username)
        return result

    async def scrape_videos_async(self, username: str, limit: int = 200, include_comments: bool = False) -> List[Dict[str, Any]]:
        """Async version of video scraping with concurrent processing."""
        if not self.enable_async:
            return self.scrape_videos(username, limit, include_comments)
        
        from tiktok_scraping_scripts.async_pipeline import AsyncPipeline
        # For now, delegate to sync method but could be enhanced for true async scraping
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.scrape_videos, username, limit, include_comments)
        return result

    async def run_analytics_async(
        self,
        username: str,
        videos_file: Optional[str] = None,
        tz: str = "UTC",
        window_days: int = 60,
    ) -> Dict[str, Any]:
        """Async version of analytics processing."""
        if not self.enable_async:
            return self.run_analytics(username, videos_file, tz, window_days)
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.run_analytics, username, videos_file, tz, window_days)
        return result

    async def run_comprehensive_async(self, username: str, limit: int = 200) -> Dict[str, Any]:
        """Run a comprehensive async analysis including profile, videos, and analytics."""
        if not self.enable_async:
            # Fall back to sync methods
            profile_data = self.scrape_profile(username)
            video_data = self.scrape_videos(username, limit)
            analytics_data = self.run_analytics(username)
            return {
                "profile": profile_data,
                "videos": video_data,
                "analytics": analytics_data
            }
        
        # Run everything concurrently
        profile_task = self.scrape_profile_async(username)
        videos_task = self.scrape_videos_async(username, limit)
        
        profile_data, video_data = await asyncio.gather(profile_task, videos_task)
        
        # Run analytics after we have the data
        analytics_data = await self.run_analytics_async(username)
        
        return {
            "profile": profile_data,
            "videos": video_data,
            "analytics": analytics_data
        }
