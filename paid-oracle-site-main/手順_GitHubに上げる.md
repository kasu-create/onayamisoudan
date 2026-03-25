# GitHub に上げる（やることだけ）

## 事前に用意するもの

- GitHub のアカウント
- ブラウザで **新しいリポジトリ** を1つ作る（名前は `paid-oracle-site` でOK）
- 作ったあと表示される **HTTPS のURL**（例: `https://github.com/kasu-create/paid-oracle-site.git`）をコピー

**※ PCに Git が入っていないと `git` コマンドが使えません。**  
→ [Git for Windows](https://git-scm.com/download/win) を先にインストールしてください。

---

## 手順（この順で）

### 1. フォルダを開く

エクスプローラーで次を開く:

`デスクトップ\paid-oracle-site`

（Cursor なら **ファイル → フォルダーを開く** でこのフォルダを開いてもOK）

### 2. ターミナルを開く

- そのフォルダの中で **アドレスバー** をクリック → `cmd` と入力して Enter  
  **または**
- Cursor で **ターミナル → 新しいターミナル**（フォルダが `paid-oracle-site` になっていること）

### 3. コマンドをコピペ（1行ずつ Enter）

**※ 最後の `origin` のURLだけ、あなたのリポジトリのURLに書き換え**

```bash
git init
git add .
git commit -m "Initial: paid oracle site"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/paid-oracle-site.git
git push -u origin main
```

### 4. ログインを聞かれたら

- ブラウザで GitHub にログインする  
- または **Personal Access Token** をパスワード代わりに使う（GitHub の Settings → Developer settings）

### 5. GitHub Pages（サイトを公開したいとき）

1. GitHub のリポジトリページ → **Settings**
2. 左メニュー **Pages**
3. **Branch** で `main` と `/ (root)` を選んで Save  
4. 数分後に `https://あなたのユーザー名.github.io/paid-oracle-site/oracle/` のようなURLが案内される（リポジトリ名によってパスが変わります）

---

## よくあるつまずき

| 現象 | 対処 |
|------|------|
| `git` と言われる | [Git for Windows](https://git-scm.com/download/win) をインストール |
| `remote origin already exists` | `git remote remove origin` のあと、もう一度 `git remote add origin ...` |
| push が拒否される | リポジトリを GitHub 上で **README付きで作ってしまった** 場合は、画面の案内に従うか、空のリポジトリを新規作成し直す |

---

## このフォルダに含まれる CSS について

`assets/css/github-workspace.css` は **普通のファイル** です。  
`git add .` で **一緒にGitHubに上がります**。別操作は不要です。
