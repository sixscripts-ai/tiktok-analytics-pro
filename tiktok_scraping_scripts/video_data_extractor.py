
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Callable
import time, random, json

from scrapers.utils_loader import load_videos_any
from driver_loader import discover_driver_factory
from config import settings

try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
except Exception:
    By = WebDriverWait = EC = TimeoutException = WebDriverException = None

@dataclass
class VideoRow:
    url: str
    video_id: str|None = None
    create_time: str|None = None
    views: int|None = None
    likes: int|None = None
    comments: int|None = None
    shares: int|None = None
    duration: float|None = None
    hashtags: List[str]|None = None
    music: Dict[str, Any]|None = None
    caption: str|None = None

def _parse_overlay_count(text: str|None) -> Optional[int]:
    if not text: return None
    t = (text or '').strip().lower().replace(',', '')
    mult = 1
    if t.endswith('k'): mult = 1_000; t = t[:-1]
    elif t.endswith('m'): mult = 1_000_000; t = t[:-1]
    elif t.endswith('b'): mult = 1_000_000_000; t = t[:-1]
    try:
        return int(float(t) * mult)
    except Exception:
        return None

def _open_profile(driver, username: str):
    handle = username if username.startswith('@') else f'@{username}'
    url = f"https://www.tiktok.com/{handle}"
    driver.get(url)
    time.sleep(random.uniform(1.2, 2.0))
    return url

def _scroll_grid(driver, max_items: int = 100, max_secs: int = 25):
    start = time.time()
    last_h = 0
    while True:
        tiles = driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='user-post-item'] a[href*='/video/']")
        if len(tiles) >= max_items:
            break
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(random.uniform(0.6, 1.0))
        if time.time()-start > max_secs:
            break
        h = driver.execute_script("return document.body.scrollHeight")
        if h == last_h:
            break
        last_h = h

def _collect_from_grid(driver, limit: int = 200) -> List[VideoRow]:
    out: List[VideoRow] = []
    
    # Try multiple selectors for video links
    selectors = [
        "div[data-e2e='user-post-item'] a[href*='/video/']",
        "div[data-e2e='user-post-item-list'] a[href*='/video/']",
        "a[href*='/video/']",
        "div[data-e2e='user-post-item'] a",
        "div[data-e2e='user-post-item-list'] a"
    ]
    
    anchors = []
    for selector in selectors:
        try:
            anchors = driver.find_elements(By.CSS_SELECTOR, selector)
            if anchors:
                break
        except Exception:
            continue
    
    if not anchors:
        return out
    
    for a in anchors[:limit]:
        try:
            href = a.get_attribute("href")
            if not href or '/video/' not in href:
                continue
                
            # Try multiple selectors for view count
            view_selectors = [
                "strong",
                "span[data-e2e='video-views']",
                "span[data-e2e='browse-video-meta-like']",
                "div[data-e2e='video-views']",
                "div[data-e2e='browse-video-meta-like']"
            ]
            
            overlay = None
            for view_selector in view_selectors:
                try:
                    overlay_el = a.find_element(By.CSS_SELECTOR, view_selector)
                    overlay = overlay_el.text.strip()
                    if overlay:
                        break
                except Exception:
                    continue
            
            views = _parse_overlay_count(overlay)
            out.append(VideoRow(url=href, views=views))
            
        except Exception as e:
            print(f"Error processing video link: {e}")
            continue
    
    return out

