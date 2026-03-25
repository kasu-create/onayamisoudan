# -*- coding: utf-8 -*-
import json
import os
from datetime import date

def _quota_path():
    return os.path.join(os.path.dirname(__file__), "quota_usage.json")

def _load():
    p = _quota_path()
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save(data):
    with open(_quota_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_upload_count_for_today(project_key: str) -> int:
    return int(_load().get(project_key, {}).get(str(date.today()), 0))

def can_upload(project_key: str, max_per_day: int) -> bool:
    return get_upload_count_for_today(project_key) < max_per_day

def record_upload(project_key: str) -> None:
    data = _load()
    today = str(date.today())
    if project_key not in data:
        data[project_key] = {}
    data[project_key][today] = data[project_key].get(today, 0) + 1
    _save(data)
