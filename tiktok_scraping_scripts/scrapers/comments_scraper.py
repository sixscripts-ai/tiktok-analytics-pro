
from __future__ import annotations
from typing import Any, Dict, List, Callable, Optional
import time, random, re
from dataclasses import dataclass

from scrapers.utils_loader import load_videos_any

try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
except Exception:
    By=WebDriverWait=EC=TimeoutException=WebDriverException=NoSuchElementException=None

@dataclass
class CommentResult:
    video_id: str
    comment_id: str
    author: str|None
    text: str|None
    likes: int|None
    ts: str|None
    parent_id: str|None = None

COMMENT_TILE_SELECTORS = [
    (By.CSS_SELECTOR, "div[data-e2e='comment-item']"),
    (By.CSS_SELECTOR, "div.tiktok-1i2okah-DivCommentItemContainer"),
]

OPEN_COMMENTS_BUTTON = [
    (By.CSS_SELECTOR, "[data-e2e='browse-comment']"),
    (By.CSS_SELECTOR, "button[aria-label*='comment']"),
]

SCROLLABLE_PANEL = [
    (By.CSS_SELECTOR, "div[data-e2e='comment-list']"),
    (By.CSS_SELECTOR, "div.tiktok-1qyrx0f-DivCommentList"),
]

def _find_any(driver, selectors, timeout=10):
    last_err=None
    for how, sel in selectors:
        try:
            el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((how, sel)))
            return el
        except Exception as e:
            last_err=e
            continue
    if last_err:
        raise last_err
    raise TimeoutException("element not found")

def _all_now(driver, selectors):
    for how, sel in selectors:
        els = driver.find_elements(how, sel)
        if els:
            return els
    return []

def _int(s: str|None) -> Optional[int]:
    if not s: return None
    s=s.strip().lower().replace(',', '')
    m = re.match(r'([0-9]+(\.[0-9]+)?)\s*([kmb])?$', s)
    if not m:
        try:
            return int(s)
        except Exception:
            return None
    val=float(m.group(1))
    suf=m.group(3)
    if suf=='k': val*=1_000
    elif suf=='m': val*=1_000_000
    elif suf=='b': val*=1_000_000_000
    return int(val)

def _extract_comment_fields(tile):
    try:
        cid = tile.get_attribute("data-comment-id") or ""
    except Exception:
        cid=""
    try:
        author = None
        for how, sel in [(By.CSS_SELECTOR, "[data-e2e='comment-level1-username']"),
                         (By.CSS_SELECTOR, "a[href*='@']")]:
            els = tile.find_elements(how, sel)
            if els:
                author = els[0].text.strip() or els[0].get_attribute("href") or None
                break
    except Exception:
        author=None
    try:
        text_el = None
        for how, sel in [(By.CSS_SELECTOR, "[data-e2e='comment-text']"),
                         (By.CSS_SELECTOR, "p")]:
            els = tile.find_elements(how, sel)
            if els:
                text_el = els[0]
                break
        text = text_el.text.strip() if text_el else None
    except Exception:
        text=None
    try:
        like_el = None
        for how, sel in [(By.CSS_SELECTOR, "[data-e2e='comment-like-count']"),
                         (By.CSS_SELECTOR, "span[title*='like']")]:
            els = tile.find_elements(how, sel)
            if els:
                like_el = els[0]
                break
        likes = _int(like_el.text) if like_el else None
    except Exception:
        likes=None
    ts=None
    try:
        for how, sel in [(By.CSS_SELECTOR, "abbr[title], time[title]"),
                         (By.CSS_SELECTOR, "span time"), (By.CSS_SELECTOR, "time")]:
            els = tile.find_elements(how, sel)
            if els:
                ts = els[0].get_attribute("title") or els[0].get_attribute("datetime") or els[0].text
                if ts: break
    except Exception:
        ts=None
    return cid or "", author, text, likes, ts

def scrape_comments(
    username: str,
    video_urls: Optional[List[str]] = None,
    videos_file: Optional[str] = None,
    limit_per_video: int = 100,
    driver=None,
    driver_factory: Optional[Callable[[], Any]] = None,
    per_video_timeout: int = 30,
    max_retries: int = 3,
) -> Dict[str, Any]:

    if driver is None and driver_factory is None:
        try:
            import undetected_chromedriver as uc
            driver = uc.Chrome(options=uc.ChromeOptions())
        except Exception as e:
            raise RuntimeError("No driver provided and cannot create a local driver. Pass a Selenium WebDriver or a driver_factory.") from e
    elif driver is None:
        driver = driver_factory()

    if not video_urls and videos_file:
        vids = load_videos_any(videos_file)
        video_urls = [v.get('url') or v.get('video_url') for v in vids if v.get('url') or v.get('video_url')]
    video_urls = video_urls or []

    out: List[Dict[str, Any]] = []
    for url in video_urls:
        if not url: 
            continue
        attempt=0
        while attempt < max_retries:
            attempt += 1
            try:
                driver.get(url)
                time.sleep(random.uniform(1.0, 2.2))
                try:
                    btn = _find_any(driver, OPEN_COMMENTS_BUTTON, timeout=10)
                    try:
                        driver.execute_script("arguments[0].click();", btn)
                    except Exception:
                        btn.click()
                except Exception:
                    pass

                panel = _find_any(driver, SCROLLABLE_PANEL, timeout=per_video_timeout//2)
                seen_ids=set()
                last_added=0
                st=time.time()
                from selenium.common.exceptions import TimeoutException, WebDriverException
                while len(seen_ids) < limit_per_video and (time.time()-st) < per_video_timeout:
                    tiles = _all_now(driver, COMMENT_TILE_SELECTORS)
                    for t in tiles:
                        cid, author, text, likes, ts = _extract_comment_fields(t)
                        if not cid or cid in seen_ids:
                            continue
                        seen_ids.add(cid)
                        out.append({
                            "video_id": url,
                            "comment_id": cid,
                            "author": author,
                            "text": text,
                            "likes": likes,
                            "ts": ts,
                        })
                        last_added = time.time()
                        if len(seen_ids) >= limit_per_video:
                            break
                    try:
                        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;", panel)
                    except Exception:
                        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
                    time.sleep(random.uniform(0.6, 1.2))
                    if (time.time()-last_added) > 4:
                        try:
                            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 200;", panel)
                        except Exception:
                            pass
                break
            except Exception:
                if attempt >= max_retries:
                    break
                time.sleep(1.5 * attempt + random.uniform(0.2, 0.8))
                continue
            finally:
                time.sleep(random.uniform(0.5, 1.0))
    return {"username": username, "comments": out, "count": len(out)}
