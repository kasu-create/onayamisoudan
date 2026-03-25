import os
import subprocess
import sys


def main() -> None:
    """
    シンプルな起動スクリプト。

    - このファイルと同じフォルダにある app.py を Streamlit で起動する
    - 例外が起きた場合はコンソールにメッセージを出す
    """
    root = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(root, "app.py")

    if not os.path.exists(app_path):
        print("app.py が見つかりません。C:\\Users\\green\\yt-shorts-app に app.py を作成してください。")
        sys.exit(1)

    # windows で python / py どちらでも動くようにする
    python_cmd = sys.executable or "python"

    cmd = [python_cmd, "-m", "streamlit", "run", app_path, "--server.port", "8501", "--server.address", "0.0.0.0"]
    print("実行コマンド:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print("Streamlit の起動に失敗しました。")
        print("エラーコード:", e.returncode)
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()

