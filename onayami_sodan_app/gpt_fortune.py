"""GPT鑑定モジュール - OpenAI APIを使って恋愛相談の鑑定を行う"""
from __future__ import annotations

import random
from typing import Any

from openai import OpenAI

# タロットカード78枚（大アルカナ22枚 + 小アルカナ56枚）
MAJOR_ARCANA = [
    {"name": "The Fool", "name_jp": "愚者", "meaning": "新しい始まり、自然体、軽やかな恋、可能性"},
    {"name": "The Magician", "name_jp": "魔術師", "meaning": "魅力の発揮、主導権、関係を動かす力"},
    {"name": "The High Priestess", "name_jp": "女教皇", "meaning": "秘めた想い、直感、慎重さ、言葉にしない感情"},
    {"name": "The Empress", "name_jp": "女帝", "meaning": "愛され力、包容力、魅力の開花、満たされる愛"},
    {"name": "The Emperor", "name_jp": "皇帝", "meaning": "安定、責任感、現実的な愛、主導する力"},
    {"name": "The Hierophant", "name_jp": "教皇", "meaning": "誠実さ、信頼、正式な関係、価値観の一致"},
    {"name": "The Lovers", "name_jp": "恋人", "meaning": "強い好意、惹かれ合い、選択、深い結びつき"},
    {"name": "The Chariot", "name_jp": "戦車", "meaning": "前進、進展、積極性、関係を動かす勢い"},
    {"name": "Strength", "name_jp": "力", "meaning": "思いやり、粘り強さ、感情のコントロール、関係修復"},
    {"name": "The Hermit", "name_jp": "隠者", "meaning": "距離、慎重さ、内省、一人で考える時間"},
    {"name": "Wheel of Fortune", "name_jp": "運命の輪", "meaning": "流れの変化、チャンス、再会、好転"},
    {"name": "Justice", "name_jp": "正義", "meaning": "誠実な判断、バランス、関係の見直し、白黒をつける流れ"},
    {"name": "The Hanged Man", "name_jp": "吊るされた男", "meaning": "停滞、我慢、見方を変える必要、待機"},
    {"name": "Death", "name_jp": "死神", "meaning": "終わりと再生、区切り、新しい形への変化"},
    {"name": "Temperance", "name_jp": "節制", "meaning": "歩み寄り、穏やかな回復、復縁への調整、調和"},
    {"name": "The Devil", "name_jp": "悪魔", "meaning": "執着、依存、離れがたさ、強い引力、苦しい魅力"},
    {"name": "The Tower", "name_jp": "塔", "meaning": "衝撃、突然の変化、崩壊と再構築、本音の露出"},
    {"name": "The Star", "name_jp": "星", "meaning": "希望、癒し、憧れ、素直な願い、未来への光"},
    {"name": "The Moon", "name_jp": "月", "meaning": "不安、曖昧さ、誤解、見えない本音、揺れる感情"},
    {"name": "The Sun", "name_jp": "太陽", "meaning": "両思い、喜び、安心感、オープンな愛、明るい進展"},
    {"name": "Judgement", "name_jp": "審判", "meaning": "復活、再スタート、気持ちの再確認、関係の見直し"},
    {"name": "The World", "name_jp": "世界", "meaning": "成就、完成、安定、満たされる関係"},
]

# 小アルカナのスートと意味
SUITS = {
    "Wands": {"name_jp": "ワンド", "theme": "情熱、行動力、積極性、進展、新しい展開"},
    "Cups": {"name_jp": "カップ", "theme": "愛情、感情、共感、ときめき、心のつながり"},
    "Swords": {"name_jp": "ソード", "theme": "思考、言葉、すれ違い、不安、決断、距離"},
    "Pentacles": {"name_jp": "ペンタクル", "theme": "安定、現実性、信頼、積み重ね、将来設計"},
}

# 数字カードの意味
NUMBER_MEANINGS = {
    "Ace": "始まり、新しい可能性、種まき",
    "Two": "選択、バランス、関係の芽生え",
    "Three": "発展、成長、協力",
    "Four": "安定、休息、基盤づくり",
    "Five": "試練、変化、困難",
    "Six": "調和、援助、回復",
    "Seven": "挑戦、忍耐、内省",
    "Eight": "動き、変化、進展",
    "Nine": "達成間近、充実、願望",
    "Ten": "完成、満足、次のステージへ",
}

# コートカードの意味
COURT_MEANINGS = {
    "Page": "連絡、興味、恋の始まり、素直な気持ち、ぎこちなさ",
    "Knight": "行動、アプローチ、勢い、動きの変化",
    "Queen": "受容、魅力、安心感、内面的な成熟",
    "King": "安定、責任、誠実さ、主導権、現実的な愛情",
}


