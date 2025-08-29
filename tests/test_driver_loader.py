from __future__ import annotations
import importlib, types, sys, pathlib
from pathlib import Path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tiktok_scraping_scripts'))
import driver_loader


def test_env_variable_overrides(monkeypatch) -> None:
    monkeypatch.setenv('TIKTOK_DRIVER_FACTORY', 'math:sin')
    factory = driver_loader.discover_driver_factory()
    assert factory is importlib.import_module('math').sin


def test_config_file_used(monkeypatch, tmp_path) -> None:
    cfg_dir = tmp_path / 'tiktok_scraping_scripts'
    cfg_dir.mkdir()
    (cfg_dir / 'config.toml').write_text('[driver]\nfactory = "math:cos"', encoding='utf-8')
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv('TIKTOK_DRIVER_FACTORY', raising=False)
    factory = driver_loader.discover_driver_factory()
    assert factory is importlib.import_module('math').cos


def test_fallback_to_ads(monkeypatch) -> None:
    monkeypatch.delenv('TIKTOK_DRIVER_FACTORY', raising=False)
    cfg = Path('tiktok_scraping_scripts/config.toml')
    if cfg.exists():
        cfg.unlink()
    ads = types.ModuleType('anti_detection_system')
    def create_driver() -> str:
        return 'driver'
    ads.create_driver = create_driver
    monkeypatch.setitem(sys.modules, 'anti_detection_system', ads)
    factory = driver_loader.discover_driver_factory()
    assert factory() == 'driver'
