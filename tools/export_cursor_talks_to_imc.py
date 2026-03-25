from __future__ import annotations

import datetime as dt
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TranscriptFile:
    uuid: str
    jsonl_path: Path
    mtime: dt.datetime
    title: str


def _projects_dir() -> Path:
    user = os.environ.get("USERPROFILE")
    if not user:
        raise SystemExit("USERPROFILE が見つかりません。")
    return Path(user) / ".cursor" / "projects"


def _imc_root() -> Path:
    user = os.environ.get("USERPROFILE")
    if not user:
        raise SystemExit("USERPROFILE が見つかりません。")
    return Path(user) / "OneDrive" / "IMC"


def _iter_jsonl_files(projects_dir: Path) -> Iterable[Path]:
    yield from projects_dir.glob("**/agent-transcripts/*/*.jsonl")
    yield from projects_dir.glob("**/agent-transcripts-archived/*/*.jsonl")


def _extract_title(jsonl_path: Path) -> str:
    try:
        with jsonl_path.open("r", encoding="utf-8") as f:
            for _ in range(50):
                line = f.readline()
                if not line:
                    break
                obj = json.loads(line)
                if obj.get("role") != "user":
                    continue
                content = obj.get("message", {}).get("content", [])
                if not isinstance(content, list):
                    continue
                for part in content:
                    if part.get("type") != "text":
                        continue
                    text = part.get("text", "")
                    if not isinstance(text, str):
                        continue
                    start = text.find("<user_query>")
                    end = text.find("</user_query>")
                    if start != -1 and end != -1 and start < end:
                        q = text[start + len("<user_query>") : end].strip()
                        if q:
                            return q.replace("\n", " / ")
                break
    except Exception:
        pass
    return ""


def _collect() -> list[TranscriptFile]:
    projects = _projects_dir()
    items: list[TranscriptFile] = []
    for p in _iter_jsonl_files(projects):
        uuid = p.stem
        mtime = dt.datetime.fromtimestamp(p.stat().st_mtime)
        title = _extract_title(p)
        items.append(TranscriptFile(uuid=uuid, jsonl_path=p, mtime=mtime, title=title))
    # 同じUUIDが active / archived に重複していても、新しい方を残す
    by_uuid: dict[str, TranscriptFile] = {}
    for t in items:
        cur = by_uuid.get(t.uuid)
        if cur is None or t.mtime > cur.mtime:
            by_uuid[t.uuid] = t
    result = list(by_uuid.values())
    result.sort(key=lambda x: x.mtime, reverse=True)
    return result


def main() -> int:
    projects = _projects_dir()
    imc = _imc_root()
    target_root = imc / "cursor-agent-transcripts"
    index_md = target_root / "index.md"

    if not projects.exists():
        raise SystemExit(f"projects ディレクトリが見つかりません: {projects}")
    if not imc.exists():
        raise SystemExit(f"IMC フォルダが見つかりません: {imc}")

    target_root.mkdir(parents=True, exist_ok=True)

    transcripts = _collect()
    print(f"エクスポート対象: {len(transcripts)} 件")

    lines_md: list[str] = [
        "# Cursor agent transcripts",
        "",
        f"- Exported at: {dt.datetime.now().isoformat(timespec='seconds')}",
        "",
        "| # | Date | UUID | Title | Source |",
        "|---|------|------|-------|--------|",
    ]

    for i, t in enumerate(transcripts, start=1):
        date_str = t.mtime.strftime("%Y-%m-%d_%H-%M-%S")
        dst_dir = target_root / t.uuid
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst_file = dst_dir / f"{date_str}__{t.uuid}.jsonl"

        # すでに同じ内容がある場合は上書きでOK（最新を優先）
        shutil.copy2(t.jsonl_path, dst_file)
        rel_src = t.jsonl_path.as_posix().replace(os.environ.get("USERPROFILE", ""), "~")
        safe_title = t.title.replace("|", "｜") if t.title else ""
        lines_md.append(
            f"| {i} | {t.mtime.strftime('%Y-%m-%d %H:%M')} | `{t.uuid}` | {safe_title} | `{rel_src}` |"
        )

    index_md.write_text("\n".join(lines_md), encoding="utf-8")
    print(f"保存先: {target_root}")
    print(f"一覧:   {index_md}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

