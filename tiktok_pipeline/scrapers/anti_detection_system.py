
from __future__ import annotations
from typing import Optional, Dict, Any
import random, json

# Note: undetected_chromedriver is optional at import-time; used at runtime
def _random_ua():
    uas = [
        # Sample modern desktop UAs (rotate/extend as you like)
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36",
    ]
    return random.choice(uas)

def _apply_proxy(chrome_options, proxy: Optional[str] = None):
    if not proxy:
        return
    # proxy string examples:
    #   host:port
    #   user:pass@host:port  (for authenticated proxies, you may need an extension or CDP auth workaround)
    chrome_options.add_argument(f"--proxy-server=http://{proxy}")

def _apply_stealth_prefs(chrome_options):
    # Minimize automation flags
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--lang=en-US,en" )

def _post_launch_stealth(driver):
    # CDP / JS hooks to reduce detectable automation
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        })
    except Exception:
        pass
    try:
        driver.execute_script("""
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
        """)
    except Exception:
        pass

def create_driver(geo: str='US', headless: bool=True, proxy: Optional[str]=None, user_agent: Optional[str]=None, fingerprint: bool=True):
    """Return a hardened undetected-chromedriver instance.
    Args:
        geo: Region label for your own routing logic.
        headless: Run headless.
        proxy: Optional proxy string.
        user_agent: Optional UA override; if None, a random modern UA is used.
        fingerprint: Apply stealth flags and JS hooks.
    """
    try:
        import undetected_chromedriver as uc
    except Exception as e:
        raise RuntimeError("undetected_chromedriver not installed; cannot create driver") from e

    ua = user_agent or _random_ua()
    opts = uc.ChromeOptions()
    _apply_stealth_prefs(opts)
    opts.add_argument(f"--user-agent={ua}")
    if headless:
        opts.add_argument("--headless=new")
    _apply_proxy(opts, proxy)

    driver = uc.Chrome(options=opts)
    if fingerprint:
        _post_launch_stealth(driver)
    return driver
