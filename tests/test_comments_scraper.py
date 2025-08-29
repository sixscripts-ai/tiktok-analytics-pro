from __future__ import annotations
import types, sys

class DummyBy:
    CSS_SELECTOR = "css"

selenium = types.ModuleType("selenium")
webdriver = types.ModuleType("selenium.webdriver")
common = types.ModuleType("selenium.webdriver.common")
by_mod = types.ModuleType("selenium.webdriver.common.by")
by_mod.By = DummyBy
support = types.ModuleType("selenium.webdriver.support")
support_ui = types.ModuleType("selenium.webdriver.support.ui")
support_ui.WebDriverWait = object
expected = types.ModuleType("selenium.webdriver.support.expected_conditions")
expected.presence_of_element_located = lambda *a, **kw: None
support.ui = support_ui
support.expected_conditions = expected
webdriver.common = common
common.by = by_mod
webdriver.support = support
selenium.webdriver = webdriver
selenium.webdriver.support = support
common_ex = types.ModuleType("selenium.common.exceptions")
common_ex.TimeoutException = Exception
common_ex.WebDriverException = Exception
common_ex.NoSuchElementException = Exception
selenium.common = types.SimpleNamespace(exceptions=common_ex)

sys.modules['selenium'] = selenium
sys.modules['selenium.webdriver'] = webdriver
sys.modules['selenium.webdriver.common'] = common
sys.modules['selenium.webdriver.common.by'] = by_mod
sys.modules['selenium.webdriver.support'] = support
sys.modules['selenium.webdriver.support.ui'] = support_ui
sys.modules['selenium.webdriver.support.expected_conditions'] = expected
sys.modules['selenium.common'] = types.ModuleType('selenium.common')
sys.modules['selenium.common.exceptions'] = common_ex

import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tiktok_scraping_scripts'))
from scrapers import comments_scraper

class FakeElement:
    def __init__(self, text: str = "", attrs: dict | None = None, children: dict | None = None) -> None:
        self.text = text
        self._attrs = attrs or {}
        self._children = children or {}

    def get_attribute(self, attr: str):
        return self._attrs.get(attr)

    def find_elements(self, how, sel):
        return self._children.get((how, sel), [])


def test_int_parsing() -> None:
    assert comments_scraper._int('1.2K') == 1200
    assert comments_scraper._int('3M') == 3_000_000
    assert comments_scraper._int(None) is None


def test_extract_comment_fields() -> None:
    author = FakeElement(text='user', attrs={'href': 'https://tiktok.com/@user'})
    text_el = FakeElement(text='hello world')
    like_el = FakeElement(text='1.5K')
    time_el = FakeElement(attrs={'title': '2023-01-01'})
    tile = FakeElement(
        attrs={'data-comment-id': 'c1'},
        children={
            ('css', "[data-e2e='comment-level1-username']"): [author],
            ('css', "[data-e2e='comment-text']"): [text_el],
            ('css', "[data-e2e='comment-like-count']"): [like_el],
            ('css', "abbr[title], time[title]"): [time_el],
        }
    )
    cid, user, text, likes, ts = comments_scraper._extract_comment_fields(tile)
    assert cid == 'c1'
    assert user == 'user'
    assert text == 'hello world'
    assert likes == 1500
    assert ts == '2023-01-01'
