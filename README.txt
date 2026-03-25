========================================
YouTube Shorts アップローダー
（パスに日本語がない場所に置いて使ってください）
========================================

■ 「encodings が見つからない」エラーについて

このエラーは Python 本体の不具合です。まず Python を修復してください。

1. スタートメニューで「アプリと機能」または「プログラムのアンインストール」を開く
2. 一覧から「Python 3.12」を探す
3. クリックして「変更」→「Repair（修復）」を実行
4. 修復後、PC を再起動し、新しいターミナルを開く

修復でも直らない場合: Python をいったんアンインストールし、
https://www.python.org/downloads/ から再度インストール。
「Add Python to PATH」に必ずチェックを入れる。


■ 起動方法（Python を直したあと）

1. このフォルダを C:\yt-shorts-app など、パスに日本語がない場所にコピーする
2. ターミナルで:

   cd （このフォルダのパス）
   python run_app.py

3. ブラウザで http://localhost:8501 を開く


■ または

このフォルダにある start_app.bat をダブルクリック。


■ 初回セットアップ

- config.example.yaml をコピーして config.yaml を作成
- secrets フォルダに GCP の client_secrets.json を入れる
- ターミナルで: python -m pip install -r requirements.txt

========================================
