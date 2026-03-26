"""タロット鑑定モジュール - 無料APIを使って恋愛相談の鑑定を行う"""
from __future__ import annotations

import random
import re
from typing import Any

import requests

# タロットカードAPI（無料）
TAROT_API_URL = "https://tarotapi.dev/api/v1/cards"

# 恋愛テーマの自動判定キーワード
THEME_KEYWORDS = {
    "片思い": ["片思い", "好きな人", "気になる人", "アプローチ", "両想い"],
    "告白のタイミング": ["告白", "伝える", "脈あり", "脈なし", "タイミング"],
    "嫉妬・不安": ["嫉妬", "不安", "心配", "浮気", "信じられない", "怖い"],
    "友達以上恋人未満": ["友達以上", "曖昧", "付き合う前", "微妙な関係", "キープ"],
    "年の差恋愛": ["年の差", "年上", "年下", "歳上", "歳下", "世代"],
    "両思い・交際中": ["彼氏", "彼女", "付き合って", "交際", "カップル", "デート", "記念日"],
    "復縁": ["復縁", "元カレ", "元カノ", "別れた", "やり直し", "戻りたい", "未練"],
    "音信不通": ["音信不通", "連絡こない", "ブロック", "既読無視", "未読無視"],
    "返信がそっけない": ["そっけない", "冷たい", "返信", "テンション", "温度差"],
    "結婚": ["結婚", "プロポーズ", "婚約", "入籍", "将来", "同棲"],
    "複雑恋愛": ["不倫", "既婚", "二股", "秘密", "三角関係"],
    "遠距離恋愛": ["遠距離", "会えない", "距離", "転勤", "留学"],
    "既婚者の恋": ["既婚者", "不倫相手", "奥さん", "旦那さん", "離婚"],
    "失恋・別れ": ["失恋", "振られた", "別れ", "忘れられない", "辛い"],
    "出会い": ["出会い", "恋人がほしい", "モテない", "恋愛運"],
    "連絡・LINE": ["連絡", "LINE", "既読", "未読"],
}

# タロットカードの恋愛向け解釈（主要カード）
LOVE_INTERPRETATIONS = {
    "The Fool": {
        "name": "愚者",
        "upright": "新しい恋の始まり。勇気を出して一歩踏み出すとき。直感を信じて。",
        "reversed": "無計画な行動は避けて。焦らず状況を見極めることが大切。",
    },
    "The Magician": {
        "name": "魔術師",
        "upright": "あなたには恋を叶える力がある。積極的にアプローチを。",
        "reversed": "自信過剰に注意。相手の気持ちも大切に。",
    },
    "The High Priestess": {
        "name": "女教皇",
        "upright": "直感を信じて。隠された真実が明らかになる時。",
        "reversed": "秘密や隠し事に注意。本心を見極めて。",
    },
    "The Empress": {
        "name": "女帝",
        "upright": "愛情に満ちた時期。魅力が高まり、恋愛運上昇。",
        "reversed": "依存しすぎないで。自分の時間も大切に。",
    },
    "The Emperor": {
        "name": "皇帝",
        "upright": "安定した関係が築ける。頼れる存在との出会いも。",
        "reversed": "支配的にならないで。対等な関係を意識して。",
    },
    "The Lovers": {
        "name": "恋人",
        "upright": "運命的な出会い・恋愛成就の暗示。相思相愛へ。",
        "reversed": "価値観の違いに注意。コミュニケーションを大切に。",
    },
    "The Chariot": {
        "name": "戦車",
        "upright": "積極的な行動が吉。困難を乗り越え恋を勝ち取る。",
        "reversed": "焦りは禁物。暴走せず冷静に。",
    },
    "Strength": {
        "name": "力",
        "upright": "忍耐が実を結ぶ。優しさで相手の心を開く。",
        "reversed": "自信をなくさないで。あなたの魅力を信じて。",
    },
    "The Hermit": {
        "name": "隠者",
        "upright": "一人の時間で自分を見つめ直すとき。焦らなくていい。",
        "reversed": "孤立しすぎないで。周りの人を頼って。",
    },
    "Wheel of Fortune": {
        "name": "運命の輪",
        "upright": "転機の訪れ。運命が動き出す。チャンスを逃さないで。",
        "reversed": "停滞期。でも必ず好転する。今は準備の時。",
    },
    "Justice": {
        "name": "正義",
        "upright": "誠実な対応が吉。公平な関係が築ける。",
        "reversed": "不公平さを感じているなら声に出して。",
    },
    "The Hanged Man": {
        "name": "吊るされた男",
        "upright": "待つことで状況が変わる。視点を変えてみて。",
        "reversed": "無駄な我慢はやめて。行動するタイミング。",
    },
    "Death": {
        "name": "死神",
        "upright": "終わりは新しい始まり。過去を手放して前へ。",
        "reversed": "変化を恐れないで。執着を捨てると道が開ける。",
    },
    "Temperance": {
        "name": "節制",
        "upright": "バランスの取れた関係が築ける。穏やかな愛。",
        "reversed": "感情の波に注意。冷静さを保って。",
    },
    "The Devil": {
        "name": "悪魔",
        "upright": "情熱的な恋。ただし依存には注意。",
        "reversed": "束縛から解放される。自由な恋愛へ。",
    },
    "The Tower": {
        "name": "塔",
        "upright": "衝撃的な出来事。でもそれは必要な変化。",
        "reversed": "危機は回避できる。気づきを大切に。",
    },
    "The Star": {
        "name": "星",
        "upright": "希望の光が見える。願いは叶う方向へ。",
        "reversed": "自信を持って。あなたは愛される価値がある。",
    },
    "The Moon": {
        "name": "月",
        "upright": "不安や迷いがある時期。でも直感を信じて。",
        "reversed": "真実が明らかに。曖昧な関係に決着がつく。",
    },
    "The Sun": {
        "name": "太陽",
        "upright": "最高の恋愛運！幸福な未来が待っている。",
        "reversed": "少し曇りがあるけど基本的には良好。",
    },
    "Judgement": {
        "name": "審判",
        "upright": "過去の恋が蘇る可能性。復縁のチャンス。",
        "reversed": "過去に囚われすぎないで。新しい出会いへ。",
    },
    "The World": {
        "name": "世界",
        "upright": "恋愛成就！完全な幸福。理想の関係が手に入る。",
        "reversed": "もう少しで完成。最後まで諦めないで。",
    },
}

