
from __future__ import annotations
from typing import Dict, Any, Optional, List
import json
from statistics import mean

from scrapers.utils_loader import load_videos_any, canon_hashtag
from analytics.posting_time_optimizer import posting_time_optimizer
from analytics.hashtag_efficacy import hashtag_efficacy
from analytics.sound_lifespan import sound_lifespan

def _engagement_rate(v: dict) -> float:
    views = float(v.get('views') or v.get('play_count') or 0)
    if views <= 0:
        return 0.0
    likes = float(v.get('likes') or 0)
    comments = float(v.get('comments') or 0)
    shares = float(v.get('shares') or 0)
    return (likes + comments + shares) / views

def summarize_engagement(videos: List[dict]) -> Dict[str, Any]:
    if not videos:
        return {'overall': {}, 'by_hashtag': [], 'top_videos': []}
    ers = [_engagement_rate(v) for v in videos]
    overall = {
        'videos': len(videos),
        'avg_engagement_rate': round(mean(ers), 4) if ers else 0.0,
        'avg_views': round(mean([float(v.get('views') or v.get('play_count') or 0) for v in videos]), 2),
        'share_to_view': round(mean([(float(v.get('shares') or 0) / max(1.0, float(v.get('views') or v.get('play_count') or 0))) for v in videos]), 6),
        'comment_to_view': round(mean([(float(v.get('comments') or 0) / max(1.0, float(v.get('views') or v.get('play_count') or 0))) for v in videos]), 6),
    }
    # by hashtag
    tag_stats = {}
    for v in videos:
        tags = v.get('hashtags') or v.get('tags') or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.replace(',', ' ').split() if t.strip()]
        er = _engagement_rate(v)
        for t in tags:
            ch = canon_hashtag(t)
            if not ch: continue
            tag_stats.setdefault(ch, []).append(er)
    by_hashtag = [{'hashtag': t, 'avg_er': round(mean(vals), 4), 'n': len(vals)} for t, vals in tag_stats.items() if vals]
    by_hashtag.sort(key=lambda x: (-x['avg_er'], -x['n']))
    # top videos by ER
    top_videos = sorted(videos, key=lambda v: _engagement_rate(v), reverse=True)[:10]
    return {'overall': overall, 'by_hashtag': by_hashtag[:50], 'top_videos': top_videos}

def run(username: str, videos_file: Optional[str]=None, tz: str='UTC', window_days: int=60, videos: Optional[List[Video]] = None) -> Dict[str, Any]:
    videos = videos or []
    if not videos and videos_file:
        videos = [Video.parse_obj(v) if not isinstance(v, Video) else v for v in load_videos_any(videos_file)]
    vids_dict = [v.dict() if isinstance(v, Video) else v for v in videos]
    summary = summarize_engagement(vids_dict)
    pto = posting_time_optimizer(username, tz=tz, window_days=window_days, videos=videos, videos_file=videos_file)
    he = hashtag_efficacy(username, videos=videos, videos_file=videos_file)
    sl = sound_lifespan(username=username, videos=videos, videos_file=videos_file)
    return {
        'username': username,
        'engagement': summary,
        'posting_windows': pto.get('windows', []),
        'hashtag_lift': he.get('scores', []),
        'top_sound': sl,
    }

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--username', required=True)
    ap.add_argument('--videos-file', default=None)
    ap.add_argument('--tz', default='UTC')
    ap.add_argument('--window', type=int, default=60)
    args = ap.parse_args()
    print(json.dumps(run(args.username, videos_file=args.videos_file, tz=args.tz, window_days=args.window), indent=2))
