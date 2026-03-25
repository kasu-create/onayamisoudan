# GitHub Pages に新しいUIを反映する

[公開中の鑑定ページ](https://kasu-create.github.io/paid-oracle-site/oracle/reading/) は、**GitHub 上の `paid-oracle-site` リポジトリの中身**だけが表示されます。

この PC の `Desktop\paid-oracle-site` で直しても、**プッシュするまで Web 上は変わりません。**

## 手順（GitHub Desktop 例）

1. GitHub Desktop で **`kasu-create/paid-oracle-site`** を開く  
2. **ローカルパス**を、このフォルダ（新UIがある方）に向けるか、新UIのファイルをリポジトリのクローン上にコピーする  
3. 変更が一覧に出たら **Commit** → **Push origin**  
4. 1〜3分待ってから鑑定URLを再読み込み（必要ならキャッシュ削除）

## 確認ポイント

- `oracle/reading/index.html` が `paid-reading.css` を読み込んでいること  
- `assets/css/paid-reading.css` がリポジトリに含まれていること  
- `assets/js/reading.js` が新しい内容であること  

## まだ古い画面のとき

- 別フォルダの古いプロジェクトを Push していないか確認  
- ブラウザの **スーパーリロード**（モバイルはタブを閉じて開き直し）
