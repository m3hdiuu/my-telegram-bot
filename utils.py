import os
import json
from datetime import datetime

# فایل ذخیره‌سازی آمار
STATS_FILE = "stats.json"
# فایل تنظیمات
CONFIG_FILE = "config.json"
# فایل مدیران
ADMINS_FILE = "admins.json"
# فایل تأمین‌کنندگان
SUPPLIERS_FILE = "suppliers.json"

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data["users"] = set(data.get("users", []))
                return data
        except json.JSONDecodeError:
            return {"users": set(), "downloads": {}, "tender_downloads": {}}
    return {"users": set(), "downloads": {}, "tender_downloads": {}}

def save_stats(stats):
    data = {
        "users": list(stats["users"]),
        "downloads": {k: list(v) for k, v in stats["downloads"].items()},
        "tender_downloads": stats["tender_downloads"]
    }
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"update_mode": False}
    return {"update_mode": False}

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def load_admins():
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return {170242704}  # آی‌دی ادمین اصلی

def save_admins(admins):
    with open(ADMINS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(admins), f, ensure_ascii=False, indent=4)

def load_suppliers():
    if os.path.exists(SUPPLIERS_FILE):
        try:
            with open(SUPPLIERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_suppliers(suppliers):
    with open(SUPPLIERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(suppliers, f, ensure_ascii=False, indent=4)

datetime = datetime  # برای دسترسی در فایل‌های دیگر