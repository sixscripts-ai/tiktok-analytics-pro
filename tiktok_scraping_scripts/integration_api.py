#!/usr/bin/env python3
"""
TikTok Scraping Integration API
Provides endpoints for the dashboard to trigger scraping and get real data
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from profile_scraper import scrape_profile
from video_data_extractor import run as extract_videos
from earnings_calculator import run as calculate_earnings
from engagement_analyzer import run as analyze_engagement
from driver_loader import discover_driver_factory
from data.storage import Storage

class TikTokIntegrationAPI:
    """API for integrating TikTok scraping with the dashboard"""
    
    def __init__(self, data_dir: str = "scraped_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.storage = Storage(str(self.data_dir / "cache.db"))
        
    def scrape_profile_data(self, username: str) -> Dict[str, Any]:
        """Scrape profile data for a given username"""
        try:
            # Clean username
            username = username.strip().replace('@', '')
            
            # Check if we have recent data (within 1 hour)
            cached = self.storage.get_profile(username)
            if cached and (datetime.now() - cached.updated_at).total_seconds() < 3600:
                if cached.data and not cached.data.get("error"):
                    return cached.data
            
            # Scrape new data
            driver_factory = discover_driver_factory()
            result = scrape_profile(username, driver_factory=driver_factory)
            
            # Validate result
            if not result or not result.get("profile"):
                raise Exception("No profile data returned from scraper")
            
            # Save to storage
            try:
                self.storage.set_profile(username, result)
            except Exception:
                pass
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to scrape profile for @{username}: {str(e)}"
            return {
                "error": error_msg,
                "username": username,
                "profile": None,
                "timestamp": datetime.now().isoformat()
            }
    
    def scrape_video_data(self, username: str, limit: int = 50) -> Dict[str, Any]:
        """Scrape video data for a given username"""
        try:
            username = username.strip().replace('@', '')
            
            # Check for recent data
            cached = self.storage.get_videos(username)
            if cached and (datetime.now() - cached.updated_at).total_seconds() < 3600:
                if isinstance(cached.data, list) and len(cached.data) > 0:
                    return {"videos": cached.data}
            
            # Scrape new data
            driver_factory = discover_driver_factory()
            videos = extract_videos(username, limit=limit, driver_factory=driver_factory)
            
            # Validate result
            if not isinstance(videos, list):
                raise Exception("Invalid video data format returned")
            
            # Save to storage
            try:
                self.storage.set_videos(username, videos)
            except Exception:
                pass
            
            return {"videos": videos}
            
        except Exception as e:
            error_msg = f"Failed to scrape videos for @{username}: {str(e)}"
            return {
                "error": error_msg,
                "username": username,
                "videos": [],
                "timestamp": datetime.now().isoformat()
            }
    
    def get_earnings_analysis(self, username: str) -> Dict[str, Any]:
        """Get earnings analysis for a username"""
        try:
            username = username.strip().replace('@', '')
            
            # Get video data
            cached = self.storage.get_videos(username)
            if not cached:
                video_result = self.scrape_video_data(username)
                if "error" in video_result:
                    return video_result
                cached = self.storage.get_videos(username)

            with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tmp:
                json.dump(cached.data, tmp, indent=2, default=str)
                tmp_path = tmp.name
            try:
                result = calculate_earnings(username, videos_file=tmp_path)
            finally:
                os.unlink(tmp_path)
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "username": username,
                "models": {}
            }
    
    def get_engagement_analysis(self, username: str) -> Dict[str, Any]:
        """Get engagement analysis for a username"""
        try:
            username = username.strip().replace('@', '')
            
            # Get video data
            cached = self.storage.get_videos(username)
            if not cached:
                video_result = self.scrape_video_data(username)
                if "error" in video_result:
                    return video_result
                cached = self.storage.get_videos(username)

            with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tmp:
                json.dump(cached.data, tmp, indent=2, default=str)
                tmp_path = tmp.name
            try:
                result = analyze_engagement(username, videos_file=tmp_path)
            finally:
                os.unlink(tmp_path)
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "username": username,
                "engagement": {}
            }
    
    def get_comprehensive_analysis(self, username: str) -> Dict[str, Any]:
        """Get comprehensive analysis including profile, videos, earnings, and engagement"""
        try:
            username = username.strip().replace('@', '')
            
            # Scrape all data
            profile_data = self.scrape_profile_data(username)
            video_data = self.scrape_video_data(username)
            earnings_data = self.get_earnings_analysis(username)
            engagement_data = self.get_engagement_analysis(username)

            return {
                "username": username,
                "timestamp": datetime.now().isoformat(),
                "profile": profile_data.get("profile", {}),
                "videos": video_data.get("videos", []),
                "earnings": earnings_data.get("models", {}),
                "engagement": engagement_data.get("engagement", {}),
                "posting_windows": engagement_data.get("posting_windows", []),
                "hashtag_lift": engagement_data.get("hashtag_lift", []),
                "top_sound": engagement_data.get("top_sound"),
                "errors": [
                    data.get("error") for data in [profile_data, video_data, earnings_data, engagement_data]
                    if data.get("error")
                ]
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "username": username,
                "timestamp": datetime.now().isoformat()
            }

# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TikTok Integration API")
    parser.add_argument("--username", required=True, help="TikTok username to analyze")
    parser.add_argument("--type", choices=["profile", "videos", "earnings", "engagement", "comprehensive"], 
                       default="comprehensive", help="Type of analysis to perform")
    
    args = parser.parse_args()
    
    api = TikTokIntegrationAPI()
    
    if args.type == "profile":
        result = api.scrape_profile_data(args.username)
    elif args.type == "videos":
        result = api.scrape_video_data(args.username)
    elif args.type == "earnings":
        result = api.get_earnings_analysis(args.username)
    elif args.type == "engagement":
        result = api.get_engagement_analysis(args.username)
    else:  # comprehensive
        result = api.get_comprehensive_analysis(args.username)
    
    print(json.dumps(result, indent=2, default=str))
