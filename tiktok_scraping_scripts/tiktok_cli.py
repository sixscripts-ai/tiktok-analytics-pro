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
    p.add_argument("--async", action="store_true", help="Enable async pipeline for faster processing")
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
    an_sub = an.add_subparsers(dest="kind")
    
    # {{ comprehensive analytics via pipeline }}
    an.add_argument("--username", required=True)
    an.add_argument("--videos-file", default=None)
    an.add_argument("--tz", default="UTC")
    an.add_argument("--window", type=int, default=60)
    # }}

    # {{ individual analytics commands from async pipeline branch }}
    sp_pto = an_sub.add_parser("posting_time_optimizer", help="Compute best posting time windows from videos")
    sp_pto.add_argument("--username", required=True)
    sp_pto.add_argument("--tz", default="UTC")
    sp_pto.add_argument("--window", type=int, default=60)
    sp_pto.add_argument("--videos-file", default=None)

    sp_hash = an_sub.add_parser("hashtag_efficacy", help="Compute hashtag lift vs baseline")
    sp_hash.add_argument("--username", required=True)
    sp_hash.add_argument("--min-uses", type=int, default=5)
    sp_hash.add_argument("--videos-file", default=None)

    sp_sound = an_sub.add_parser("sound_lifespan", help="Estimate sound half-life from usage")
    sp_sound.add_argument("--sound-id", default=None)
    sp_sound.add_argument("--username", default=None)
    sp_sound.add_argument("--videos-file", default=None)
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
            pipeline = TikTokPipeline(driver_factory=driver_factory, enable_async=getattr(args, 'async', False))
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
        if args.kind == "posting_time_optimizer":
            try:
                from tiktok_scraping_scripts.analytics.posting_time_optimizer import posting_time_optimizer
            except Exception:
                from analytics.posting_time_optimizer import posting_time_optimizer
            return _print(posting_time_optimizer(args.username, tz=args.tz, window_days=args.window, videos_file=args.videos_file))

        if args.kind == "hashtag_efficacy":
            try:
                from tiktok_scraping_scripts.analytics.hashtag_efficacy import hashtag_efficacy
            except Exception:
                from analytics.hashtag_efficacy import hashtag_efficacy
            return _print(hashtag_efficacy(args.username, min_uses=args.min_uses, videos_file=args.videos_file))

        if args.kind == "sound_lifespan":
            try:
                from tiktok_scraping_scripts.analytics.sound_lifespan import sound_lifespan
            except Exception:
                from analytics.sound_lifespan import sound_lifespan
            return _print(sound_lifespan(args.sound_id, args.username, videos_file=args.videos_file))

        # Default comprehensive analytics via pipeline
        pipeline = TikTokPipeline(enable_async=getattr(args, 'async', False))
        return _print(pipeline.run_analytics(args.username, videos_file=args.videos_file, tz=args.tz, window_days=args.window))

    # ----- PERSIST HANDLER -----
    if args.cmd == "persist":
        from scrapers.utils_loader import load_videos_any
        pipeline = TikTokPipeline(enable_async=getattr(args, 'async', False))
        pipeline.video_data = load_videos_any(args.input)
        pipeline.persist_results(args.output, fmt=args.format)
        return _print({"output": args.output})

    p.print_help()

if __name__ == "__main__":
    main()
