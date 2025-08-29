from __future__ import annotations
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta
from collections import defaultdict

from scrapers.utils_loader import load_videos_any
# {{ import ValidationError for flexible Video parsing }}
from pydantic import ValidationError
try:
    from ..models import Video
except ImportError:  # pragma: no cover
    from models import Video
# }}

def posting_time_optimizer(username: str, tz: str = 'UTC', window_days: int = 60, videos: Optional[List[Video]] = None, videos_file: Optional[str] = None) -> Dict[str, Any]:
    """Analyze optimal posting times based on video performance."""
    
    # {{ load videos gracefully even if missing required fields }}
    videos = videos or []
    if not videos and videos_file:
        raw_videos = load_videos_any(videos_file)
        videos = []
        for v in raw_videos:
            if isinstance(v, Video):
                videos.append(v)
            else:
                try:
                    videos.append(Video.model_validate(v))
                except ValidationError:
                    videos.append(v)
    videos = [v.dict() if isinstance(v, Video) else v for v in videos]
    # }}
    
    if not videos:
        return {
            'username': username,
            'windows': [],
            'best_days': [],
            'best_hours': [],
            'timezone': tz,
            'analysis_period_days': window_days
        }
    
    # Group videos by day of week and hour
    day_hour_performance = defaultdict(list)
    day_performance = defaultdict(list)
    hour_performance = defaultdict(list)
    
    for video in videos:
        # Extract creation time if available
        create_time = video.get('create_time') or video.get('created_at') or video.get('timestamp')
        if not create_time:
            continue
            
        try:
            # Parse timestamp
            if isinstance(create_time, (int, float)):
                dt = datetime.fromtimestamp(create_time)
            else:
                dt = datetime.fromisoformat(str(create_time).replace('Z', '+00:00'))
            
            day_of_week = dt.strftime('%A')
            hour = dt.hour
            
            # Calculate engagement rate
            views = float(video.get('views') or video.get('play_count') or 0)
            likes = float(video.get('likes') or 0)
            comments = float(video.get('comments') or 0)
            shares = float(video.get('shares') or 0)
            
            if views > 0:
                engagement_rate = (likes + comments + shares) / views
                day_hour_performance[(day_of_week, hour)].append(engagement_rate)
                day_performance[day_of_week].append(engagement_rate)
                hour_performance[hour].append(engagement_rate)
                
        except Exception:
            continue
    
    # Calculate average performance for each time slot
    windows = []
    for (day, hour), rates in day_hour_performance.items():
        if len(rates) >= 2:  # Need at least 2 videos for meaningful analysis
            avg_rate = sum(rates) / len(rates)
            windows.append({
                'day': day,
                'hour': hour,
                'avg_engagement_rate': round(avg_rate, 4),
                'video_count': len(rates),
                'time_slot': f"{day} {hour:02d}:00"
            })
    
    # Sort by engagement rate
    windows.sort(key=lambda x: x['avg_engagement_rate'], reverse=True)
    
    # Best days
    best_days = []
    for day, rates in day_performance.items():
        if len(rates) >= 2:
            avg_rate = sum(rates) / len(rates)
            best_days.append({
                'day': day,
                'avg_engagement_rate': round(avg_rate, 4),
                'video_count': len(rates)
            })
    best_days.sort(key=lambda x: x['avg_engagement_rate'], reverse=True)
    
    # Best hours
    best_hours = []
    for hour, rates in hour_performance.items():
        if len(rates) >= 2:
            avg_rate = sum(rates) / len(rates)
            best_hours.append({
                'hour': hour,
                'avg_engagement_rate': round(avg_rate, 4),
                'video_count': len(rates)
            })
    best_hours.sort(key=lambda x: x['avg_engagement_rate'], reverse=True)
    
    return {
        'username': username,
        'windows': windows[:10],  # Top 10 time slots
        'best_days': best_days[:7],
        'best_hours': best_hours[:24],
        'timezone': tz,
        'analysis_period_days': window_days,
        'total_videos_analyzed': len([v for v in videos if v.get('create_time')])
    }
