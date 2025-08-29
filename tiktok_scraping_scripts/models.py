from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel

class Music(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None

class Video(BaseModel):
    url: str
    video_id: Optional[str] = None
    create_time: Optional[str] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    duration: Optional[float] = None
    hashtags: Optional[List[str]] = None
    music: Optional[Music] = None
    caption: Optional[str] = None

class Profile(BaseModel):
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    total_likes: Optional[int] = None
    video_count: Optional[int] = None
    verified: Optional[bool] = None
    profile_url: Optional[str] = None
    created_at: Optional[str] = None
