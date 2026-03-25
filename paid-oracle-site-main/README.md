# 有料オラクル鑑定（GitHub Pages + カスタムドメイン）

**左にファイルが出ないときは `START_HERE.md` を開いてください。**（Cursor では **`paid-oracle-site` フォルダごと**を「フォルダーを開く」で開く必要があります。）

## URL 構成（他LPと分離）

| パス | 役割 |
|------|------|
| `/oracle/` | 有料商品のLP・説明・STORES への導線 |
| `/oracle/reading/` | 購入者向け鑑定フロー（3枚 → 5枚）※トークンはクエリで渡す想定 |

例（サブドメインを切る場合）:

- `https://oracle.example.com/oracle/`
- `https://oracle.example.com/oracle/reading/?token=YOUR_TOKEN`

ルートドメイン直下に置く場合は `example.com/oracle/` 同様。

## GitHub Pages の設定

1. リポジトリ **Settings → Pages**
2. **Branch**: `main` / **folder**: `/ (root)`
3. **Custom domain**: 使うドメイン（例: `oracle.example.com`）を入力
4. ドメイン側で **CNAME** を `YOUR_USERNAME.github.io` に向ける（GitHub の案内に従う）
5. **Enforce HTTPS** をオン（証明書が発行されたら）

ルートに置いた `CNAME` ファイルにドメインを1行で書いておくと Pages が参照します（中身は実ドメインに差し替え）。

## ファイル構成（主要）

| パス | 内容 |
|------|------|
| `oracle/index.html` | 有料LP |
| `oracle/reading/index.html` | 鑑定フロー（GitHub風UI） |
| `assets/js/tarot-deck.js` | **78枚**のカードデータのみ（名前・ID・スート） |
| `assets/js/card-meanings.js` | **鑑定文案**（大アルカナ個別／小アルカナは追記で上書き可） |
| `assets/js/spread-config.js` | 3枚・5枚のポジション定義 |
| `assets/js/reading.js` | シャッフル・配布・まとめ生成 |
| `assets/css/github-workspace.css` | 鑑定ページのGitHub風スタイル |

画像アセットは未使用。カードは CSS で表示（後から画像に差し替え可）。

## ローカル確認

静的ファイルなので、任意のローカルサーバーで `paid-oracle-site` をルートにして開いてください。

```bash
# 例: npx（このフォルダで実行）
npx --yes serve .
```

`http://localhost:3000/oracle/` と `http://localhost:3000/oracle/reading/` を確認。

## セキュリティ

- **トークン検証**を本番で行う場合は、GitHub Pages だけでは不十分なことがあります。  
  最初は「長い推測困難なURLを1回だけメール送付」など運用で補うか、後から Workers / Firebase 等を追加してください。
- 秘密情報はリポジトリにコミットしない。
