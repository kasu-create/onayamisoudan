# 無料鑑定 `continue.html` 用パッチ（78枚タロット画像）

対象: [無料鑑定｜恋愛オラクル（continue.html）](https://kasu-create.github.io/tarot/continue.html)

## 内容

- `continue.html` … 3枚選択画面で **`assets/cards/c01.svg`〜`c78.svg` から毎回ランダムに3枚** を表示（A/B/C の意味づけは従来どおり）
- `assets/cards/` … 78枚のオリジナル簡易SVG（著作権クリアの自己生成デザイン）
- `generate_cards.py` … カードを再生成するとき用

## GitHub（kasu-create/tarot）への反映手順

1. リポジトリ [kasu-create/tarot](https://github.com/kasu-create/tarot) をクローン（または既存の作業コピーを開く）
2. このフォルダ内の **`continue.html`** をリポジトリ直下の `continue.html` に上書きコピー
3. フォルダ **`assets/`** ごとリポジトリ直下にコピー（`assets/cards/c01.svg` … が並ぶ状態）
4. `git add` → `commit` → `push`（GitHub Pages が `main` なら自動で反映）

## ローカル確認

```powershell
cd C:\Users\green\yt-shorts-app\tarot_continue_patch
python -m http.server 8765
```

ブラウザで `http://localhost:8765/continue.html` を開き、「次へ：カードを選ぶ」で画像が毎回変わることを確認。

## 画像の差し替え

実カード画像（ご自身で権利が明確なもの）に差し替える場合は、`assets/cards/c01.svg`〜`c78.svg` を同じファイル名で置き換えてください（拡張子を `.png` 等に変える場合は `continue.html` 内の `TAROT_DECK_URLS` も合わせて変更）。
