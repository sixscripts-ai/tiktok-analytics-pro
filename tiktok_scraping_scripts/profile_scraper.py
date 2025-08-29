
from __future__ import annotations
from typing import List, Optional, Dict, Any, Callable
import time, random, re, json

try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
except Exception:
    By = WebDriverWait = EC = TimeoutException = WebDriverException = None

# --- Helpers ---

_NUMBER_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([kmbKMB])?\s*$")
def parse_count(text: str|None) -> Optional[int]:
    if not text:
        return None
    t = text.strip().replace(',', '')
    m = _NUMBER_RE.match(t)
    if not m:
        try:
            return int(t)
        except Exception:
            return None
    val = float(m.group(1))
    suf = (m.group(2) or '').lower()
    if suf == 'k': val *= 1_000
    elif suf == 'm': val *= 1_000_000
    elif suf == 'b': val *= 1_000_000_000
    return int(val)

def _safe_text(el):
    try:
        return (el.text or '').strip()
    except Exception:
        return None

def _get_attr(el, name):
    try:
        return el.get_attribute(name)
    except Exception:
        return None

try:
    from .models import Profile
except ImportError:  # pragma: no cover
    from models import Profile

# --- Core ---

def _open_profile(driver, username: str):
    handle = username if username.startswith('@') else f'@{username}'
    url = f"https://www.tiktok.com/{handle}"
    driver.get(url)
    # human-like pause
    time.sleep(random.uniform(1.2, 2.2))
    return url

def _wait(driver, how, sel, timeout=12):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((how, sel)))

def _find(driver, how, sel):
    els = driver.find_elements(how, sel)
    return els[0] if els else None

def _try_many(driver, selectors, timeout=10):
    last=None
    for how, sel in selectors:
        try:
            el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((how, sel)))
            return el
        except Exception as e:
            last = e
    if last: raise last
    raise TimeoutException("element not found")  # type: ignore

def scrape_profile(username: str, driver=None, driver_factory: Optional[Callable[[], Any]] = None) -> Profile:
    if driver is None and driver_factory is None:
        try:
            import undetected_chromedriver as uc
            driver = uc.Chrome(options=uc.ChromeOptions())
        except Exception as e:
            raise RuntimeError("No driver available; pass a Selenium driver or driver_factory.") from e
    elif driver is None:
        driver = driver_factory()

    url = _open_profile(driver, username)

    # Display name / username
    display_name = None
    uname = None
    try:
        # data-e2e='user-title' contains both
        title_el = _try_many(driver, [
            (By.CSS_SELECTOR, "h1[data-e2e='user-title']"),
            (By.CSS_SELECTOR, "h1.tiktok-.*")  # fallback; regex won't work directly but left for visual
        ], timeout=10)
        if title_el:
            display_name = _safe_text(title_el)
        # username often nearby
        uname_el = _find(driver, By.CSS_SELECTOR, "h2[data-e2e='user-subtitle']") or _find(driver, By.CSS_SELECTOR, "a[href*='@']")
        uname = _safe_text(uname_el) or username
    except Exception:
        uname = username

    # Bio
    bio = None
    try:
        bio_el = _find(driver, By.CSS_SELECTOR, "h2[data-e2e='user-bio']") or _find(driver, By.CSS_SELECTOR, "p[data-e2e='user-bio']")
        bio = _safe_text(bio_el)
    except Exception:
        pass

    # Stats (following, followers, likes)
    following = followers = likes = None
    try:
        stat_els = driver.find_elements(By.CSS_SELECTOR, "strong[data-e2e='followers-count'], strong[data-e2e='following-count'], strong[data-e2e='likes-count']")
        # If not present, try generic strongs under stats container
        if not stat_els:
            stat_els = driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='user-stats'] strong")
        # Extract by nearby labels
        for el in stat_els:
            label_el = el.find_element(By.XPATH, "../span") if el else None
            label = _safe_text(label_el) or ''
            val = parse_count(_safe_text(el))
            if 'Following' in label or 'following' in label:
                following = val
            elif 'Followers' in label or 'followers' in label:
                followers = val
            elif 'Likes' in label or 'likes' in label:
                likes = val
    except Exception:
        pass

    # Verified badge
    verified = None
    try:
        vb = _find(driver, By.CSS_SELECTOR, "span[data-e2e='verified-badge']") or _find(driver, By.CSS_SELECTOR, "svg[aria-label*='Verified']")
        verified = bool(vb)
    except Exception:
        verified = None

    # Video count: count grid tiles (lazy)
    video_count = None
    try:
        tiles = driver.find_elements(By.CSS_SELECTOR, "div[data-e2e='user-post-item']")
        if tiles:
            video_count = len(tiles)
    except Exception:
        pass

    prof = Profile(
        username=uname or username,
        display_name=display_name,
        bio=bio,
        follower_count=followers,
        following_count=following,
        total_likes=likes,
        video_count=video_count,
        verified=verified,
        profile_url=url,
        created_at=None,
    )
    return prof

def run(usernames: List[str], driver_factory: Optional[Callable[[], Any]] = None) -> List[Profile]:
    out: List[Profile] = []
    driver = None
    if driver_factory is None:
        try:
            import undetected_chromedriver as uc
            driver = uc.Chrome(options=uc.ChromeOptions())
        except Exception:
            driver = None
    else:
        driver = driver_factory()
    if driver is None:
        raise RuntimeError("No WebDriver available. Provide driver_factory() or ensure undetected_chromedriver is installed.")
    try:
        for u in usernames:
            out.append(scrape_profile(u, driver=driver))
            time.sleep(random.uniform(0.8, 1.5))
    finally:
        try:
            driver.quit()
        except Exception:
            pass
    return out

if __name__ == "__main__":
    import argparse, sys
    ap = argparse.ArgumentParser()
    ap.add_argument("usernames", nargs='+')
    args = ap.parse_args()
    res = run(args.usernames)
    print(json.dumps(res, indent=2, default=str))
