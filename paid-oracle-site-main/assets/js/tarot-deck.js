/**
 * ライダー版準拠・78枚フルデッキ（日本語名）
 * 鑑定文案は別ファイル: card-meanings.js（getCardMeaning(card.id)）
 * 画像は assets/cards/{id}.webp|png|jpg（card-images.js 参照）。未配置時は記号表示。
 */

const MAJOR = [
  { id: "m00", n: 0, nameJa: "愚者" },
  { id: "m01", n: 1, nameJa: "魔術師" },
  { id: "m02", n: 2, nameJa: "女教皇" },
  { id: "m03", n: 3, nameJa: "女帝" },
  { id: "m04", n: 4, nameJa: "皇帝" },
  { id: "m05", n: 5, nameJa: "法王" },
  { id: "m06", n: 6, nameJa: "恋人" },
  { id: "m07", n: 7, nameJa: "戦車" },
  { id: "m08", n: 8, nameJa: "力" },
  { id: "m09", n: 9, nameJa: "隠者" },
  { id: "m10", n: 10, nameJa: "運命の輪" },
  { id: "m11", n: 11, nameJa: "正義" },
  { id: "m12", n: 12, nameJa: "吊るされた男" },
  { id: "m13", n: 13, nameJa: "死" },
  { id: "m14", n: 14, nameJa: "節制" },
  { id: "m15", n: 15, nameJa: "悪魔" },
  { id: "m16", n: 16, nameJa: "塔" },
  { id: "m17", n: 17, nameJa: "星" },
  { id: "m18", n: 18, nameJa: "月" },
  { id: "m19", n: 19, nameJa: "太陽" },
  { id: "m20", n: 20, nameJa: "審判" },
  { id: "m21", n: 21, nameJa: "世界" },
];

const SUITS = [
  { id: "wands", nameJa: "ワンド", glyph: "◇" },
  { id: "cups", nameJa: "カップ", glyph: "▽" },
  { id: "swords", nameJa: "ソード", glyph: "△" },
  { id: "pentacles", nameJa: "ペンタクル", glyph: "⬡" },
];

const PIPS = [
  { rank: "ace", labelJa: "エース", num: 1 },
  { rank: "02", labelJa: "2", num: 2 },
  { rank: "03", labelJa: "3", num: 3 },
  { rank: "04", labelJa: "4", num: 4 },
  { rank: "05", labelJa: "5", num: 5 },
  { rank: "06", labelJa: "6", num: 6 },
  { rank: "07", labelJa: "7", num: 7 },
  { rank: "08", labelJa: "8", num: 8 },
  { rank: "09", labelJa: "9", num: 9 },
  { rank: "10", labelJa: "10", num: 10 },
];

const COURTS = [
  { rank: "page", labelJa: "ページ" },
  { rank: "knight", labelJa: "ナイト" },
  { rank: "queen", labelJa: "クイーン" },
  { rank: "king", labelJa: "キング" },
];

function buildMinorCards() {
  const out = [];
  for (const suit of SUITS) {
    for (const p of PIPS) {
      out.push({
        id: `${suit.id}_${p.rank}`,
        arcana: "minor",
        suit: suit.id,
        suitJa: suit.nameJa,
        glyph: suit.glyph,
        rank: p.rank,
        nameJa: `${suit.nameJa}の${p.labelJa}`,
      });
    }
    for (const c of COURTS) {
      out.push({
        id: `${suit.id}_${c.rank}`,
        arcana: "minor",
        suit: suit.id,
        suitJa: suit.nameJa,
        glyph: suit.glyph,
        rank: c.rank,
        nameJa: `${suit.nameJa}の${c.labelJa}`,
      });
    }
  }
  return out;
}

const MINOR_CACHE = buildMinorCards();

/**
 * @returns {Array<{ id: string, arcana: string, nameJa: string, glyph?: string, suit?: string, suitJa?: string, rank?: string, majorIndex?: number }>}
 */
export function buildFullDeck() {
  const major = MAJOR.map((m) => ({
    id: m.id,
    arcana: "major",
    nameJa: m.nameJa,
    majorIndex: m.n,
    glyph: "✦",
  }));
  return [...major, ...MINOR_CACHE.map((c) => ({ ...c }))];
}

/** Fisher–Yates（コピーを返す） */
export function shuffleDeck(deck) {
  const a = deck.map((c) => ({ ...c }));
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function deckCount() {
  return 22 + MINOR_CACHE.length;
}
