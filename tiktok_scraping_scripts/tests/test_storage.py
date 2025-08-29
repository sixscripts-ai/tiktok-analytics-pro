from __future__ import annotations

from pathlib import Path

from tiktok_scraping_scripts.data.storage import Storage


def test_profile_crud(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    storage = Storage(str(db_path))

    username = "alice"
    data1 = {"profile": {"follower_count": 1}}
    storage.set_profile(username, data1)

    cached = storage.get_profile(username)
    assert cached is not None
    assert cached.data == data1

    data2 = {"profile": {"follower_count": 2}}
    storage.set_profile(username, data2)

    cached2 = storage.get_profile(username)
    assert cached2 is not None
    assert cached2.data == data2
    assert cached2.updated_at >= cached.updated_at


def test_video_crud(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    storage = Storage(str(db_path))

    username = "bob"
    videos1 = [{"id": 1}, {"id": 2}]
    storage.set_videos(username, videos1)

    cached = storage.get_videos(username)
    assert cached is not None
    assert cached.data == videos1

    videos2 = [{"id": 3}]
    storage.set_videos(username, videos2)

    cached2 = storage.get_videos(username)
    assert cached2 is not None
    assert cached2.data == videos2
    assert cached2.updated_at >= cached.updated_at
