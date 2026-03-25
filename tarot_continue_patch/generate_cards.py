#!/usr/bin/env python3
"""78枚のタロット風SVGを assets/cards/c01.svg … c78.svg として出力（オリジナル簡易デザイン）。"""

from __future__ import annotations

from pathlib import Path

MAJOR_JA = [
    "愚者",
    "魔術師",
    "女教皇",
    "女帝",
    "皇帝",
    "法王",
    "恋人",
    "戦車",
    "力",
    "隠者",
    "運命の輪",
    "正義",
    "吊るされた男",
    "死",
    "節制",
    "悪魔",
    "塔",
    "星",
    "月",
    "太陽",
    "審判",
    "世界",
]

SUITS_JA = [
    ("ワンド", "◇"),
    ("カップ", "▽"),
    ("ソード", "△"),
    ("ペンタクル", "⬡"),
]

PIPS = [
    ("エース", 1),
    ("2", 2),
    ("3", 3),
    ("4", 4),
    ("5", 5),
    ("6", 6),
    ("7", 7),
    ("8", 8),
    ("9", 9),
    ("10", 10),
]

COURTS = ["ページ", "ナイト", "クイーン", "キング"]


def build_names() -> list[tuple[str, str]]:
    """(表示名, サブタイトル) 78件"""
    out: list[tuple[str, str]] = [(n, "大アルカナ") for n in MAJOR_JA]
    for suit, _glyph in SUITS_JA:
        for label, _n in PIPS:
            out.append((f"{suit}の{label}", "小アルカナ"))
        for court in COURTS:
            out.append((f"{suit}の{court}", "小アルカナ"))
    return out


def svg_for_index(i: int, title: str, subtitle: str) -> str:
    n = i + 1
    num = str(n).zfill(2)
    hue = (n * 17) % 360
    hue2 = (hue + 48) % 360
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="360" height="600" viewBox="0 0 360 600" role="img" aria-label="{title}">
  <defs>
    <linearGradient id="g{n}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="hsl({hue} 55% 16%)"/>
      <stop offset="100%" stop-color="hsl({hue2} 60% 9%)"/>
    </linearGradient>
    <radialGradient id="r{n}" cx="50%" cy="30%" r="65%">
      <stop offset="0%" stop-color="hsla({hue2} 90% 78% / 0.45)"/>
      <stop offset="100%" stop-color="hsla({hue2} 90% 78% / 0)"/>
    </radialGradient>
  </defs>
  <rect width="360" height="600" rx="22" fill="url(#g{n})"/>
  <rect x="12" y="12" width="336" height="576" rx="14" fill="none" stroke="hsl({hue2} 50% 55%)" stroke-width="2"/>
  <circle cx="180" cy="220" r="120" fill="url(#r{n})"/>
  <circle cx="180" cy="220" r="86" fill="none" stroke="hsl({hue2} 85% 80%)" stroke-width="1.6"/>
  <text x="180" y="78" fill="hsl({hue2} 90% 88%)" text-anchor="middle" style="font: 600 18px Georgia, serif; letter-spacing:2px;">{num}</text>
  <text x="180" y="420" fill="hsl({hue2} 95% 92%)" text-anchor="middle" style="font: 700 22px Georgia, serif;">{title}</text>
  <text x="180" y="452" fill="hsl({hue2} 40% 72%)" text-anchor="middle" style="font: 500 13px 'Segoe UI', sans-serif;">{subtitle}</text>
  <text x="180" y="560" fill="hsl({hue2} 50% 70%)" text-anchor="middle" style="font: 500 10px 'Segoe UI', sans-serif; letter-spacing:3px;">REN'S TAROT</text>
</svg>
"""


def main() -> None:
    root = Path(__file__).resolve().parent
    out_dir = root / "assets" / "cards"
    out_dir.mkdir(parents=True, exist_ok=True)
    names = build_names()
    if len(names) != 78:
        raise SystemExit(f"Expected 78 cards, got {len(names)}")
    for i, (title, sub) in enumerate(names):
        num = str(i + 1).zfill(2)
        (out_dir / f"c{num}.svg").write_text(svg_for_index(i, title, sub), encoding="utf-8")
    print(f"Wrote 78 files to {out_dir}")


if __name__ == "__main__":
    main()
