import json
import os
from pathlib import Path
from typing import Any, Dict

APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "OmniCall"
CONFIG_PATH = APP_DIR / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "display_name": "",
    "user_id": "",
    "pairing_link": "",
    "test_confirmed": False,
    "template_path": "",
    "threshold": 0.8,
    "debounce_seconds": 10,
    "poll_ms": 200,
    "last_match_ts": None,
    "total_matches": 0,
}

def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    else:
        data = {}
    merged = DEFAULT_CONFIG.copy()
    merged.update(data if isinstance(data, dict) else {})
    return merged

def save_config(cfg: Dict[str, Any]) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