def generate_minor_arcana() -> list[dict]:
    """小アルカナ56枚を生成"""
    cards = []
    numbers = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"]
    courts = ["Page", "Knight", "Queen", "King"]
    
    for suit, suit_info in SUITS.items():
        # 数字カード（1-10）
        for num in numbers:
            cards.append({
                "name": f"{num} of {suit}",
                "name_jp": f"{suit_info['name_jp']}の{num}",
                "meaning": f"{NUMBER_MEANINGS[num]}（{suit_info['theme']}）",
                "is_major": False,
            })
        # コートカード
        for court in courts:
            cards.append({
                "name": f"{court} of {suit}",
                "name_jp": f"{suit_info['name_jp']}の{court}",
                "meaning": f"{COURT_MEANINGS[court]}（{suit_info['theme']}）",
                "is_major": False,
            })
    
    return cards


def get_all_cards() -> list[dict]:
    """78枚全てのカードを取得"""
    major = [{"is_major": True, **card} for card in MAJOR_ARCANA]
    minor = generate_minor_arcana()
    return major + minor


def draw_cards(count: int = 1) -> list[dict]:
    """ランダムにカードを引く（正位置のみ）"""
    all_cards = get_all_cards()
    return random.sample(all_cards, min(count, len(all_cards)))


def create_fortune_prompt(question: str, theme: str, main_card: dict, sub_cards: list[dict]) -> str:
    """GPTに送るプロンプトを生成"""
    
    sub_cards_text = "\n".join([
        f"- {pos}: {card['name_jp']}（{card['name']}）- {card['meaning']}"
        for pos, card in zip(["過去", "現在", "未来"], sub_cards)
    ])
    
    return f"""あなたは恋愛・復縁専門の、優しくて頼れるタロット占い師です。
相談者の不安や迷いに寄り添いながら、前向きで現実的、そして実践しやすいアドバイスを届けてください。

【相談テーマ】{theme}

【相談内容】
{question}

【本鑑定カード（ワンオラクル）】
{main_card['name_jp']}（{main_card['name']}）
意味: {main_card['meaning']}
{'※大アルカナ：この恋にとって重要な転機・学び・運命的なテーマがあります' if main_card.get('is_major') else ''}

【おまけ鑑定カード（過去・現在・未来）】
{sub_cards_text}

以下のフォーマットで鑑定結果を出力してください。
本鑑定とおまけ鑑定の内容は必ず一貫させてください。
相談者の不安を受け止め、厳しいカードでも傷つける言い方をせず、最後は必ず前向きで実践可能なアドバイスにつなげてください。

---

## 🔮 本鑑定結果

### 引いたカード
**{main_card['name_jp']}（{main_card['name']}）**

### あなたの気持ち 💭
[300〜400文字程度で、相談者の不安、期待、迷い、本音をやさしく整理して伝える]

### お相手の気持ち 💕
[300〜400文字程度で、相手の気持ちや距離感、迷い、関係への温度感を丁寧に読み解く。断定ではなく傾向として表現する]

### より良い未来のためのアドバイス ✨
[250〜350文字程度で、今の相談者が実践しやすい具体的なアドバイスを書く]

---

## 🎁 おまけ鑑定：あなたの恋愛の流れ

### 過去 - {sub_cards[0]['name_jp']}
[100〜150文字程度で、これまでの関係や背景を説明する]

### 現在 - {sub_cards[1]['name_jp']}
[100〜150文字程度で、今の状況や気持ちの流れを説明する]

### 未来 - {sub_cards[2]['name_jp']}
[100〜150文字程度で、希望を持てる形で今後の流れを伝える。断定ではなく可能性として表現する]

---

最後は、相談者の心が少し軽くなるような一言でやさしく締めてください。"""


def perform_gpt_reading(
    api_key: str,
    question: str,
    theme: str,
    model: str = "gpt-4o-mini"
) -> dict[str, Any]:
    """GPTを使ってタロット鑑定を実行"""
    
    # カードを引く
    main_card = draw_cards(1)[0]
    sub_cards = draw_cards(3)
    
    # プロンプト生成
    prompt = create_fortune_prompt(question, theme, main_card, sub_cards)
    
    # OpenAI API呼び出し
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "あなたは恋愛・復縁専門の、優しくて頼れるタロット占い師です。口調はやわらかく、親しみやすく、カジュアルで優しい。相談者の味方として寄り添います。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.8,
        max_tokens=2000,
    )
    
    result_text = response.choices[0].message.content
    
    return {
        "theme": theme,
        "question": question,
        "main_card": main_card,
        "sub_cards": sub_cards,
        "reading": result_text,
        "model": model,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }
    }
