from __future__ import annotations
import asyncio
import time
import requests
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

sys.path.append(str(Path(__file__).resolve().parents[1]))
from async_pipeline import AsyncPipeline, TaskQueue

PORT = 8765
URLS = [f"http://localhost:{PORT}" for _ in range(20)]


def _start_server() -> HTTPServer:
    server = HTTPServer(("localhost", PORT), SimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def sync_fetch() -> float:
    start = time.time()
    for url in URLS:
        requests.get(url)
    return time.time() - start


async def async_fetch() -> float:
    start = time.time()
    async with AsyncPipeline(concurrency=5) as pipe:
        q = TaskQueue(workers=5)
        for url in URLS:
            await q.add_task(lambda url=url: pipe.fetch(url))
        await q.run()
    return time.time() - start


def main() -> None:
    server = _start_server()
    try:
        sync_time = sync_fetch()
        async_time = asyncio.run(async_fetch())
        print(f"sync_seconds={sync_time:.2f}")
        print(f"async_seconds={async_time:.2f}")
        if async_time:
            print(f"speedup={sync_time/async_time:.2f}x")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()