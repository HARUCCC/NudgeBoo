import json
import os
import sys
from datetime import datetime

if getattr(sys, 'frozen', False):
    _BASE = os.path.dirname(sys.executable)
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(_BASE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

DEFAULT_CONFIG = {
    "log_dir": os.path.join(_BASE, "logs"),
    "work_mode": "fixed",  # "fixed" or "flexible"
    "work_start": "09:00",
    "work_end": "18:00",
    "work_duration": 9,  # total hours including lunch (for flexible mode)
    "reminder_interval_min": 120,
    "lunch_start": "12:00",
    "lunch_end": "13:30",
    "dnd_mode": False,
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            merged = {**DEFAULT_CONFIG, **cfg}
            return merged
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_today_md_path(cfg):
    log_dir = cfg["log_dir"]
    os.makedirs(log_dir, exist_ok=True)
    today = datetime.now().strftime("%m.%d")
    return os.path.join(log_dir, f"{today}.md")


def ensure_today_md(cfg):
    path = get_today_md_path(cfg)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            pass
    return path


def append_log(cfg, content):
    path = ensure_today_md(cfg)
    with open(path, "a", encoding="utf-8") as f:
        try:
            with open(path, "r", encoding="utf-8") as check:
                text = check.read()
                if text and not text.endswith('\n'):
                    f.write('\n')
        except:
            pass
        f.write(content + "\n")
    return path
