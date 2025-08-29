import sys, argparse, json
from pathlib import Path

# Add both the repo root and package root to sys.path for safer imports
base_dir = Path(__file__).resolve().parents[1]
pkg_dir = Path(__file__).resolve().parent
for path in (base_dir, pkg_dir):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# {{ import pipeline orchestrator }}
from pipeline.orchestrator import TikTokPipeline
# }}

def _print(obj):
    print(json.dumps(obj, indent=2, default=str))

def main(argv=None):
    p = argparse.ArgumentParser(prog="tiktokctl")
    sub = p.add_subparsers(dest="cmd")

    # --- SCRAPE ---
    ps = sub.add_parser("scrape", help="Scrape data from TikTok")
    ps_sub = ps.add_subparsers(dest="kind")

    # {{ profile scraping }}
    sp_profile = ps_sub.add_parser("profile", help="Fetch profile information")
    sp_profile.add_argument("--username", required=True)
    sp_profile.add_argument("--no-driver", action="store_true", help="Run without creating a Selenium driver (dev only)")
    # }}

    # {{ video scraping }}
    sp_videos = ps_sub.add_parser("videos", help="Fetch user videos")
    sp_videos.add_argument("--username", required=True)
    sp_videos.add_argument("--limit", type=int, default=200)
    sp_videos.add_argument("--include-comments", action="store_true")
    sp_videos.add_argument("--no-driver", action="store_true", help="Run without creating a Selenium driver (dev only)")
    # }}

    sp_comments = ps_sub.add_parser("comments", help="Scroll + parse comments via Selenium")
    sp_comments.add_argument("--username", required=True)
    sp_comments.add_argument("--videos-file", default=None, help="JSON or JSONL with videos (must contain 'url' or 'video_url')")
    sp_comments.add_argument("--limit-per-video", type=int, default=100)
    sp_comments.add_argument("--per-video-timeout", type=int, default=30)
    sp_comments.add_argument("--max-retries", type=int, default=3)
    sp_comments.add_argument("--no-driver", action="store_true", help="Run without creating a Selenium driver (dev only)")

    # --- ANALYZE ---
    an = sub.add_parser("analyze", help="Run analytics over scraped data")
    # {{ analyze args }}
    an.add_argument("--username", required=True)
    an.add_argument("--videos-file", default=None)
    an.add_argument("--tz", default="UTC")
    an.add_argument("--window", type=int, default=60)
    # }}

    # {{ persist command }}
    pe = sub.add_parser("persist", help="Persist video data to file")
    pe.add_argument("--input", required=True, help="Path to JSON or JSONL with videos")
    pe.add_argument("--output", required=True, help="Destination file path")
    pe.add_argument("--format", default=None, help="Output format (json|jsonl|csv|xlsx|pdf)")
    # }}

    args = p.parse_args(argv)

    # ----- SCRAPE HANDLERS -----
    if args.cmd == "scrape":
        if args.kind in ("profile", "videos"):
            try:
                from tiktok_scraping_scripts.cli.driver_loader import discover_driver_factory
            except Exception:
                try:
                    from cli.driver_loader import discover_driver_factory
                except Exception:
                    from driver_loader import discover_driver_factory
            driver_factory = None if args.no_driver else discover_driver_factory()
            pipeline = TikTokPipeline(driver_factory=driver_factory)
            if args.kind == "profile":
                return _print(pipeline.scrape_profile(args.username))
            if args.kind == "videos":
                return _print(pipeline.scrape_videos(args.username, limit=args.limit, include_comments=args.include_comments))
        if args.kind == "comments":
            try:
                from tiktok_scraping_scripts.cli.driver_loader import discover_driver_factory
            except Exception:
                try:
                    from cli.driver_loader import discover_driver_factory
                except Exception:
                    from driver_loader import discover_driver_factory
            try:
                from tiktok_scraping_scripts.scrapers.comments_scraper import scrape_comments
            except Exception:
                from scrapers.comments_scraper import scrape_comments
            driver_factory = None if args.no_driver else discover_driver_factory()
            return _print(scrape_comments(
                username=args.username,
                videos_file=args.videos_file,
                limit_per_video=args.limit_per_video,
                driver_factory=driver_factory,
                per_video_timeout=args.per_video_timeout,
                max_retries=args.max_retries,
            ))

    # ----- ANALYZE HANDLERS -----
    if args.cmd == "analyze":
        pipeline = TikTokPipeline()
        return _print(pipeline.run_analytics(args.username, videos_file=args.videos_file, tz=args.tz, window_days=args.window))

    # ----- PERSIST HANDLER -----
    if args.cmd == "persist":
        from scrapers.utils_loader import load_videos_any
        pipeline = TikTokPipeline()
        pipeline.video_data = load_videos_any(args.input)
        pipeline.persist_results(args.output, fmt=args.format)
        return _print({"output": args.output})

    p.print_help()

if __name__ == "__main__":
    main()
