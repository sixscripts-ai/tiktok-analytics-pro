from __future__ import annotations
from typing import Dict, Any, List, Optional
import json
from collections import defaultdict

from scrapers.utils_loader import load_videos_any, canon_hashtag
try:
    from ..models import Video
except ImportError:  # pragma: no cover
    from models import Video

def hashtag_efficacy(username: str, min_uses: int = 5, videos: Optional[List[Video]] = None, videos_file: Optional[str] = None) -> Dict[str, Any]:
    """Analyze hashtag performance and effectiveness."""
    
    videos = videos or []
    if not videos and videos_file:
        videos = [Video.parse_obj(v) if not isinstance(v, Video) else v for v in load_videos_any(videos_file)]
    videos = [v.dict() if isinstance(v, Video) else v for v in videos]
    
    if not videos:
        return {
            'username': username,
            'scores': [],
            'top_hashtags': [],
            'hashtag_count': 0
        }
    
    # Collect hashtag data
    hashtag_videos = defaultdict(list)
    hashtag_engagement = defaultdict(list)
    
    for video in videos:
        # Extract hashtags
        tags = video.get('hashtags') or video.get('tags') or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.replace(',', ' ').split() if t.strip()]
        
        # Calculate engagement rate
        views = float(video.get('views') or video.get('play_count') or 0)
        likes = float(video.get('likes') or 0)
        comments = float(video.get('comments') or 0)
        shares = float(video.get('shares') or 0)
        
        if views > 0:
            engagement_rate = (likes + comments + shares) / views
        else:
            engagement_rate = 0
        
        # Process each hashtag
        for tag in tags:
            canon_tag = canon_hashtag(tag)
            if canon_tag:
                hashtag_videos[canon_tag].append(video)
                hashtag_engagement[canon_tag].append(engagement_rate)
    
    # Calculate baseline engagement (average across all videos)
    all_engagement_rates = []
    for video in videos:
        views = float(video.get('views') or video.get('play_count') or 0)
        likes = float(video.get('likes') or 0)
        comments = float(video.get('comments') or 0)
        shares = float(video.get('shares') or 0)
        
        if views > 0:
            engagement_rate = (likes + comments + shares) / views
            all_engagement_rates.append(engagement_rate)
    
    baseline_engagement = sum(all_engagement_rates) / len(all_engagement_rates) if all_engagement_rates else 0
    
    # Calculate hashtag efficacy scores
    scores = []
    for hashtag, engagement_rates in hashtag_engagement.items():
        if len(engagement_rates) >= min_uses:
            avg_engagement = sum(engagement_rates) / len(engagement_rates)
            lift = (avg_engagement - baseline_engagement) / baseline_engagement if baseline_engagement > 0 else 0
            
            scores.append({
                'hashtag': hashtag,
                'avg_engagement_rate': round(avg_engagement, 4),
                'baseline_engagement': round(baseline_engagement, 4),
                'lift_percentage': round(lift * 100, 2),
                'video_count': len(engagement_rates),
                'total_views': sum(float(v.get('views') or v.get('play_count') or 0) for v in hashtag_videos[hashtag]),
                'total_likes': sum(float(v.get('likes') or 0) for v in hashtag_videos[hashtag]),
                'total_comments': sum(float(v.get('comments') or 0) for v in hashtag_videos[hashtag]),
                'total_shares': sum(float(v.get('shares') or 0) for v in hashtag_videos[hashtag])
            })
    
    # Sort by lift percentage
    scores.sort(key=lambda x: x['lift_percentage'], reverse=True)
    
    # Top hashtags by usage
    top_hashtags = []
    for hashtag, videos_list in hashtag_videos.items():
        if len(videos_list) >= min_uses:
            total_views = sum(float(v.get('views') or v.get('play_count') or 0) for v in videos_list)
            total_likes = sum(float(v.get('likes') or 0) for v in videos_list)
            
            top_hashtags.append({
                'hashtag': hashtag,
                'usage_count': len(videos_list),
                'total_views': total_views,
                'total_likes': total_likes,
                'avg_views_per_video': round(total_views / len(videos_list), 2)
            })
    
    top_hashtags.sort(key=lambda x: x['usage_count'], reverse=True)
    
    return {
        'username': username,
        'scores': scores[:20],  # Top 20 hashtags by lift
        'top_hashtags': top_hashtags[:20],  # Top 20 hashtags by usage
        'hashtag_count': len(hashtag_videos),
        'baseline_engagement': round(baseline_engagement, 4),
        'total_videos_analyzed': len(videos)
    }
