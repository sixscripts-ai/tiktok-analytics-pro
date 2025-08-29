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

def sound_lifespan(sound_id: Optional[str] = None, username: Optional[str] = None, videos: Optional[List[Video]] = None, videos_file: Optional[str] = None) -> Dict[str, Any]:
    """Analyze sound/music lifespan and popularity trends."""
    
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
            'sound_id': sound_id,
            'username': username,
            'sound_analysis': {},
            'trending_sounds': [],
            'sound_count': 0
        }
    
    # Collect sound data
    sound_videos = defaultdict(list)
    sound_engagement = defaultdict(list)
    sound_timeline = defaultdict(list)
    
    for video in videos:
        # Extract sound/music information
        music = video.get('music') or {}
        sound_title = music.get('title', 'Unknown Sound')
        sound_id_video = music.get('id')
        
        # Skip if we're looking for a specific sound and this doesn't match
        if sound_id and sound_id_video != sound_id:
            continue
        
        # Calculate engagement rate
        views = float(video.get('views') or video.get('play_count') or 0)
        likes = float(video.get('likes') or 0)
        comments = float(video.get('comments') or 0)
        shares = float(video.get('shares') or 0)
        
        if views > 0:
            engagement_rate = (likes + comments + shares) / views
        else:
            engagement_rate = 0
        
        # Extract creation time
        create_time = video.get('create_time') or video.get('created_at') or video.get('timestamp')
        
        sound_key = sound_id_video or sound_title
        
        sound_videos[sound_key].append(video)
        sound_engagement[sound_key].append(engagement_rate)
        
        if create_time:
            try:
                if isinstance(create_time, (int, float)):
                    dt = datetime.fromtimestamp(create_time)
                else:
                    dt = datetime.fromisoformat(str(create_time).replace('Z', '+00:00'))
                sound_timeline[sound_key].append(dt)
            except Exception:
                pass
    
    # Analyze specific sound if requested
    sound_analysis = {}
    if sound_id or (username and sound_videos):
        target_sound = sound_id or list(sound_videos.keys())[0]
        if target_sound in sound_videos:
            videos_list = sound_videos[target_sound]
            engagement_rates = sound_engagement[target_sound]
            timeline = sound_timeline[target_sound]
            
            if timeline:
                timeline.sort()
                first_use = timeline[0]
                last_use = timeline[-1]
                lifespan_days = (last_use - first_use).days
                
                # Calculate usage frequency
                usage_by_week = defaultdict(int)
                for dt in timeline:
                    week_key = dt.strftime('%Y-%W')
                    usage_by_week[week_key] += 1
                
                peak_week = max(usage_by_week.items(), key=lambda x: x[1]) if usage_by_week else None
                
                sound_analysis = {
                    'sound_id': target_sound,
                    'sound_title': videos_list[0].get('music', {}).get('title', 'Unknown'),
                    'total_uses': len(videos_list),
                    'lifespan_days': lifespan_days,
                    'first_use': first_use.isoformat(),
                    'last_use': last_use.isoformat(),
                    'avg_engagement_rate': round(sum(engagement_rates) / len(engagement_rates), 4) if engagement_rates else 0,
                    'total_views': sum(float(v.get('views') or v.get('play_count') or 0) for v in videos_list),
                    'total_likes': sum(float(v.get('likes') or 0) for v in videos_list),
                    'peak_week': peak_week[0] if peak_week else None,
                    'peak_week_uses': peak_week[1] if peak_week else 0,
                    'usage_trend': 'increasing' if len(timeline) > 1 and timeline[-1] > timeline[-2] else 'stable'
                }
    
    # Find trending sounds (most used recently)
    trending_sounds = []
    for sound_key, timeline in sound_timeline.items():
        if timeline:
            recent_uses = [dt for dt in timeline if dt > datetime.now() - timedelta(days=30)]
            total_uses = len(timeline)
            recent_uses_count = len(recent_uses)
            
            if recent_uses_count > 0:
                videos_list = sound_videos[sound_key]
                engagement_rates = sound_engagement[sound_key]
                
                trending_sounds.append({
                    'sound_id': sound_key,
                    'sound_title': videos_list[0].get('music', {}).get('title', 'Unknown'),
                    'total_uses': total_uses,
                    'recent_uses_30d': recent_uses_count,
                    'avg_engagement_rate': round(sum(engagement_rates) / len(engagement_rates), 4) if engagement_rates else 0,
                    'total_views': sum(float(v.get('views') or v.get('play_count') or 0) for v in videos_list),
                    'trend_score': recent_uses_count / max(total_uses, 1)  # Higher score = more recent usage
                })
    
    # Sort by trend score
    trending_sounds.sort(key=lambda x: x['trend_score'], reverse=True)
    
    return {
        'sound_id': sound_id,
        'username': username,
        'sound_analysis': sound_analysis,
        'trending_sounds': trending_sounds[:10],  # Top 10 trending sounds
        'sound_count': len(sound_videos),
        'total_videos_analyzed': len(videos)
    }
