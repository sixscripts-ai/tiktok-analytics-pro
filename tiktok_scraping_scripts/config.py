from __future__ import annotations
from typing import List, Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    proxy_list: List[str] = Field(default_factory=list, env="PROXY_LIST")
    postgres_url: Optional[str] = Field(default=None, env="POSTGRES_URL")
    mongo_url: Optional[str] = Field(default=None, env="MONGO_URL")
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    captcha_api_key: Optional[str] = Field(default=None, env="CAPTCHA_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
