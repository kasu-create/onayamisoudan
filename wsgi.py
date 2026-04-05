"""
本番用エントリ（リポジトリルートから起動するための1本）。

Render 例（Root Directory は空のまま）:
  Build:  pip install -r tools/revenue/requirements.txt
  Start:  gunicorn --bind 0.0.0.0:$PORT wsgi:app

tools/revenue へ cd しないので、「cd が失敗して Not Found」系を避けやすい。
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_REVENUE = _ROOT / "tools" / "revenue"
if not _REVENUE.is_dir():
    raise RuntimeError(f"tools/revenue が見つかりません: {_REVENUE}")
sys.path.insert(0, str(_REVENUE))

from server import app  # noqa: E402

__all__ = ["app"]
