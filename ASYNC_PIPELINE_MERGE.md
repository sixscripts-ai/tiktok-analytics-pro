# Async Pipeline Integration

This document describes the resolution of conflicts between the `codex/build-async-pipeline-for-tiktok-scraping` branch and `main`, and how to use the merged functionality.

## Changes Made

### 1. Added Async Pipeline Components
- **`async_pipeline.py`**: Core async pipeline with `AsyncPipeline` and `TaskQueue` classes
- **`benchmarks/`**: Directory with performance benchmarks for async vs sync operations
- **Enhanced requirements**: Added `aiohttp>=3.8.0` dependency

### 2. Enhanced TikTokPipeline Orchestrator
The main `TikTokPipeline` class now supports both sync and async operations:

```python
# Sync usage (default)
pipeline = TikTokPipeline()
result = pipeline.scrape_profile("username")

# Async usage
pipeline = TikTokPipeline(enable_async=True)
result = await pipeline.scrape_profile_async("username")
```

### 3. Updated CLI Interface
The CLI now supports both unified and granular analytics commands:

```bash
# Unified analytics via pipeline (default)
python tiktok_cli.py analyze --username example_user

# Individual analytics commands (from async branch)
python tiktok_cli.py analyze posting_time_optimizer --username example_user
python tiktok_cli.py analyze hashtag_efficacy --username example_user
python tiktok_cli.py analyze sound_lifespan --username example_user

# Enable async processing
python tiktok_cli.py --async analyze --username example_user
```

## Conflicts Resolved

### 1. CLI Structure
- **Conflict**: async branch had granular analytics subcommands vs main's unified pipeline approach
- **Resolution**: Merged both approaches - CLI supports both unified analytics and individual commands

### 2. Import Dependencies  
- **Conflict**: main branch added models.py imports that didn't exist in async branch
- **Resolution**: Removed conflicting imports from earnings_calculator.py, engagement_analyzer.py, and integration_api.py

### 3. File Structure
- **Conflict**: async branch had benchmarks/ directory, main had pipeline/ and additional structure
- **Resolution**: Preserved both structures - async benchmarks + main's pipeline architecture

## Usage Examples

### Running Benchmarks
```bash
cd tiktok_scraping_scripts/benchmarks
python async_pipeline_benchmark.py
```

### Using Async Pipeline Directly
```python
import asyncio
from async_pipeline import AsyncPipeline, TaskQueue

async def main():
    async with AsyncPipeline(concurrency=5) as pipeline:
        result = await pipeline.fetch("https://example.com")
        print(result)

asyncio.run(main())
```

### Using Enhanced Orchestrator
```python
import asyncio
from pipeline.orchestrator import TikTokPipeline

# Sync usage
pipeline = TikTokPipeline()
profile = pipeline.scrape_profile("username")

# Async usage  
async def async_analysis():
    pipeline = TikTokPipeline(enable_async=True)
    result = await pipeline.run_comprehensive_async("username")
    return result

result = asyncio.run(async_analysis())
```

## Installation

To use async features, install additional dependencies:
```bash
pip install aiohttp>=3.8.0
```

## Backward Compatibility

All existing functionality remains unchanged. The async features are opt-in and don't affect existing code that doesn't explicitly enable them.