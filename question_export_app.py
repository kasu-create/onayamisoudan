from __future__ import annotations

from io import BytesIO

import streamlit as st
from PIL import Image

from question_assets import export_question_image, list_question_options, load_questions, question_image_bytes, question_from_row


def preview_image(png_bytes: bytes) -> Image.Image:
    return Image.open(BytesIO(png_bytes))


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #120a27 0%, #1d1140 100%);
            color: #faf6ff;
        }
        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .summary-card {
            padding: 18px 20px;
            border-radius: 22px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(241, 205, 125, 0.18);
            margin-bottom: 1rem;
        }
        .list-card {
            padding: 18px 20px;
            border-radius: 22px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(241, 205, 125, 0.14);
            margin-bottom: 0.9rem;
        }
        .meta {
            color: #f3cd82;
            font-size: 0.82rem;
            margin-bottom: 0.35rem;
        }
        .name {
            font-size: 1.08rem;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }
        .question {
            white-space: pre-wrap;
            line-height: 1.85;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="お悩み相談 管理画面", page_icon="🖼️", layout="wide")
    apply_theme()
    st.title("お悩み相談 管理画面")
    st.caption("届いた相談を確認し、そのまま動画素材として保存できます。")

    top_left, _ = st.columns([1, 4])
    with top_left:
        if st.button("最新の相談を反映", use_container_width=True):
            st.rerun()

    df = load_questions()
    if df.empty:
        st.warning("まだ相談は保存されていません。現在の `questions_box.csv` は空です。")
        st.info("先に `http://localhost:8501` 側で相談を追加してください。追加後にこの画面で `最新の相談を反映` を押すと一覧に出ます。")
        return

    st.markdown(
        f"""
        <div class="summary-card">
            <div class="meta">TOTAL</div>
            <div class="name">{len(df)}件の相談があります</div>
            <div class="question">最新の相談から順に確認できます。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.02, 0.98], gap="large")
    options = list_question_options(df)
    labels = [label for label, _ in options]
    id_map = {label: question_id for label, question_id in options}

    with left_col:
        st.subheader("届いた相談")
        for _, row in df.iloc[::-1].iterrows():
            row_id = int(row["id"])
            if st.button(f"#{row_id} {row['display_name']}", key=f"pick_{row_id}", use_container_width=True):
                st.session_state["selected_export_id"] = row_id
            st.markdown(
                f"""
                <div class="list-card">
                    <div class="meta">{row['created_at']}</div>
                    <div class="name">{row['display_name']}</div>
                    <div class="question">{row['question']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right_col:
        st.subheader("素材書き出し")
        default_index = 0
        if "selected_export_id" in st.session_state:
            for index, (_, question_id) in enumerate(options):
                if question_id == st.session_state["selected_export_id"]:
                    default_index = index
                    break
        selected_label = st.selectbox("対象の相談", labels, index=default_index)
        selected_id = id_map[selected_label]
        st.session_state["selected_export_id"] = selected_id

        row = df.loc[df["id"].astype(int) == selected_id].iloc[0]
        question_data = question_from_row(row)
        png_bytes = question_image_bytes(question_data)

        st.image(preview_image(png_bytes), use_container_width=True)
        you_birth = str(question_data.get("you_birth") or "").strip()
        them_birth = str(question_data.get("them_birth") or "").strip()
        birth_line = ""
        if you_birth or them_birth:
            birth_line = f"<div class=\"meta\">生年月日：あなた {you_birth or '—'} / お相手 {them_birth or '—'}</div>"
        st.markdown(
            f"""
            <div class="summary-card">
                {birth_line}
                <div class="name">{question_data['display_name']}</div>
                <div class="question">{question_data['question']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.download_button(
            "この相談をPNGで保存",
            data=png_bytes,
            file_name=f"question_{selected_id:03d}.png",
            mime="image/png",
            use_container_width=True,
        )

        if st.button("プロジェクト内にも保存する", use_container_width=True):
            output = export_question_image(question_data)
            st.success(f"保存しました: {output}")

        st.markdown("---")
        if st.button("すべての相談をPNG素材として保存", type="primary", use_container_width=True):
            outputs = []
            for _, export_row in df.iterrows():
                outputs.append(export_question_image(question_from_row(export_row)))
            st.success(f"{len(outputs)}件を書き出しました。保存先: {outputs[0].parent}")


if __name__ == "__main__":
    main()
