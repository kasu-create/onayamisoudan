# お悩み相談フォーム（Streamlit）

## 公開（Streamlit Community Cloud）

1. このフォルダをGitHubにpushします（GitHub DesktopでOK）
2. Streamlit Community Cloudで「New app」を作成
3. Repository / Branch を選択
4. Main file path を `app.py` にしてDeploy（公開フォーム用）
5. 管理画面は「別アプリ」として `admin_app.py` でDeploy（公開フォームからはリンクしません）

### Secrets（必須）

Streamlit Cloud の App settings → Secrets に、以下を追加します。

```toml
ADMIN_PASS = "ここにパスコード"
```

## 使い方（公開URL）

- 相談フォーム（みんなが入力）: `app.py`（公開URL）
- 管理画面（あなた用）: `admin_app.py`（別URL・パスコード必須）

## Secrets（必須）

Streamlit Cloud の App settings → Secrets に、以下を追加します（管理画面アプリ側）。

```toml
ADMIN_PASS = "ここにパスコード"
```

## 注意（重要）

- `questions_box.csv` はアプリが書き込みます。
- 公開運用する場合は、スパム対策（合言葉・制限）や、保存先（スプレッドシート等）を検討してください。

# YouTube Shorts 多アカウントアップローダー

YouTube Shorts を複数アカウントで自動アップロードするツールです。**GAS 不要・Python のみ**で動きます。

- キューに動画を登録 → 順番にアップロード
- 複数アカウントを登録して、アカウントごとに振り分け可能
- 1日あたりのアップロード数や間隔を設定可能

---

## クイックスタート（すでにセットアップ済みの人）

1. **start_app.bat** をダブルクリックする  
   または ターミナルで:
   ```bash
   cd （このフォルダのパス）
   python run_app.py
   ```
2. ブラウザで **http://localhost:8501** を開く
3. キューに動画を追加して「アップロード実行」

---

## はじめて使う人

**👉 [はじめて使う人向け.md](はじめて使う人向け.md)** に、最初から順に手順をまとめています。

1. Python のインストール
2. このフォルダの置き場所（パスに日本語がないこと）
3. パッケージのインストール
4. config と GCP の client_secrets の用意
5. アカウント登録（add_account.py）
6. キューに動画を追加して実行

---

## 必要なもの

- **Python 3.10 以上**（3.12 や 3.14 でも可）
- **Google Cloud で YouTube Data API v3 を有効にしたプロジェクト**と、その **OAuth クライアント（デスクトップ）** の JSON（client_secrets.json）

---

## Cursor で使う場合

このフォルダを **Cursor** で開くと、AI がプロジェクトの前提・起動方法を理解して案内できます。**Cursor向け説明書.md** を参照してください。

---

## フォルダ構成（目安）

```
（このフォルダ）/
├── app.py              # Web UI
├── run_app.py          # 起動用
├── add_account.py      # アカウント追加
├── config.yaml         # 設定（要作成）
├── upload_queue.csv    # アップロードキュー
├── secrets/
│   └── client_secrets.json   # GCP の認証情報（要配置）
├── accounts/
│   └── account_01/     # 各アカウントのトークン
├── はじめて使う人向け.md
└── 運用のしかた（動画準備・他PCからアカウント追加）.md
```

---

## ほかの人に渡すとき

- このフォルダ一式を ZIP で渡す（**accounts フォルダ内の token.json は個人の権限なので、必要なら除いて渡す**）
- **はじめて使う人向け.md** を読んでもらう
- client_secrets.json は **1つの GCP プロジェクトを共有**すれば、みんなが同じファイルで複数アカウントを追加できる

詳細は **運用のしかた（動画準備・他PCからアカウント追加）.md** を参照。
