#!/usr/bin/env python3
"""paid-oracle-site 用: tarot-deck.js の id に合わせて assets/cards/{id}.svg を78枚出力"""

from __future__ import annotations

import sys
from pathlib import Path

MAJOR = [
    ("m00", "愚者"),
    ("m01", "魔術師"),
    ("m02", "女教皇"),
    ("m03", "女帝"),
    ("m04", "皇帝"),
    ("m05", "法王"),
    ("m06", "恋人"),
    ("m07", "戦車"),
    ("m08", "力"),
    ("m09", "隠者"),
    ("m10", "運命の輪"),
    ("m11", "正義"),
    ("m12", "吊るされた男"),
    ("m13", "死"),
    ("m14", "節制"),
    ("m15", "悪魔"),
    ("m16", "塔"),
    ("m17", "星"),
    ("m18", "月"),
    ("m19", "太陽"),
    ("m20", "審判"),
    ("m21", "世界"),
]

SUITS = ["wands", "cups", "swords", "pentacles"]
SUIT_JA = {"wands": "ワンド", "cups": "カップ", "swords": "ソード", "pentacles": "ペンタクル"}
PIPS = [
    ("ace", "エース"),
    ("02", "2"),
    ("03", "3"),
    ("04", "4"),
    ("05", "5"),
    ("06", "6"),
    ("07", "7"),
    ("08", "8"),
    ("09", "9"),
    ("10", "10"),
]
COURTS = [
    ("page", "ページ"),
    ("knight", "ナイト"),
    ("queen", "クイーン"),
    ("king", "キング"),
]


def all_card_defs() -> list[tuple[str, str, str]]:
    """(id, title, subtitle)"""
    out: list[tuple[str, str, str]] = [(cid, name, "大アルカナ") for cid, name in MAJOR]
    for suit in SUITS:
        sj = SUIT_JA[suit]
        for rank, label in PIPS:
            cid = f"{suit}_{rank}"
            out.append((cid, f"{sj}の{label}", "小アルカナ"))
        for rank, label in COURTS:
            cid = f"{suit}_{rank}"
            out.append((cid, f"{sj}の{label}", "小アルカナ"))
    return out


def svg_content(index: int, card_id: str, title: str, subtitle: str) -> str:
    h = (index * 19 + hash(card_id) % 97) % 360
    h2 = (h + 50) % 360
    short_id = card_id.replace("_", " ")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="420" height="700" viewBox="0 0 420 700" role="img" aria-label="{title}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="hsl({h} 62% 16%)"/>
      <stop offset="100%" stop-color="hsl({h2} 65% 9%)"/>
    </linearGradient>
    <radialGradient id="gl" cx="50%" cy="32%" r="68%">
      <stop offset="0%" stop-color="hsla({h2} 92% 82% / 0.5)"/>
      <stop offset="100%" stop-color="hsla({h2} 92% 82% / 0)"/>
    </radialGradient>
  </defs>
  <rect width="420" height="700" rx="26" fill="url(#bg)"/>
  <rect x="14" y="14" width="392" height="672" rx="18" fill="none" stroke="hsl({h2} 50% 58%)" stroke-width="2.2"/>
  <circle cx="210" cy="250" r="130" fill="url(#gl)"/>
  <text x="210" y="88" fill="hsl({h2} 88% 85%)" text-anchor="middle" style="font: 600 14px ui-monospace, monospace; letter-spacing:1px;">{card_id}</text>
  <text x="210" y="500" fill="hsl({h2} 95% 92%)" text-anchor="middle" style="font: 700 26px Georgia, serif;">{title}</text>
  <text x="210" y="538" fill="hsl({h2} 45% 72%)" text-anchor="middle" style="font: 500 15px 'Segoe UI', sans-serif;">{subtitle}</text>
  <text x="210" y="642" fill="hsl({h2} 55% 68%)" text-anchor="middle" style="font: 500 11px 'Segoe UI', sans-serif; letter-spacing:2px;">REN'S TAROT</text>
</svg>
"""


def main() -> None:
    dest = Path.home() / "Desktop" / "paid-oracle-site" / "assets" / "cards"
    if len(sys.argv) >= 2:
        dest = Path(sys.argv[1]).expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)
    defs = all_card_defs()
    if len(defs) != 78:
        raise SystemExit(f"expected 78, got {len(defs)}")
    for i, (cid, title, sub) in enumerate(defs):
        (dest / f"{cid}.svg").write_text(svg_content(i, cid, title, sub), encoding="utf-8")
    print(f"Wrote {len(defs)} SVGs to {dest}")


if __name__ == "__main__":
    main()
