# ニッチSaaS収益サーバー
# server.py は tools/revenue。ダッシュ用HTML/JSは tools/ 直下を参照するため tools ごとコピー。
FROM python:3.12-slim-bookworm

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY tools/revenue/requirements.txt /app/tools/revenue/requirements.txt
RUN pip install --no-cache-dir -r /app/tools/revenue/requirements.txt

COPY tools /app/tools
COPY wsgi.py /app/wsgi.py
WORKDIR /app

EXPOSE 8000
# Render / Railway / Fly 等は PORT を注入（ルート wsgi.py 経由で tools/revenue を読む）
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 wsgi:app"]
