# -*- coding: utf-8 -*-
import argparse
import os
import sys
import yaml
from auth import get_client_secrets_path, get_authenticated_service

def load_config():
    path = os.path.join(os.path.dirname(__file__), "config.yaml")
    if not os.path.exists(path):
        print("config.yaml がありません。config.example.yaml をコピーして config.yaml を作成してください。")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("account_id")
    parser.add_argument("--client-secrets", default=None)
    args = parser.parse_args()
    account_id = args.account_id.strip().lower()
    if not account_id.startswith("account_"):
        account_id = "account_" + account_id.replace("account_", "")
    root = os.path.dirname(os.path.abspath(__file__))
    account_dir = os.path.join(root, "accounts", account_id)
    config = load_config()
    client_secrets = args.client_secrets or get_client_secrets_path(account_id, config)
    client_secrets = os.path.join(root, client_secrets) if not os.path.isabs(client_secrets) else client_secrets
    print("アカウントID:", account_id)
    print("ブラウザでログインし、権限を許可してください。")
    get_authenticated_service(account_dir, client_secrets)
    print("完了:", account_id)

if __name__ == "__main__":
    main()