def _hydrate_video_meta(driver, row: VideoRow, per_video_timeout: int = 15) -> VideoRow:
    if not row.url:
        return row
    driver.get(row.url)
    try:
        WebDriverWait(driver, per_video_timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, "video, div[data-e2e='browse-video']")))
    except Exception:
        pass
    time.sleep(random.uniform(0.8, 1.2))
    # video id from URL
    vid_id = None
    try:
        # .../video/1234567890123456789
        parts = row.url.split('/video/')
        if len(parts) > 1:
            vid_id = parts[1].split('?')[0].split('/')[0]
    except Exception:
        pass
    row.video_id = row.video_id or vid_id

    # caption text
    try:
        cap_el = driver.find_element(By.CSS_SELECTOR, "div[data-e2e='browse-video-desc']") or driver.find_element(By.CSS_SELECTOR, "h1[data-e2e='video-desc']")
        row.caption = cap_el.text.strip()
    except Exception:
        pass

    # counts - improved with multiple selectors
    try:
        def to_int(s):
            if not s: return None
            s = s.strip().lower().replace(',', '')
            mult = 1
            if s.endswith('k'): mult = 1_000; s=s[:-1]
            elif s.endswith('m'): mult = 1_000_000; s=s[:-1]
            elif s.endswith('b'): mult = 1_000_000_000; s=s[:-1]
            try:
                return int(float(s)*mult)
            except Exception:
                return None

        # Multiple selectors for each metric
        like_selectors = [
            "button[aria-label*='like']",
            "button[data-e2e='like-icon']",
            "span[data-e2e='like-count']",
            "div[data-e2e='like-count']",
            "button[aria-label*='Like']"
        ]
        
        comment_selectors = [
            "button[aria-label*='comment']",
            "button[data-e2e='comment-icon']",
            "span[data-e2e='comment-count']",
            "div[data-e2e='comment-count']",
            "button[aria-label*='Comment']"
        ]
        
        share_selectors = [
            "button[aria-label*='share']",
            "button[data-e2e='share-icon']",
            "span[data-e2e='share-count']",
            "div[data-e2e='share-count']",
            "button[aria-label*='Share']"
        ]
        
        # Try to get likes
        for selector in like_selectors:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, selector)
                val = to_int(btn.text or btn.get_attribute('aria-label') or btn.get_attribute('title'))
                if val:
                    row.likes = val
                    break
            except Exception:
                continue
        
        # Try to get comments
        for selector in comment_selectors:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, selector)
                val = to_int(btn.text or btn.get_attribute('aria-label') or btn.get_attribute('title'))
                if val:
                    row.comments = val
                    break
            except Exception:
                continue
        
        # Try to get shares
        for selector in share_selectors:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, selector)
                val = to_int(btn.text or btn.get_attribute('aria-label') or btn.get_attribute('title'))
                if val:
                    row.shares = val
                    break
            except Exception:
                continue
                
    except Exception:
        pass

    # duration (if present)
    try:
        dur = driver.find_element(By.CSS_SELECTOR, "span[data-e2e='video-duration']")
        # usually mm:ss
        txt = dur.text.strip()
        if ':' in txt:
            mm, ss = txt.split(':')[-2:]
            row.duration = int(mm)*60 + int(ss)
    except Exception:
        pass

    # hashtags + music
    try:
        tags = []
        tag_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/tag/']")
        for t in tag_links:
            txt = (t.text or '').strip()
            if txt:
                if not txt.startswith('#'):
                    txt = '#' + txt
                tags.append(txt.lower())
        row.hashtags = tags or row.hashtags
    except Exception:
        pass

    try:
        m = {}
        music_link = driver.find_element(By.CSS_SELECTOR, "a[href*='/music/']")
        m['title'] = (music_link.text or '').strip()
        href = music_link.get_attribute('href') or ''
        # /music/some-name-1234567890123456789
        if href:
            sid = href.rstrip('/').split('-')[-1]
            m['id'] = sid if sid.isdigit() else None
        row.music = m
    except Exception:
        pass

    return row

def run(username: str, limit: int = 200, incremental: bool = True, include_comments: bool = False,
        driver=None, driver_factory: Optional[Callable[[], Any]] = None, out: Optional[str]=None) -> List[Dict[str, Any]]:
    driver_factory = driver_factory or discover_driver_factory()
    if driver is None:
        driver = driver_factory()

    try:
        _open_profile(driver, username)
        _scroll_grid(driver, max_items=limit, max_secs=30)
        rows = _collect_from_grid(driver, limit=limit)
        results: List[Dict[str, Any]] = []
        
        # Only hydrate if we found videos
        if rows:
            for r in rows:
                try:
                    hydrated = _hydrate_video_meta(driver, r)
                    results.append(asdict(hydrated))
                    time.sleep(random.uniform(0.5, 1.0))
                except Exception:
                    # Add basic video data even if hydration fails
                    results.append(asdict(r))
        else:
            pass
            
    except Exception as e:
        results = []
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    if include_comments:
        # optional: enrich with comments using our comments scraper
        try:
            from tiktok_scraping_scripts.scrapers.comments_scraper import scrape_comments
            comm = scrape_comments(username, video_urls=[r['url'] for r in results], limit_per_video=100, driver_factory=driver_factory)
            # attach comment counts if missing
            by_vid = {}
            for c in comm.get('comments', []):
                by_vid.setdefault(c['video_id'], 0)
                by_vid[c['video_id']] += 1
            for r in results:
                if r.get('comments') is None and r.get('url') in by_vid:
                    r['comments'] = by_vid[r['url']]
        except Exception:
            pass

    if out:
        p = Path(out)
        if p.suffix.lower() == '.jsonl':
            with p.open('w', encoding='utf-8') as f:
                for row in results:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
        else:
            p.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    return results

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--username', required=True)
    ap.add_argument('--limit', type=int, default=200)
    ap.add_argument('--include-comments', action='store_true')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    res = run(args.username, limit=args.limit, include_comments=args.include_comments, out=args.out)
    print(json.dumps(res[:3], indent=2, ensure_ascii=False))
