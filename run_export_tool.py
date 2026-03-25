import os
import subprocess
import sys


def main() -> None:
    root = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(root, "question_export_app.py")

    if not os.path.exists(app_path):
        print("question_export_app.py が見つかりません。")
        sys.exit(1)

    python_cmd = sys.executable or "python"
    cmd = [python_cmd, "-m", "streamlit", "run", app_path, "--server.port", "8502", "--server.address", "0.0.0.0"]
    print("起動コマンド:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print("書き出しツールの起動に失敗しました。")
        print("エラーコード:", exc.returncode)
        sys.exit(exc.returncode)


if __name__ == "__main__":
    main()
