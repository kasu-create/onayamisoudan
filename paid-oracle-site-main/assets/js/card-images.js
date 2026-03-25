/**
 * タロットカード画像のパス解決（assets/cards/{id}.{ext}）
 * 画像は著作権の都合でリポジトリに同梱しません。README の一覧に沿って配置してください。
 */

import { buildFullDeck } from "./tarot-deck.js";

/** 試す順（先に見つかった拡張子を使用） */
export const CARD_IMAGE_EXTENSIONS = ["jpg", "webp", "png", "jpeg"];

/**
 * @param {string} cardId 例: m00, wands_ace
 * @param {string} ext 拡張子（ドットなし）
 */
export function resolveCardImageUrl(cardId, ext) {
  return new URL(`../cards/${cardId}.${ext}`, import.meta.url).href;
}

/** デッキに含まれる全カードID（画像ファイル名のベースと一致） */
export function getAllCardImageIds() {
  return buildFullDeck().map((c) => c.id);
}
