
import os, importlib
from pathlib import Path

def _load_from_spec(spec: str):
    mod, func = spec.split(":")
    return getattr(importlib.import_module(mod), func)

def discover_driver_factory():
    # 1) ENV var
    spec = os.getenv("TIKTOK_DRIVER_FACTORY")
    if spec:
        try:
            return _load_from_spec(spec)
        except Exception as e:
            raise RuntimeError(f"Failed to load driver factory from TIKTOK_DRIVER_FACTORY={spec}: {e}")

    # 2) Config TOML (repo / cwd / home)
    for cfg in (Path.cwd()/ "tiktok_scraping_scripts"/"config.toml",
                Path.cwd()/ "config.toml",
                Path.home()/ ".tiktokctl.toml"):
        if cfg.exists():
            try:
                try:
                    import tomllib as toml  # py311+
                except Exception:
                    import tomli as toml     # py310 and below (add tomli to requirements if needed)
                conf = toml.loads(cfg.read_text(encoding="utf-8"))
                factory_spec = (conf.get("driver") or {}).get("factory")
                if factory_spec:
                    return _load_from_spec(factory_spec)
            except Exception as e:
                raise RuntimeError(f"Failed to parse driver factory from {cfg}: {e}")

    # 3) Fallback to built-in anti-detection system
    try:
        import anti_detection_system as ads
        return getattr(ads, "create_driver")
    except Exception as e:
        print(f"Failed to import anti_detection_system: {e}")
        # Last resort: local undetected-chromedriver (dev convenience)
        try:
            import undetected_chromedriver as uc
            return lambda **kw: uc.Chrome(options=uc.ChromeOptions())
        except Exception as e2:
            raise RuntimeError("No driver factory available. Set TIKTOK_DRIVER_FACTORY or provide config.toml, "
                               "or ensure anti_detection_system.create_driver exists.") from e2
