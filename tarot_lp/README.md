# Tarot LP (78 cards)

## 1) 78枚のカードを生成

```powershell
cd C:\Users\green\yt-shorts-app\tarot_lp
python generate_cards.py
```

`assets/cards` に 78 枚の SVG が作成されます。

## 2) ローカルでサイト表示

```powershell
cd C:\Users\green\yt-shorts-app\tarot_lp
python -m http.server 8080
```

ブラウザで `http://localhost:8080` を開くと表示されます。

## 3) できること

- 有料版に寄せたダークトーンの世界観
- 1枚引き（ランダム表示）
- 78枚のカード一覧表示
