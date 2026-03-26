from __future__ import annotations

import io
import math
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
QUESTIONS_CSV = ROOT / "questions_box.csv"
EXPORT_DIR = ROOT / "exports" / "question_images"

# Google Sheets 公開CSV URL（お悩み相談データ）
GOOGLE_SHEET_ID = "18-_rNCncpt2LbvxZ-auHmnvNPHUyn9n9F37x42_eQwk"
GOOGLE_SHEET_GID = "1908512133"
GOOGLE_SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=csv&gid={GOOGLE_SHEET_GID}"

COLUMNS = [
    "id",
    "display_name",
    "reply_to",
    "avatar",
    "you_birth",
    "them_birth",
    "question",
    "created_at",
]

# Google Forms の列名 → 内部列名 のマッピング
GFORM_COLUMN_MAP = {
    "タイムスタンプ": "created_at",
    "名前（偽名でもOK）": "display_name",
    "自分の生年月日（8桁）": "you_birth",
    "相手の生年月日（8桁・不明なら空欄）": "them_birth",
    "悩み": "question",
}

DEFAULT_QUESTION = {
    "id": 0,
    "display_name": "月野ルナ",
    "reply_to": "月野ルナに届いた恋のおたより",
    "avatar": "",
    "you_birth": "",
    "them_birth": "",
    "question": "好きな人から連絡が来ません。\nもう諦めた方がいいですか？",
    "created_at": "",
}

FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/YuGothB.ttc"),
    Path("C:/Windows/Fonts/YuGothM.ttc"),
    Path("C:/Windows/Fonts/meiryob.ttc"),
    Path("C:/Windows/Fonts/msgothic.ttc"),
]


def load_questions() -> pd.DataFrame:
    """ローカルCSVから読み込む（旧方式・フォールバック用）"""
    if not QUESTIONS_CSV.exists():
        return pd.DataFrame(columns=COLUMNS)
    df = pd.read_csv(QUESTIONS_CSV)
    for column in COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[COLUMNS]


def load_questions_from_gsheet() -> pd.DataFrame:
    """Google Sheets（Forms連携）からデータを読み込む"""
    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
    except Exception as e:
        print(f"[WARN] Google Sheets 読み込み失敗: {e}")
        return pd.DataFrame(columns=COLUMNS)

    # 列名を内部形式にリネーム
    df = df.rename(columns=GFORM_COLUMN_MAP)

    # 必要な列がなければ追加
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # id列を自動生成（行番号ベース）
    df["id"] = range(1, len(df) + 1)

    # 不要な列を除外して返す
    return df[COLUMNS]


def save_questions(df: pd.DataFrame) -> None:
    df.to_csv(QUESTIONS_CSV, index=False)


