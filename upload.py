# -*- coding: utf-8 -*-
import os
from googleapiclient.http import MediaFileUpload

def ensure_shorts_title(title: str, auto_append: bool = True) -> str:
    if not auto_append:
        return title
    if "#Shorts" in title or "#shorts" in title:
        return title
    return f"{title} #Shorts"

def upload_video(youtube, file_path: str, title: str, description: str = "", tags: list = None, category_id: str = "22", privacy_status: str = "private", publish_at: str = None, auto_append_shorts_tag: bool = True):
    title = ensure_shorts_title(title, auto_append_shorts_tag)
    tags = tags or []
    # 予約投稿時は YouTube の仕様で必ず「非公開」にする（指定時刻に自動で公開される）
    if publish_at:
        privacy_status = "private"
    body = {"snippet": {"title": title, "description": description or "", "tags": tags, "categoryId": category_id}, "status": {"privacyStatus": privacy_status, "selfDeclaredMadeForKids": False}}
    if publish_at:
        body["status"]["publishAt"] = publish_at
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  アップロード進捗: {int(status.progress() * 100)}%")
    print(f"  完了 動画ID: {response.get('id')}")
    return response
