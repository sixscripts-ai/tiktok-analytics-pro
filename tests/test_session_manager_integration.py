import sys
import os
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tiktok_scraping_scripts.network.session_manager import create_session
from tiktok.tiktok_analyzer import TikTokEarningsAnalyzer
from tiktok.tiktok_research import TikTokResearch
import tiktok_scraping_scripts.anti_detection_system as ads


def test_session_env_config(monkeypatch):
    monkeypatch.setenv("TIKTOK_PROXY", "http://proxy.example:8080")
    monkeypatch.setenv("TIKTOK_USER_AGENT", "EnvAgent/1.0")
    monkeypatch.setenv("TIKTOK_EXTRA_HEADERS", '{"X-Test": "1"}')

    session = create_session()
    assert session.proxies["http"] == "http://proxy.example:8080"
    assert session.proxies["https"] == "http://proxy.example:8080"
    assert session.headers["User-Agent"] == "EnvAgent/1.0"
    assert session.headers["X-Test"] == "1"


def test_consumers_share_session(monkeypatch):
    monkeypatch.setenv("TIKTOK_USER_AGENT", "EnvAgent/2.0")
    analyzer = TikTokEarningsAnalyzer()
    research = TikTokResearch()
    assert analyzer.session.headers["User-Agent"] == "EnvAgent/2.0"
    assert research.session.headers["User-Agent"] == "EnvAgent/2.0"


def test_anti_detection_uses_env(monkeypatch):
    monkeypatch.setenv("TIKTOK_USER_AGENT", "EnvAgent/3.0")
    monkeypatch.setenv("TIKTOK_PROXY", "http://proxy.example:8080")

    class DummyChromeOptions:
        def __init__(self):
            self.arguments = []
        def add_argument(self, arg):
            self.arguments.append(arg)

    class DummyChrome:
        def __init__(self, options):
            self.options = options
        def execute_cdp_cmd(self, *args, **kwargs):
            pass
        def execute_script(self, *args, **kwargs):
            pass

    uc = SimpleNamespace(Chrome=DummyChrome, ChromeOptions=DummyChromeOptions)
    monkeypatch.setitem(sys.modules, "undetected_chromedriver", uc)

    driver = ads.create_driver()
    args = driver.options.arguments
    assert any("EnvAgent/3.0" in a for a in args)
    assert any("--proxy-server=http://proxy.example:8080" == a for a in args)
