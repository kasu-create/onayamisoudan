# お悩み相談（Streamlit）

このフォルダだけを使って、公開用フォームと管理画面（別URL）を作ります。

## 公開（Streamlit Community Cloud）

同じGitHubリポジトリから **アプリを2つ**作ります。

### アプリ①：公開フォーム（みんなが入力）

- **Main file path**: `onayami_sodan_app/app.py`
- これが「公開URL」になります

### アプリ②：管理画面（あなた用）

- **Main file path**: `onayami_sodan_app/admin_app.py`
- Secrets を設定（必須）

#### Secrets（管理画面アプリ側）

```toml
ADMIN_PASS = "好きなパスコード"
```

## ローカル起動（確認用）

```bash
cd C:\Users\green\yt-shorts-app
python -m streamlit run onayami_sodan_app/app.py --server.port 8501
python -m streamlit run onayami_sodan_app/admin_app.py --server.port 8502
```

