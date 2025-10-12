from __future__ import annotations
import asyncio
from typing import Any, Awaitable, Callable, List, Optional

import aiohttp


class AsyncPipeline:
    """Simple aiohttp-based fetch pipeline."""

    def __init__(self, concurrency: int = 5, headers: Optional[dict[str, str]] = None):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        }
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "AsyncPipeline":
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session:
            await self.session.close()
        self.session = None

    async def fetch(self, url: str) -> str:
        if not self.session:
            raise RuntimeError("AsyncPipeline session not started")
        async with self.semaphore:
            async with self.session.get(url) as resp:
                resp.raise_for_status()
                return await resp.text()


class TaskQueue:
    """Lightweight async task queue for concurrent scraping."""

    def __init__(self, workers: int = 5):
        self.queue: asyncio.Queue[Callable[[], Awaitable[Any]]] = asyncio.Queue()
        self.results: List[Any] = []
        self.workers = workers

    async def add_task(self, coro: Callable[[], Awaitable[Any]]) -> None:
        await self.queue.put(coro)

    async def _worker(self) -> None:
        while True:
            job = await self.queue.get()
            if job is None:
                self.queue.task_done()
                break
            try:
                res = await job()
                self.results.append(res)
            finally:
                self.queue.task_done()

    async def run(self) -> List[Any]:
        workers = [asyncio.create_task(self._worker()) for _ in range(self.workers)]
        for _ in range(self.workers):
            await self.queue.put(None)
        await self.queue.join()
        for w in workers:
            await w
        return self.results