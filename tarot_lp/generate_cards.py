#!/usr/bin/env python3
"""Generate 78 original SVG tarot-style cards for local use."""

from __future__ import annotations

from pathlib import Path
import re


MAJOR_ARCANA = [
    "The Fool",
    "The Magician",
    "The High Priestess",
    "The Empress",
    "The Emperor",
    "The Hierophant",
    "The Lovers",
    "The Chariot",
    "Strength",
    "The Hermit",
    "Wheel of Fortune",
    "Justice",
    "The Hanged Man",
    "Death",
    "Temperance",
    "The Devil",
    "The Tower",
    "The Star",
    "The Moon",
    "The Sun",
    "Judgement",
    "The World",
]

RANKS = [
    "Ace",
    "Two",
    "Three",
    "Four",
    "Five",
    "Six",
    "Seven",
    "Eight",
    "Nine",
    "Ten",
    "Page",
    "Knight",
    "Queen",
    "King",
]

SUITS = ["Wands", "Cups", "Swords", "Pentacles"]


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def card_svg(index: int, title: str, subtitle: str) -> str:
    hue = (index * 19) % 360
    hue2 = (hue + 50) % 360
    number = str(index + 1).zfill(2)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="420" height="700" viewBox="0 0 420 700" role="img" aria-label="{title}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="hsl({hue} 65% 18%)"/>
      <stop offset="100%" stop-color="hsl({hue2} 70% 10%)"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="32%" r="68%">
      <stop offset="0%" stop-color="hsla({hue2} 95% 85% / 0.55)"/>
      <stop offset="100%" stop-color="hsla({hue2} 95% 85% / 0)"/>
    </radialGradient>
  </defs>
  <rect width="420" height="700" rx="26" fill="url(#bg)"/>
  <rect x="14" y="14" width="392" height="672" rx="18" fill="none" stroke="hsl({hue2} 55% 72%)" stroke-width="2.3"/>
  <rect x="33" y="33" width="354" height="634" rx="10" fill="none" stroke="hsl({hue2} 55% 50%)" stroke-width="1"/>
  <circle cx="210" cy="250" r="138" fill="url(#glow)"/>
  <circle cx="210" cy="250" r="98" fill="none" stroke="hsl({hue2} 90% 85%)" stroke-width="1.8"/>
  <path d="M210 150 L240 250 L210 350 L180 250 Z" fill="none" stroke="hsl({hue2} 90% 83%)" stroke-width="2"/>
  <path d="M112 250 H308 M210 152 V348" stroke="hsl({hue2} 90% 83%)" stroke-width="1.2"/>
  <text x="210" y="90" fill="hsl({hue2} 92% 88%)" text-anchor="middle" style="font: 600 22px Georgia, serif; letter-spacing: 2px;">{number}</text>
  <text x="210" y="492" fill="hsl({hue2} 95% 90%)" text-anchor="middle" style="font: 700 28px Georgia, serif;">{title}</text>
  <text x="210" y="528" fill="hsl({hue2} 55% 78%)" text-anchor="middle" style="font: 500 16px 'Segoe UI', sans-serif; letter-spacing: 1px;">{subtitle}</text>
  <text x="210" y="638" fill="hsl({hue2} 65% 84%)" text-anchor="middle" style="font: 500 12px 'Segoe UI', sans-serif; letter-spacing: 3px;">REN'S TAROT COLLECTION</text>
</svg>
"""


def build_card_names() -> list[tuple[str, str]]:
    cards: list[tuple[str, str]] = [(name, "Major Arcana") for name in MAJOR_ARCANA]
    for suit in SUITS:
        cards.extend((f"{rank} of {suit}", "Minor Arcana") for rank in RANKS)
    return cards


def main() -> None:
    root = Path(__file__).resolve().parent
    cards_dir = root / "assets" / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)

    cards = build_card_names()
    if len(cards) != 78:
        raise RuntimeError(f"Expected 78 cards, got {len(cards)}")

    for i, (title, subtitle) in enumerate(cards):
        filename = f"{str(i + 1).zfill(2)}_{slugify(title)}.svg"
        content = card_svg(i, title, subtitle)
        (cards_dir / filename).write_text(content, encoding="utf-8")

    print(f"Created {len(cards)} cards in: {cards_dir}")


if __name__ == "__main__":
    main()
