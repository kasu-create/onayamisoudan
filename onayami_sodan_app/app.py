from __future__ import annotations

import re

import streamlit as st

from question_assets import create_question, load_questions


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 15% 10%, rgba(255, 217, 137, 0.16), transparent 18%),
                radial-gradient(circle at 85% 85%, rgba(122, 81, 255, 0.18), transparent 28%),
                linear-gradient(180deg, #110924 0%, #1a1036 44%, #22124a 100%);
            color: #fbf5ff;
        }
        .block-container {
            max-width: 1160px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        h1, h2, h3, label, p, li, div, span {
            font-family: "Yu Gothic UI", "Hiragino Sans", sans-serif;
        }
        .hero {
            padding: 34px 34px 30px;
            border-radius: 32px;
            border: 1px solid rgba(241, 205, 125, 0.24);
            background:
                radial-gradient(circle at top right, rgba(255,255,255,0.06), transparent 22%),
                linear-gradient(140deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
            box-shadow: 0 28px 70px rgba(7, 2, 29, 0.42);
            margin-bottom: 1.4rem;
        }
        .hero-title {
            font-size: 2.45rem;
            line-height: 1.2;
            font-weight: 800;
            margin-bottom: 0.8rem;
        }
        .hero-copy {
            color: #ddd1f2;
            line-height: 1.9;
            font-size: 1rem;
            max-width: 700px;
        }
        /* 余白が原因の「謎の空白」を減らす */
        .stMarkdown p { margin: 0.20rem 0 0.35rem 0; }
        .stMarkdown { margin-bottom: 0.18rem; }
        .stTextInput, .stTextArea { margin-top: 0.10rem; }
        .form-shell {
            max-width: 760px;
            margin: 0 auto 1.5rem;
        }
        .soft-card {
            padding: 28px 28px 26px;
            border-radius: 32px;
            background:
                radial-gradient(circle at top right, rgba(255,255,255,0.05), transparent 28%),
                rgba(255,255,255,0.045);
            border: 1px solid rgba(241, 205, 125, 0.18);
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
        }
        .soft-card .form-title { margin-bottom: 0.25rem; }
        .soft-card .form-copy { margin-bottom: 0.65rem; }
        .form-title {
            font-size: 1.95rem;
            font-weight: 800;
            line-height: 1.25;
            margin-bottom: 0.5rem;
        }
        .form-copy {
            color: #dbd0f2;
            font-size: 0.98rem;
            line-height: 1.85;
            margin-bottom: 1.2rem;
        }
        .stTextInput > div > div > input,
        .stTextArea textarea {
            background: rgba(12, 8, 33, 0.82) !important;
            color: #fff8ff !important;
            border: 1px solid rgba(239, 201, 118, 0.26) !important;
            border-radius: 16px !important;
        }
        .stTextArea textarea {
            min-height: 220px !important;
            line-height: 1.85 !important;
        }
        .stButton > button {
            border-radius: 999px !important;
            border: 1px solid rgba(243, 206, 122, 0.58) !important;
            background: linear-gradient(135deg, #f5ca77, #cb8f37) !important;
            color: #2a163f !important;
            font-weight: 800 !important;
            padding: 0.72rem 1.2rem !important;
        }
        .stAlert {
            border-radius: 18px;
        }
        .mini-note {
            margin-top: 1rem;
            color: #d8cdef;
            font-size: 0.94rem;
            line-height: 1.8;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def normalize_birth(value: str) -> str:
    raw = (value or "").strip()
    return re.sub(r"[^0-9]", "", raw)


def main() -> None:
    st.set_page_config(page_title="お悩み相談フォーム", page_icon="🌙", layout="wide")
    apply_theme()

    # 送信後のクリアは「次のrerunの最初」に行う（widget生成後に session_state を触るとStreamlit例外になるため）
    if st.session_state.get("_clear_form_once") is True:
        for key in ("form_name", "form_you_birth", "form_them_birth", "form_question"):
            st.session_state[key] = ""
        st.session_state["_clear_form_once"] = False

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">そのまま書いてください。</div>
            <div class="hero-copy">
                返信が来ない不安も、気持ちが読めない切なさも、そのままで大丈夫です。<br>
                下のフォームに「名前 / 自分の生年月日（8桁）/ 相手の生年月日（8桁・不明なら空欄）/ 悩み」を順番に入力して、最後に送信してください。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _ = load_questions()
    st.markdown('<div class="form-shell">', unsafe_allow_html=True)
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="form-title">お悩み相談フォーム</div>
        <div class="form-copy">
            どこに何を書くか（例）<br>
            ① 名前：月子（偽名OK）<br>
            ② 自分の生年月日：19990101（8桁）<br>
            ③ 相手の生年月日：不明なら空欄<br>
            ④ 悩み：いま困っていることを、そのまま文章で
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("question_form", clear_on_submit=False):
        st.markdown("**名前（偽名でもOK）**  ニックネームでOK。動画で読み上げられても困らない名前にしてね。")
        name = st.text_input(
            label="名前（偽名でもOK）",
            placeholder="例：月子",
            label_visibility="collapsed",
            key="form_name",
        )

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**自分の生年月日（8桁）**  `YYYYMMDD`（例：19990101）")
            you_birth = st.text_input(
                label="自分の生年月日（8桁）",
                placeholder="例：19990101",
                label_visibility="collapsed",
                key="form_you_birth",
            )
        with col_b:
            st.markdown("**相手の生年月日（8桁・不明なら空欄）**  `YYYYMMDD`（例：20001231）")
            them_birth = st.text_input(
                label="相手の生年月日（8桁・不明なら空欄）",
                placeholder="不明なら空欄",
                label_visibility="collapsed",
                key="form_them_birth",
            )

        st.markdown("**悩み**  状況（いつから/何があった）と、知りたいこと（どうしたいか）を書いてください。")
        question = st.text_area(
            label="悩み",
            placeholder="例：好きな人から急に返信が減りました。嫌われたのか不安です。どうしたらいいですか？",
            height=320,
            label_visibility="collapsed",
            key="form_question",
        )

        submitted = st.form_submit_button("送信する", type="primary", use_container_width=True)
        if submitted:
            if not question.strip():
                st.error("「悩み」を入力してください。")
            else:
                you_birth_norm = normalize_birth(you_birth)
                them_birth_norm = normalize_birth(them_birth)

                if you_birth_norm and not re.fullmatch(r"\d{8}", you_birth_norm):
                    st.error("「自分の生年月日」は8桁（YYYYMMDD）で入力してください。例：19990101")
                    st.stop()
                if them_birth_norm and not re.fullmatch(r"\d{8}", them_birth_norm):
                    st.error("「相手の生年月日」は8桁（YYYYMMDD）で入力してください。例：20001231（不明なら空欄でOK）")
                    st.stop()

                create_question(
                    name,
                    "",
                    "",
                    question,
                    you_birth=you_birth_norm,
                    them_birth=them_birth_norm,
                )
                st.success("送信しました。ありがとうございます。")
                st.session_state["_clear_form_once"] = True
                st.rerun()

    st.markdown(
        """
        <div class="mini-note">
            少し崩れた言い回しでも、そのまま送って大丈夫です。<br>
            送っていただいた相談内容は、恋愛相談の動画コンテンツとして使用する場合があります。
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


main()