def create_question(
    display_name: str,
    reply_to: str,
    avatar: str,
    question: str,
    you_birth: str = "",
    them_birth: str = "",
) -> dict[str, str | int]:
    df = load_questions()
    now = datetime.now().isoformat(timespec="seconds")
    cleaned_name = display_name.strip() or "匿名さん"
    new_row = {
        "id": 1 if df.empty else int(df["id"].max()) + 1,
        "display_name": cleaned_name,
        "reply_to": reply_to.strip() or f"{cleaned_name}に届いた恋のおたより",
        "avatar": avatar.strip(),
        "you_birth": str(you_birth).strip(),
        "them_birth": str(them_birth).strip(),
        "question": question.strip(),
        "created_at": now,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_questions(df)
    return new_row


def question_from_row(row: pd.Series) -> dict[str, str | int]:
    return {
        "id": int(row["id"]),
        "display_name": str(row["display_name"]),
        "reply_to": str(row["reply_to"]),
        "avatar": str(row["avatar"]),
        "you_birth": str(row.get("you_birth", "")),
        "them_birth": str(row.get("them_birth", "")),
        "question": str(row["question"]),
        "created_at": str(row["created_at"]),
    }


def list_question_options(df: pd.DataFrame) -> list[tuple[str, int]]:
    return [
        (f"#{int(row['id'])} {str(row['question']).replace(chr(10), ' ')[:30]}", int(row["id"]))
        for _, row in df.iloc[::-1].iterrows()
    ]


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def _measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    wrapped_lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        if not paragraph:
            wrapped_lines.append("")
            continue
        current = ""
        for char in paragraph:
            candidate = f"{current}{char}"
            if current and _measure(draw, candidate, font) > max_width:
                wrapped_lines.append(current)
                current = char
            else:
                current = candidate
        if current:
            wrapped_lines.append(current)
    return wrapped_lines or [text]


def _draw_star(draw: ImageDraw.ImageDraw, center: tuple[float, float], radius: float, fill: tuple[int, int, int, int]) -> None:
    cx, cy = center
    points: list[tuple[float, float]] = []
    for index in range(8):
        angle = math.pi / 4 * index
        current_radius = radius if index % 2 == 0 else radius * 0.42
        points.append((cx + math.cos(angle) * current_radius, cy + math.sin(angle) * current_radius))
    draw.polygon(points, fill=fill)


def _draw_crescent(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    draw.ellipse(box, fill=(255, 238, 205, 255))
    offset = 34
    x1, y1, x2, y2 = box
    draw.ellipse((x1 + offset, y1 - 10, x2 + offset, y2 - 10), fill=(34, 20, 68, 235))


def _draw_name_emblem(draw: ImageDraw.ImageDraw, center: tuple[int, int], text: str, font: ImageFont.ImageFont) -> None:
    cx, cy = center
    draw.ellipse((cx - 52, cy - 52, cx + 52, cy + 52), fill=(68, 40, 115, 255), outline=(238, 201, 125, 255), width=3)
    _draw_star(draw, (cx, cy), 16, (247, 214, 144, 255))
    initial = text[:1] if text else "恋"
    bbox = draw.textbbox((0, 0), initial, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text((cx - text_w / 2, cy + 20 - text_h / 2), initial, font=font, fill=(255, 239, 213, 255))


def render_question_image(question_data: dict[str, str | int], size: tuple[int, int] = (1920, 1080)) -> Image.Image:
    base_w, base_h = 1080, 1920
    width, height = size
    sx = width / base_w
    sy = height / base_h
    s_font = sy
    s_geom = min(sx, sy)

    base = Image.new("RGBA", size, (18, 11, 44, 255))
    draw = ImageDraw.Draw(base)

    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = (int(17 + 23 * ratio), int(10 + 7 * ratio), int(42 + 34 * ratio), 255)
        draw.line((0, y, width, y), fill=color)

    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((width - int(410 * sx), int(70 * sy), width - int(50 * sx), int(430 * sy)), fill=(255, 216, 151, 120))
    glow_draw.ellipse((int(30 * sx), int(1380 * sy), int(440 * sx), int(1800 * sy)), fill=(118, 74, 255, 80))
    glow_draw.ellipse((int(710 * sx), int(1180 * sy), int(1090 * sx), int(1600 * sy)), fill=(255, 168, 96, 32))
    glow = glow.filter(ImageFilter.GaussianBlur(int(42 * s_geom)))
    base.alpha_composite(glow)

    _draw_crescent(draw, (int(width - 305 * sx), int(120 * sy), int(width - 125 * sx), int(300 * sy)))

    for x_pos, y_pos, radius in [(120, 160, 18), (220, 280, 12), (410, 145, 14), (590, 245, 10), (845, 410, 12), (180, 590, 10), (965, 810, 16)]:
        _draw_star(draw, (int(x_pos * sx), int(y_pos * sy)), int(radius * s_geom), (251, 220, 151, 230))

    card = (int(82 * sx), int(238 * sy), int(width - 82 * sx), int(height - 126 * sy))
    draw.rounded_rectangle(card, radius=int(48 * s_geom), fill=(70, 42, 119, 218), outline=(233, 198, 126, 255), width=max(1, int(4 * s_geom)))

    badge_box = (int(124 * sx), int(284 * sy), int(width - 124 * sx), int(432 * sy))
    draw.rounded_rectangle(badge_box, radius=int(30 * s_geom), fill=(255, 246, 230, 240), outline=(239, 202, 127, 255), width=max(1, int(3 * s_geom)))

    badge_font = _get_font(max(10, int(30 * s_font)))
    name_font = _get_font(max(14, int(60 * s_font)))
    mark_font = _get_font(max(10, int(30 * s_font)))
    question_font = _get_font(max(12, int(64 * s_font)))
    initial_font = _get_font(max(10, int(34 * s_font)))

    display_name = str(question_data.get("display_name") or DEFAULT_QUESTION["display_name"])
    question = str(question_data.get("question") or DEFAULT_QUESTION["question"])

    draw.text((int(154 * sx), int(318 * sy)), "LOVE MESSAGE", font=badge_font, fill=(123, 88, 38, 255))
    _draw_name_emblem(draw, (int(184 * sx), int(544 * sy)), display_name, initial_font)
    draw.text((int(265 * sx), int(505 * sy)), "相談者", font=mark_font, fill=(245, 206, 125, 255))
    draw.text((int(265 * sx), int(548 * sy)), display_name, font=name_font, fill=(255, 238, 210, 255))

    bubble = (int(118 * sx), int(690 * sy), int(width - 118 * sx), int(1445 * sy))
    draw.rounded_rectangle(bubble, radius=int(38 * s_geom), fill=(252, 248, 255, 246), outline=(237, 201, 126, 255), width=max(1, int(3 * s_geom)))

    max_text_width = (bubble[2] - bubble[0]) - int(110 * sx)
    lines = _wrap_text(draw, question, question_font, max_text_width)[:6]
    line_height = max(18, int(88 * sy))
    total_height = max(len(lines), 1) * line_height
    current_y = bubble[1] + max((bubble[3] - bubble[1] - total_height) // 2, int(42 * sy))
    for line in lines:
        text_width = _measure(draw, line, question_font)
        current_x = bubble[0] + (bubble[2] - bubble[0] - text_width) / 2
        draw.text((current_x, current_y), line, font=question_font, fill=(38, 28, 61, 255))
        current_y += line_height

    return base.convert("RGB")


def question_image_bytes(question_data: dict[str, str | int], size: tuple[int, int] = (1920, 1080)) -> bytes:
    image = render_question_image(question_data, size=size)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def export_question_image(question_data: dict[str, str | int], size: tuple[int, int] = (1920, 1080)) -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    question_id = int(question_data.get("id", 0) or 0)
    display_name = str(question_data.get("display_name") or "question")
    safe_name = re.sub(r"[^0-9A-Za-z_\-一-龠ぁ-んァ-ヶー]+", "_", display_name).strip("_") or "question"
    file_path = EXPORT_DIR / f"question_{question_id:03d}_{safe_name}.png"
    render_question_image(question_data, size=size).save(file_path, format="PNG")
    return file_path

