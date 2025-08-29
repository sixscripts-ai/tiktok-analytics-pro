from __future__ import annotations
from datetime import datetime, timedelta
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tiktok_scraping_scripts'))
from analytics import hashtag_efficacy, posting_time_optimizer, sound_lifespan


def test_hashtag_efficacy(monkeypatch) -> None:
    videos = [
        {'hashtags': ['test', '#Other'], 'views': 100, 'likes': 10, 'comments': 5, 'shares': 5},
        {'hashtags': ['test'], 'views': 200, 'likes': 40, 'comments': 10, 'shares': 10},
        {'hashtags': ['other'], 'views': 100, 'likes': 10, 'comments': 0, 'shares': 0},
    ]
    monkeypatch.setattr(
        'analytics.hashtag_efficacy.load_videos_any',
        lambda fp: videos,
    )
    result = hashtag_efficacy.hashtag_efficacy('user', min_uses=1, videos_file='x.json')
    assert result['scores'][0]['hashtag'] == 'test'
    assert result['hashtag_count'] == 2


def test_posting_time_optimizer(monkeypatch) -> None:
    base = datetime(2023, 1, 1, 10)
    videos = [
        {'create_time': base.timestamp(), 'views': 100, 'likes': 10, 'comments': 0, 'shares': 0},
        {'create_time': (base + timedelta(days=7)).timestamp(), 'views': 100, 'likes': 20, 'comments': 0, 'shares': 0},
        {'create_time': (base + timedelta(days=1, hours=1)).timestamp(), 'views': 100, 'likes': 30, 'comments': 0, 'shares': 0},
        {'create_time': (base + timedelta(days=8, hours=1)).timestamp(), 'views': 100, 'likes': 40, 'comments': 0, 'shares': 0},
    ]
    monkeypatch.setattr(
        'analytics.posting_time_optimizer.load_videos_any',
        lambda fp: videos,
    )
    result = posting_time_optimizer.posting_time_optimizer('user', videos_file='x.json')
    assert result['windows'][0]['day'] == 'Monday'
    assert result['best_days'][0]['day'] == 'Monday'
    assert result['best_hours'][0]['hour'] == 11


def test_sound_lifespan(monkeypatch) -> None:
    now = datetime.now()
    videos = [
        {'music': {'id': '1', 'title': 'Song1'}, 'views': 100, 'likes': 10, 'comments': 0, 'shares': 0, 'create_time': (now - timedelta(days=5)).timestamp()},
        {'music': {'id': '1', 'title': 'Song1'}, 'views': 200, 'likes': 20, 'comments': 0, 'shares': 0, 'create_time': (now - timedelta(days=1)).timestamp()},
        {'music': {'id': '2', 'title': 'Song2'}, 'views': 150, 'likes': 15, 'comments': 0, 'shares': 0, 'create_time': (now - timedelta(days=10)).timestamp()},
    ]
    monkeypatch.setattr(
        'analytics.sound_lifespan.load_videos_any',
        lambda fp: videos,
    )
    result = sound_lifespan.sound_lifespan(sound_id='1', username='u', videos_file='x.json')
    assert result['sound_analysis']['total_uses'] == 2
    assert result['sound_count'] == 1
