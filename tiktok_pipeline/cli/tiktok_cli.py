
import argparse, json

from tiktok_pipeline.cli.driver_loader import discover_driver_factory
from tiktok_pipeline.scrapers.comments_scraper import scrape_comments
from tiktok_pipeline.analytics.posting_time_optimizer import posting_time_optimizer
from tiktok_pipeline.analytics.hashtag_efficacy import hashtag_efficacy
from tiktok_pipeline.analytics.sound_lifespan import sound_lifespan

def _print(obj):
    print(json.dumps(obj, indent=2, default=str))

def main(argv=None):
    p = argparse.ArgumentParser(prog="tiktokctl")
    sub = p.add_subparsers(dest="cmd")

    # --- SCRAPE ---
    ps = sub.add_parser("scrape", help="Scrape data from TikTok")
    ps_sub = ps.add_subparsers(dest="kind")

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

    args = p.parse_args(argv)

    # ----- SCRAPE HANDLERS -----
    if args.cmd == "scrape":
        if args.kind == "comments":
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
            return _print(posting_time_optimizer(
                args.username,
                tz=args.tz,
                window_days=args.window,
                videos_file=args.videos_file,
            ))

        if args.kind == "hashtag_efficacy":
            return _print(hashtag_efficacy(
                args.username,
                min_uses=args.min_uses,
                videos_file=args.videos_file,
            ))

        if args.kind == "sound_lifespan":
            return _print(sound_lifespan(
                args.sound_id,
                args.username,
                videos_file=args.videos_file,
            ))

    p.print_help()

if __name__ == "__main__":
    main()
