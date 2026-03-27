from __future__ import annotations

from io import BytesIO

import streamlit as st
from PIL import Image

from question_assets import (
    export_question_image,
    list_question_options,
    load_questions_from_gsheet,
    question_from_row,
    question_image_bytes,
)
from tarot_fortune import detect_theme, perform_reading
from gpt_fortune import perform_gpt_reading


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
        .tarot-card {
            padding: 20px;
            border-radius: 20px;
            background: linear-gradient(145deg, rgba(90, 50, 140, 0.4), rgba(40, 20, 80, 0.6));
            border: 2px solid rgba(241, 205, 125, 0.3);
            margin-bottom: 1rem;
            text-align: center;
        }
        .tarot-position {
            color: #f3cd82;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }
        .tarot-name {
            font-size: 1.4rem;
            font-weight: 800;
            color: #fff;
            margin-bottom: 0.2rem;
        }
        .tarot-orientation {
            font-size: 0.85rem;
            color: #c9b8e8;
            margin-bottom: 0.6rem;
        }
        .tarot-meaning {
            font-size: 0.95rem;
            line-height: 1.7;
            color: #e8e0f5;
        }
        .theme-badge {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            background: linear-gradient(135deg, #f5ca77, #cb8f37);
            color: #2a163f;
            font-weight: 700;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        .advice-card {
            padding: 22px 24px;
            border-radius: 22px;
            background: linear-gradient(145deg, rgba(255, 200, 100, 0.15), rgba(255, 180, 80, 0.08));
            border: 1px solid rgba(241, 205, 125, 0.35);
            margin-top: 1.2rem;
        }
        .advice-title {
            color: #f3cd82;
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .advice-text {
            font-size: 1.05rem;
            line-height: 1.9;
            color: #fff;
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

    df = load_questions_from_gsheet()
    if df.empty:
        st.warning("まだ相談は届いていません。")
        st.info("Google Forms から相談が届くと、ここに一覧表示されます。`最新の相談を反映` で再読込できます。")
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
            birth_line = f'<div class="meta">生年月日：あなた {you_birth or "—"} / お相手 {them_birth or "—"}</div>'
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

    # ==================== タロット鑑定セクション ====================
    st.markdown("---")
    st.header("🔮 タロット鑑定")
    st.caption("お悩みに対してタロットカードで鑑定します。画面録画で動画素材にできます。")

    # 鑑定対象の相談を選択
    fortune_col1, fortune_col2 = st.columns([1, 2])
    
    with fortune_col1:
        fortune_label = st.selectbox(
            "鑑定する相談を選択",
            labels,
            index=default_index,
            key="fortune_select"
        )
        fortune_id = id_map[fortune_label]
        fortune_row = df.loc[df["id"].astype(int) == fortune_id].iloc[0]
        fortune_data = question_from_row(fortune_row)
        
        # テーマ自動判定
        detected_theme = detect_theme(str(fortune_data.get("question", "")))
        st.markdown(f'<div class="theme-badge">テーマ: {detected_theme}</div>', unsafe_allow_html=True)
        
        st.markdown(
            f"""
            <div class="list-card">
                <div class="name">{fortune_data['display_name']}</div>
                <div class="question">{fortune_data['question']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        if st.button("🃏 この悩みを鑑定する", type="primary", use_container_width=True):
            st.session_state["tarot_reading"] = perform_reading(str(fortune_data.get("question", "")))
            st.session_state["tarot_for_id"] = fortune_id

    with fortune_col2:
        # 鑑定結果の表示
        if "tarot_reading" in st.session_state and st.session_state.get("tarot_for_id") == fortune_id:
            reading = st.session_state["tarot_reading"]
            
            st.markdown(f'<div class="theme-badge">🔮 {reading["theme"]} の鑑定結果</div>', unsafe_allow_html=True)
            
            # カード3枚を横並びで表示
            card_cols = st.columns(3)
            for i, card in enumerate(reading["cards"]):
                with card_cols[i]:
                    st.markdown(
                        f"""
                        <div class="tarot-card">
                            <div class="tarot-position">{card['position']}</div>
                            <div class="tarot-name">{card['card_name_jp']}</div>
                            <div class="tarot-orientation">{card['orientation']}</div>
                            <div class="tarot-meaning">{card['meaning']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            
            # 総合アドバイス
            st.markdown(
                f"""
                <div class="advice-card">
                    <div class="advice-title">✨ 総合アドバイス</div>
                    <div class="advice-text">{reading['overall_advice']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            # 再鑑定ボタン
            if st.button("🔄 もう一度カードを引く", use_container_width=True):
                st.session_state["tarot_reading"] = perform_reading(str(fortune_data.get("question", "")))
                st.rerun()
        else:
            st.info("左の「この悩みを鑑定する」ボタンを押すと、タロットカードで鑑定結果が表示されます。")

    # ==================== GPT鑑定セクション ====================
    st.markdown("---")
    st.header("🤖 GPT鑑定（AI占い師）")
    st.caption("GPTsと同じプロンプトで、AIが本格的な恋愛鑑定を行います。画面録画で動画素材に。")

    # APIキー入力
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="OpenAI APIキーを入力してください。入力内容は保存されません。",
        key="openai_api_key"
    )

    gpt_col1, gpt_col2 = st.columns([1, 2])

    with gpt_col1:
        gpt_label = st.selectbox(
            "GPT鑑定する相談を選択",
            labels,
            index=default_index,
            key="gpt_select"
        )
        gpt_id = id_map[gpt_label]
        gpt_row = df.loc[df["id"].astype(int) == gpt_id].iloc[0]
        gpt_data = question_from_row(gpt_row)
        
        # テーマ自動判定
        gpt_theme = detect_theme(str(gpt_data.get("question", "")))
        st.markdown(f'<div class="theme-badge">テーマ: {gpt_theme}</div>', unsafe_allow_html=True)
        
        st.markdown(
            f"""
            <div class="list-card">
                <div class="name">{gpt_data['display_name']}</div>
                <div class="question">{gpt_data['question']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # モデル選択
        gpt_model = st.selectbox(
            "使用モデル",
            ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
            index=0,
            help="gpt-4o-miniが最もコスパ良。gpt-4oは高品質だがコスト高。"
        )
        
        if st.button("🔮 GPTで鑑定する", type="primary", use_container_width=True, disabled=not api_key):
            if not api_key:
                st.error("APIキーを入力してください。")
            else:
                with st.spinner("GPTが鑑定中... ✨"):
                    try:
                        result = perform_gpt_reading(
                            api_key=api_key,
                            question=str(gpt_data.get("question", "")),
                            theme=gpt_theme,
                            model=gpt_model
                        )
                        st.session_state["gpt_reading"] = result
                        st.session_state["gpt_for_id"] = gpt_id
                        st.rerun()
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
        
        if not api_key:
            st.warning("APIキーを入力すると鑑定できます。")

    with gpt_col2:
        # GPT鑑定結果の表示
        if "gpt_reading" in st.session_state and st.session_state.get("gpt_for_id") == gpt_id:
            result = st.session_state["gpt_reading"]
            
            st.markdown(f'<div class="theme-badge">🔮 {result["theme"]} のGPT鑑定結果</div>', unsafe_allow_html=True)
            
            # 引いたカード情報
            main_card = result["main_card"]
            st.markdown(
                f"""
                <div class="tarot-card" style="text-align: left;">
                    <div class="tarot-position">本鑑定カード</div>
                    <div class="tarot-name">{main_card['name_jp']}</div>
                    <div class="tarot-meaning">{main_card['meaning']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            # おまけ鑑定カード
            st.markdown("**おまけ鑑定カード（過去・現在・未来）**")
            sub_cols = st.columns(3)
            for i, (pos, card) in enumerate(zip(["過去", "現在", "未来"], result["sub_cards"])):
                with sub_cols[i]:
                    st.markdown(
                        f"""
                        <div class="tarot-card" style="padding: 12px;">
                            <div class="tarot-position">{pos}</div>
                            <div class="tarot-name" style="font-size: 1rem;">{card['name_jp']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            
            # 鑑定結果テキスト
            st.markdown("---")
            st.markdown(result["reading"])
            
            # トークン使用量
            usage = result.get("usage", {})
            st.caption(f"使用トークン: {usage.get('total_tokens', 'N/A')} tokens（モデル: {result.get('model', 'N/A')}）")
            
            # 再鑑定ボタン
            if st.button("🔄 もう一度GPT鑑定する", use_container_width=True):
                with st.spinner("GPTが鑑定中... ✨"):
                    try:
                        result = perform_gpt_reading(
                            api_key=api_key,
                            question=str(gpt_data.get("question", "")),
                            theme=gpt_theme,
                            model=gpt_model
                        )
                        st.session_state["gpt_reading"] = result
                        st.rerun()
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
        else:
            st.info("左の「GPTで鑑定する」ボタンを押すと、AIが本格的な鑑定結果を生成します。")


main()

