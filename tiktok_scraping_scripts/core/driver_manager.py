from __future__ import annotations

import os
import random
from typing import List, Optional


def _bool_env(value: Optional[bool], key: str, default: bool) -> bool:
    if value is not None:
        return value
    env = os.getenv(key)
    if env is None:
        return default
    return env.strip().lower() in {"1", "true", "yes", "on"}


def _choose_proxy(proxy: Optional[str], proxies: Optional[List[str]]) -> Optional[str]:
    if proxy:
        return proxy
    if proxies is None:
        raw = os.getenv("PROXY_LIST", "")
        proxies = [p.strip() for p in raw.split(",") if p.strip()]
    if proxies:
        return random.choice(proxies)
    return None


def get_driver(
    *,
    headless: bool | None = None,
    timeout: int | None = None,
    proxy: Optional[str] = None,
    proxies: Optional[List[str]] = None,
    use_stealth: bool | None = None,
):
    headless = _bool_env(headless, "SELENIUM_HEADLESS", True)
    use_stealth = _bool_env(use_stealth, "SELENIUM_STEALTH", False)
    timeout = timeout if timeout is not None else int(os.getenv("SELENIUM_TIMEOUT", "30"))
    proxy = _choose_proxy(proxy, proxies)
    try:
        import undetected_chromedriver as uc
        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        driver = uc.Chrome(options=options)
        try:
            driver.set_page_load_timeout(timeout)
        except Exception:
            pass
        if use_stealth:
            try:
                from selenium_stealth import stealth
                stealth(
                    driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    run_on_insecure_origins=False,
                )
            except Exception:
                pass
        return driver
    except Exception as e:
        raise RuntimeError("Failed to initialize web driver") from e
