
from __future__ import annotations
from typing import Dict, Any, Optional, List
import json, statistics as stats
from pathlib import Path

from scrapers.utils_loader import load_videos_any
from config import settings

DEFAULTS = {
    'brand_cpm_per_view': (0.02, 0.04, 0.08),      # $ per view equivalent via brand deals
    'creator_fund_rpm':   (0.02, 0.04, 0.06),      # $ per 1k views
    'affiliate_conv':     (0.3, 0.6, 1.2),         # % of 100 clicks -> sales (as absolute percent not fraction)
    'affiliate_aov':      (20, 40, 80),            # $ basket
    'affiliate_comm':     (0.08, 0.10, 0.15),      # % commission
    'merch_conv':         (0.6, 1.2, 2.0),         # % of engaged viewers purchasing
    'merch_aov':          (25, 45, 70),            # $ basket
    'merch_margin':       (0.25, 0.40, 0.55),      # gross margin
}

def _pick(triple, which='mid'):
    lo, md, hi = triple
    return {'low': lo, 'mid': md, 'high': hi}[which]

def _sum_views(videos: List[dict]) -> int:
    return int(sum(int(v.get('views') or v.get('play_count') or 0) for v in videos))

def brand_deal_estimate(videos: List[dict], params=DEFAULTS) -> Dict[str, Any]:
    total_views = _sum_views(videos)
    # Convert CPM-ish into per-view assumption
    lo, md, hi = params['brand_cpm_per_view']
    return {'low': round(total_views * lo, 2), 'mid': round(total_views * md, 2), 'high': round(total_views * hi, 2)}

def creator_fund_estimate(videos: List[dict], params=DEFAULTS) -> Dict[str, Any]:
    total_views = _sum_views(videos)
    lo, md, hi = params['creator_fund_rpm']
    # rpm is per 1k
    return {'low': round(total_views/1000.0 * lo, 2), 'mid': round(total_views/1000.0 * md, 2), 'high': round(total_views/1000.0 * hi, 2)}

def affiliate_estimate(videos: List[dict], params=DEFAULTS) -> Dict[str, Any]:
    total_views = _sum_views(videos)
    # assume clicks ~ 1-3% of viewers as a rough range
    click_rate = (0.01, 0.02, 0.03)
    clicks = tuple(total_views * r for r in click_rate)
    conv = params['affiliate_conv']
    aov = params['affiliate_aov']
    comm = params['affiliate_comm']
    low = clicks[0] * (conv[0]/100.0) * aov[0] * comm[0]
    mid = clicks[1] * (conv[1]/100.0) * aov[1] * comm[1]
    high= clicks[2] * (conv[2]/100.0) * aov[2] * comm[2]
    return {'low': round(low,2), 'mid': round(mid,2), 'high': round(high,2)}

def merch_estimate(videos: List[dict], params=DEFAULTS) -> Dict[str, Any]:
    total_views = _sum_views(videos)
    # engaged viewers: likes+comments+shares / views proxy
    likes = sum(int(v.get('likes') or 0) for v in videos)
    comments = sum(int(v.get('comments') or 0) for v in videos)
    shares = sum(int(v.get('shares') or 0) for v in videos)
    engaged = max(0, likes + comments + shares)
    conv = params['merch_conv']
    aov = params['merch_aov']
    margin = params['merch_margin']
    low = engaged * (conv[0]/100.0) * aov[0] * margin[0]
    mid = engaged * (conv[1]/100.0) * aov[1] * margin[1]
    high= engaged * (conv[2]/100.0) * aov[2] * margin[2]
    return {'low': round(low,2), 'mid': round(mid,2), 'high': round(high,2)}

def run(username: str, profile_file: Optional[str]=None, videos_file: Optional[str]=None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    params = params or DEFAULTS
    videos = load_videos_any(videos_file) if videos_file else []
    # Base outputs
    out = {
        'username': username,
        'assumptions': params,
        'models': {
            'brand_deals': brand_deal_estimate(videos, params),
            'creator_fund': creator_fund_estimate(videos, params),
            'affiliate': affiliate_estimate(videos, params),
            'merch': merch_estimate(videos, params),
        }
    }
    return out

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--username', required=True)
    ap.add_argument('--videos-file', default=None)
    ap.add_argument('--params', default=None, help='JSON file to override defaults')
    args = ap.parse_args()
    p = None
    if args.params:
        try:
            p = json.loads(Path(args.params).read_text())
        except Exception:
            p = None
    print(json.dumps(run(args.username, videos_file=args.videos_file, params=p), indent=2))