# デフォルトの解釈（APIから取得したカード用）
DEFAULT_INTERPRETATIONS = {
    "upright": "このカードは恋愛において前向きな変化を示しています。直感を信じて行動してみましょう。",
    "reversed": "慎重さが求められる時期。焦らず、相手の気持ちをよく観察してみて。",
}


def detect_theme(question_text: str) -> str:
    """悩みのテキストからテーマを自動判定"""
    question_lower = question_text.lower()
    
    for theme, keywords in THEME_KEYWORDS.items():
        for keyword in keywords:
            if keyword in question_lower:
                return theme
    
    return "恋愛全般"


def fetch_tarot_cards(count: int = 3) -> list[dict[str, Any]]:
    """タロットAPIからカードを取得（3枚引き）"""
    try:
        response = requests.get(f"{TAROT_API_URL}/random?n={count}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("cards", [])
    except Exception as e:
        print(f"[WARN] Tarot API error: {e}")
        # フォールバック: ローカルでランダム生成
        return _generate_fallback_cards(count)


def _generate_fallback_cards(count: int) -> list[dict[str, Any]]:
    """APIが使えない場合のフォールバック"""
    major_arcana = list(LOVE_INTERPRETATIONS.keys())
    selected = random.sample(major_arcana, min(count, len(major_arcana)))
    return [{"name": name, "name_short": name.lower().replace(" ", "_")} for name in selected]


def get_love_interpretation(card_name: str, is_reversed: bool = False) -> dict[str, str]:
    """カード名から恋愛向け解釈を取得"""
    if card_name in LOVE_INTERPRETATIONS:
        interp = LOVE_INTERPRETATIONS[card_name]
        return {
            "name_jp": interp["name"],
            "meaning": interp["reversed"] if is_reversed else interp["upright"],
        }
    
    # 未登録カードはデフォルト解釈
    return {
        "name_jp": card_name,
        "meaning": DEFAULT_INTERPRETATIONS["reversed"] if is_reversed else DEFAULT_INTERPRETATIONS["upright"],
    }


def perform_reading(question_text: str) -> dict[str, Any]:
    """タロット鑑定を実行（3枚引き: 過去・現在・未来）"""
    theme = detect_theme(question_text)
    cards = fetch_tarot_cards(3)
    
    positions = ["過去", "現在", "未来"]
    reading_results = []
    
    for i, card in enumerate(cards):
        card_name = card.get("name", "Unknown")
        is_reversed = random.choice([True, False])  # 正位置/逆位置をランダム決定
        interpretation = get_love_interpretation(card_name, is_reversed)
        
        reading_results.append({
            "position": positions[i] if i < len(positions) else f"カード{i+1}",
            "card_name": card_name,
            "card_name_jp": interpretation["name_jp"],
            "is_reversed": is_reversed,
            "orientation": "逆位置" if is_reversed else "正位置",
            "meaning": interpretation["meaning"],
            "image_url": f"https://www.sacred-texts.com/tarot/pkt/img/{card.get('name_short', 'ar00')}.jpg",
        })
    
    # 総合アドバイスを生成
    overall_advice = _generate_overall_advice(theme, reading_results)
    
    return {
        "theme": theme,
        "cards": reading_results,
        "overall_advice": overall_advice,
    }


def _generate_overall_advice(theme: str, cards: list[dict]) -> str:
    """総合アドバイスを生成"""
    future_card = cards[-1] if cards else None
    
    if not future_card:
        return "カードがあなたの恋を応援しています。"
    
    # 未来のカードがポジティブかどうかで分岐
    positive_cards = ["The Sun", "The Star", "The World", "The Lovers", "The Empress", "Wheel of Fortune"]
    is_positive = future_card["card_name"] in positive_cards and not future_card["is_reversed"]
    
    # テーマ別アドバイス
    theme_advice = {
        "片思い": {
            True: "あなたの想いは届く可能性が高いです。勇気を出して一歩踏み出してみて。相手もあなたのことを意識しているかもしれません。",
            False: "今は焦らず、相手との距離を縮める時期。友達としての関係を深めながら、自然なタイミングを待ちましょう。"
        },
        "告白のタイミング": {
            True: "告白のタイミングが近づいています。相手の反応を見ながら、思い切って気持ちを伝えてみて。成功の可能性は高いです。",
            False: "今すぐの告白は少し待って。もう少し相手との距離を縮めてから。焦らず、自然な流れを大切に。"
        },
        "嫉妬・不安": {
            True: "不安は杞憂に終わりそうです。相手はあなたのことを大切に思っています。自信を持って。",
            False: "不安を相手にぶつける前に、まず自分の中で整理を。冷静に状況を見ると、思い過ごしかもしれません。"
        },
        "友達以上恋人未満": {
            True: "関係が進展するタイミングです。少し踏み込んだアプローチで、友達から恋人への扉が開きます。",
            False: "今は友達としての関係を大切に。急に変えようとせず、相手が心を開くのを待ちましょう。"
        },
        "年の差恋愛": {
            True: "年齢差は問題になりません。二人の気持ちが通じ合えば、関係は良い方向に進みます。",
            False: "周囲の目を気にしすぎないで。大切なのは二人の関係。自分たちのペースで進めましょう。"
        },
        "連絡・LINE": {
            True: "連絡は来る方向です。ただし、あなたからも自然なきっかけを作ってみて。軽い話題から始めるのがおすすめ。",
            False: "今は待つ時期。相手にも事情があるかもしれません。追いすぎず、自分の時間を充実させましょう。"
        },
        "返信がそっけない": {
            True: "相手の態度は一時的なもの。忙しさや疲れが原因かも。少し時間を置けば、元の温度感に戻ります。",
            False: "返信が冷たく感じるのは、相手の余裕のなさかも。追いすぎず、軽い返しやすいメッセージを心がけて。"
        },
        "音信不通": {
            True: "連絡が再開する兆しがあります。ただし、重い連絡は避けて。軽い挨拶程度から始めてみて。",
            False: "今は追わない方が吉。相手の状況が落ち着くまで、自分の時間を大切にしましょう。"
        },
        "復縁": {
            True: "復縁の可能性はあります。ただし、同じ失敗を繰り返さないよう、自分自身の変化も大切にして。",
            False: "過去を振り返るより、新しい出会いに目を向けるタイミングかもしれません。あなたにはもっと良い人がいるはず。"
        },
        "結婚": {
            True: "結婚に向けて良い流れが来ています。自然な会話の中で、将来の話を出してみて。",
            False: "焦らないで。二人の関係を深めることが先。結婚は自然な流れで訪れます。"
        },
        "複雑恋愛": {
            True: "状況が整理されていく兆し。焦らず、冷静に判断することで良い方向に進みます。",
            False: "感情に流されず、現実を見つめて。あなた自身が本当に望む未来を考える時です。"
        },
        "遠距離恋愛": {
            True: "距離を超えて、二人の絆は強まっています。会えない時間も信頼で乗り越えられます。",
            False: "不安になる時もあるけど、連絡の質を大切に。会えた時の時間を濃くすることが大切。"
        },
        "既婚者の恋": {
            True: "状況が動く可能性はありますが、慎重に。あなた自身の幸せを最優先に考えて。",
            False: "現実を冷静に見つめる時。この恋が本当にあなたを幸せにするか、考えてみて。"
        }
    }
    
    if theme in theme_advice:
        return theme_advice[theme][is_positive]
    
    # デフォルト
    if is_positive:
        return "恋愛運は上昇中！積極的に行動することで、良い結果に繋がります。自信を持って。"
    else:
        return "今は内面を磨く時期。焦らず自分を大切にすることで、良いご縁が巡ってきます。"
