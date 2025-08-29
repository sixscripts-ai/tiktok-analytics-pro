from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class CachedData(Base):
    __tablename__ = "cached_data"

    id = Column(Integer, primary_key=True)
    username = Column(String, index=True, nullable=False)
    data_type = Column(String, index=True, nullable=False)
    data = Column(Text, nullable=False)
    updated_at = Column(DateTime, index=True, nullable=False, default=datetime.utcnow)


@dataclass
class CachedItem:
    data: Any
    updated_at: datetime


class Storage:
    """SQLite-backed storage for cached TikTok data."""

    def __init__(self, db_path: str = "scraped_data.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _get(self, username: str, data_type: str) -> Optional[CachedItem]:
        with self.Session() as session:
            item = (
                session.query(CachedData)
                .filter_by(username=username, data_type=data_type)
                .first()
            )
            if item:
                import json

                return CachedItem(json.loads(item.data), item.updated_at)
            return None

    def _set(self, username: str, data_type: str, data: Any) -> None:
        with self.Session() as session:
            import json

            json_data = json.dumps(data, default=str)
            item = (
                session.query(CachedData)
                .filter_by(username=username, data_type=data_type)
                .first()
            )
            now = datetime.utcnow()
            if item:
                item.data = json_data
                item.updated_at = now
            else:
                item = CachedData(
                    username=username,
                    data_type=data_type,
                    data=json_data,
                    updated_at=now,
                )
                session.add(item)
            session.commit()

    def get_profile(self, username: str) -> Optional[CachedItem]:
        return self._get(username, "profile")

    def set_profile(self, username: str, data: Dict[str, Any]) -> None:
        self._set(username, "profile", data)

    def get_videos(self, username: str) -> Optional[CachedItem]:
        return self._get(username, "videos")

    def set_videos(self, username: str, data: List[Dict[str, Any]]) -> None:
        self._set(username, "videos", data)

    def delete(self, username: str, data_type: str) -> None:
        with self.Session() as session:
            session.query(CachedData).filter_by(
                username=username, data_type=data_type
            ).delete()
            session.commit()
