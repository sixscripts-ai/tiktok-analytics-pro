
from __future__ import annotations
from typing import Optional, Dict, Any

from tiktok_scraping_scripts.network.session_manager import (
    get_random_user_agent,
    get_proxy,
)

# Note: undetected_chromedriver is optional at import-time; used at runtime

def _apply_proxy(chrome_options, proxy: Optional[str] = None):
    proxy = proxy or get_proxy()
    if not proxy:
        return
    chrome_options.add_argument(f"--proxy-server={proxy}")

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

    ua = user_agent or get_random_user_agent()
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
