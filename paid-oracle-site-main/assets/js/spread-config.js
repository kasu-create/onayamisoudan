/**
 * スプレッド定義（3枚 → 5枚）
 * 鑑定文テンプレは後から差し替え可能
 */

export const SPREAD_THREE = [
  { key: "situation", label: "現状", hint: "いま置かれている流れ" },
  { key: "block", label: "障害・課題", hint: "乗り越えるところ" },
  { key: "advice", label: "アドバイス", hint: "意識するとよい向き" },
];

export const SPREAD_FIVE = [
  { key: "core", label: "核心", hint: "悩みの中心にあるもの" },
  { key: "hidden", label: "見えにくい要素", hint: "まだ気づいていない層" },
  { key: "near", label: "近い動き", hint: "この先しばらくの傾向" },
  { key: "stance", label: "取るとよい態度", hint: "整え方・立ち位置" },
  { key: "outlook", label: "まとめの示唆", hint: "全体を束ねるメッセージ" },
];
