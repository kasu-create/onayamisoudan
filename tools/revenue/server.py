"""
ニッチSaaS案 — 収益化サーバー（Stripe Checkout + ランディング）

起動例:
  tools/revenue/.env に鍵を書く（env.local.example 参照）→ cd tools/revenue → py server.py
  または PowerShell:
  cd tools/revenue
  $env:STRIPE_SECRET_KEY="sk_test_..."
  $env:STRIPE_PRICE_LIGHT="price_..."
  $env:STRIPE_PRICE_STANDARD="price_..."
  $env:STRIPE_PRICE_RETAINER="price_..."   # 任意（サブスク）
  $env:PUBLIC_BASE_URL="http://127.0.0.1:5000"
  python server.py

本番では HTTPS の URL を PUBLIC_BASE_URL に設定し、Stripe のWebhookで
履歴管理するとより安全（現状は success の session 検証のみ）。
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

import stripe
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, url_for

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent

# tools/revenue/.env に鍵を書けば、起動のたびに PowerShell で $env しなくてよい
load_dotenv(HERE / ".env")

app = Flask(__name__, template_folder=str(HERE / "templates"))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-change-me-for-session")


@app.before_request
def _stripe_api_key() -> None:
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "").strip()


def _public_base() -> str:
    return os.environ.get("PUBLIC_BASE_URL", "http://127.0.0.1:5000").rstrip("/")


def _default_meta() -> dict:
    return {
        "top20": [],
        "priority": {},
        "low_competition": [],
        "pattern_labels": {
            "1": "予約",
            "2": "資料期限",
            "3": "進捗",
            "4": "追客",
            "5": "規制",
        },
        "patterns": {},
    }


def _catalog_raw() -> dict:
    path = HERE / "ideas_catalog.json"
    if not path.is_file():
        return {"version": 1, "default_monthly_jpy": 2000, "meta": _default_meta(), "ideas": []}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    meta = dict(_default_meta())
    meta.update(data.get("meta") or {})
    data["meta"] = meta
    data.setdefault("version", 1)
    data.setdefault("default_monthly_jpy", 2000)
    data.setdefault("ideas", [])
    return data


def _resolved_default_monthly(catalog: dict) -> int:
    env_def = os.environ.get("IDEA_DEFAULT_MONTHLY_JPY", "").strip()
    if env_def.isdigit():
        return max(50, int(env_def))
    return max(50, int(catalog.get("default_monthly_jpy", 2000)))


def _idea_monthly_jpy(idea: dict, catalog: dict) -> int:
    if idea.get("monthly_jpy") is not None:
        return max(50, int(idea["monthly_jpy"]))
    return _resolved_default_monthly(catalog)


def _get_idea(idea_id: int) -> dict | None:
    catalog = _catalog_raw()
    for it in catalog.get("ideas", []):
        if int(it.get("id", -1)) == idea_id:
            return it
    return None


def _product_page_path(idea_id: int) -> str:
    return url_for("product_page", idea_id=idea_id)


def _listing_text_for_marketplace(idea: dict, idea_id: int, monthly_jpy: int, page_url: str) -> str:
    """クラウドソーシング等に貼る説明文。ideas_catalog の listing_pitch があれば {{URL}} を置換。"""
    custom = str(idea.get("listing_pitch") or "").strip()
    if custom:
        return (
            custom.replace("{{URL}}", page_url)
            .replace("{{url}}", page_url)
            .replace("{{MONTHLY}}", f"{monthly_jpy:,}")
        )
    cat = str(idea.get("category", "")).strip()
    title = str(idea.get("title", "")).strip()
    return (
        f"【{cat}】{title}\n\n"
        f"ニッチSaaS向けのテーマ案です。リサーチ・スコアリング済みの月額プラン（目安 ¥{monthly_jpy:,}/月）として提供しています。\n"
        f"詳細・お申込み: {page_url}\n"
    )


def _channel_playbook() -> dict:
    path = HERE / "channel_playbook.json"
    if not path.is_file():
        return {"channels": [], "disclaimer_ja": ""}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _match_score(idea: dict, ch: dict) -> int:
    cat = str(idea.get("category", ""))
    title = str(idea.get("title", ""))
    hay = cat + title
    score = int(ch.get("base_score", 0))
    w = int(ch.get("keyword_weight", 2))
    for kw in ch.get("category_keywords") or []:
        if kw and kw in hay:
            score += w
    return score


def _ranked_channels(idea: dict) -> list[tuple[dict, int]]:
    pb = _channel_playbook()
    out = [(ch, _match_score(idea, ch)) for ch in pb.get("channels", []) if ch.get("id")]
    out.sort(key=lambda x: -x[1])
    return out


def _post_title_for_channel(idea: dict, ch: dict) -> str:
    tpl = str(ch.get("title_template") or "").strip()
    cat = str(idea.get("category", ""))
    tit = str(idea.get("title", ""))[:80]
    if not tpl:
        return f"【{cat}】{tit}｜月額プラン（リサーチ済テーマ）"
    return tpl.format(category=cat, title=tit)


def _post_body_for_channel(idea: dict, idea_id: int, ch: dict, page_url: str, monthly_jpy: int) -> str:
    base_listing = _listing_text_for_marketplace(idea, idea_id, monthly_jpy, page_url)
    prefix = str(ch.get("body_prefix") or "").strip()
    suffix = str(ch.get("body_suffix") or "").strip()
    parts: list[str] = []
    if prefix:
        parts.append(prefix)
    parts.append(base_listing)
    if suffix:
        parts.append(suffix)
    return "\n\n".join(parts).strip()


def _post_fulfillment_webhook(payload: dict) -> None:
    """FULFILLMENT_WEBHOOK_URL があれば JSON POST（Make / Zapier / 自前API 向け）。"""
    url = os.environ.get("FULFILLMENT_WEBHOOK_URL", "").strip()
    if not url:
        return
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=12)
    except (urllib.error.URLError, OSError) as e:
        print(f"FULFILLMENT_WEBHOOK_URL 通知失敗: {e}", file=sys.stderr)


@app.route("/api/catalog_config")
def catalog_config():
    catalog = _catalog_raw()
    return jsonify(
        default_monthly_jpy=_resolved_default_monthly(catalog),
        stripe_ready=bool(os.environ.get("STRIPE_SECRET_KEY", "").strip()),
        idea_count=len(catalog.get("ideas", [])),
    )


@app.route("/api/ideas")
def api_ideas():
    c = _catalog_raw()
    return jsonify(
        version=c.get("version", 1),
        default_monthly_jpy=_resolved_default_monthly(c),
        meta=c.get("meta", _default_meta()),
        ideas=c.get("ideas", []),
    )


@app.route("/catalog")
@app.route("/products")
@app.route("/store")
def catalog_page():
    c = _catalog_raw()
    items = []
    for it in sorted(c.get("ideas", []), key=lambda x: int(x.get("id", 0))):
        iid = int(it.get("id", 0))
        amt = _idea_monthly_jpy(it, c)
        items.append(
            {
                "id": iid,
                "category": it.get("category", ""),
                "title": it.get("title", ""),
                "sell": int(it.get("sell", 0)),
                "comp": int(it.get("comp", 0)),
                "recur": int(it.get("recur", 0)),
                "total": int(it.get("sell", 0)) + int(it.get("comp", 0)) + int(it.get("recur", 0)),
                "monthly_jpy": amt,
            }
        )
    return render_template(
        "catalog.html",
        ideas=items,
        idea_count=len(items),
        stripe_ideas_ok=bool(os.environ.get("STRIPE_SECRET_KEY", "").strip()),
    )


@app.route("/p/<int:idea_id>")
def product_page(idea_id: int):
    """商品ごとの共有用ランディング（案件サイト本文に貼るURL用）。"""
    catalog = _catalog_raw()
    idea = _get_idea(idea_id)
    if not idea:
        abort(404)
    monthly = _idea_monthly_jpy(idea, catalog)
    base = _public_base().rstrip("/")
    page_url = base + _product_page_path(idea_id)
    listing_text = _listing_text_for_marketplace(idea, idea_id, monthly, page_url)
    title = str(idea.get("title", "")).strip()
    category = str(idea.get("category", "")).strip()
    og_desc = f"{category}向け「{title}」の月額プラン（目安 ¥{monthly:,}/月）。"[:200]
    return render_template(
        "product.html",
        idea_id=idea_id,
        title=title,
        category=category,
        sell=int(idea.get("sell", 0)),
        comp=int(idea.get("comp", 0)),
        recur=int(idea.get("recur", 0)),
        total=int(idea.get("sell", 0)) + int(idea.get("comp", 0)) + int(idea.get("recur", 0)),
        monthly_jpy=monthly,
        share_url=page_url,
        listing_text=listing_text,
        og_desc=og_desc,
        stripe_ideas_ok=bool(os.environ.get("STRIPE_SECRET_KEY", "").strip()),
    )


@app.route("/api/idea/<int:idea_id>/share")
def api_idea_share(idea_id: int):
    """自動化用: 共有URLと案件貼り付け用テキストをJSONで返す。"""
    catalog = _catalog_raw()
    idea = _get_idea(idea_id)
    if not idea:
        abort(404)
    monthly = _idea_monthly_jpy(idea, catalog)
    base = _public_base().rstrip("/")
    page_url = base + _product_page_path(idea_id)
    return jsonify(
        idea_id=idea_id,
        page_url=page_url,
        checkout_path=url_for("checkout_idea", idea_id=idea_id),
        listing_text=_listing_text_for_marketplace(idea, idea_id, monthly, page_url),
        monthly_jpy=monthly,
        title=str(idea.get("title", "")),
        category=str(idea.get("category", "")),
    )


@app.route("/sell")
def sell_hub():
    pb = _channel_playbook()
    c = _catalog_raw()
    ideas_min = []
    for it in sorted(c.get("ideas", []), key=lambda x: int(x.get("id", 0))):
        ideas_min.append(
            {
                "id": int(it.get("id", 0)),
                "category": it.get("category", ""),
                "title": it.get("title", ""),
            }
        )
    return render_template(
        "sell_hub.html",
        channels=pb.get("channels", []),
        disclaimer=pb.get("disclaimer_ja", ""),
        ideas=ideas_min,
    )


@app.route("/sell/<int:idea_id>")
def sell_idea_page(idea_id: int):
    catalog = _catalog_raw()
    idea = _get_idea(idea_id)
    if not idea:
        abort(404)
    monthly = _idea_monthly_jpy(idea, catalog)
    base = _public_base().rstrip("/")
    page_url = base + _product_page_path(idea_id)
    pb = _channel_playbook()
    ranked = _ranked_channels(idea)
    max_score = ranked[0][1] if ranked else 0
    kits: list[dict] = []
    for ch, score in ranked:
        kits.append(
            {
                "id": ch.get("id"),
                "name": ch.get("name"),
                "url": ch.get("url") or "",
                "role": ch.get("role"),
                "fit": ch.get("fit"),
                "score": score,
                "highlight": score == max_score and max_score >= 4,
                "post_title": _post_title_for_channel(idea, ch),
                "post_body": _post_body_for_channel(idea, idea_id, ch, page_url, monthly),
                "steps": ch.get("posting_steps") or [],
            }
        )
    return render_template(
        "sell_idea.html",
        idea_id=idea_id,
        title=str(idea.get("title", "")),
        category=str(idea.get("category", "")),
        page_url=page_url,
        checkout_full_url=base + url_for("checkout_idea", idea_id=idea_id),
        monthly_jpy=monthly,
        disclaimer=pb.get("disclaimer_ja", ""),
        kits=kits,
        stripe_ideas_ok=bool(os.environ.get("STRIPE_SECRET_KEY", "").strip()),
        max_match_score=max_score,
    )


@app.route("/api/idea/<int:idea_id>/sell-kit")
def api_idea_sell_kit(idea_id: int):
    catalog = _catalog_raw()
    idea = _get_idea(idea_id)
    if not idea:
        abort(404)
    monthly = _idea_monthly_jpy(idea, catalog)
    base = _public_base().rstrip("/")
    page_url = base + _product_page_path(idea_id)
    ranked = _ranked_channels(idea)
    max_score = ranked[0][1] if ranked else 0
    out_kits = []
    for ch, score in ranked:
        out_kits.append(
            {
                "channel_id": ch.get("id"),
                "name": ch.get("name"),
                "site_url": ch.get("url") or "",
                "match_score": score,
                "recommended": bool(score == max_score and max_score >= 4),
                "post_title": _post_title_for_channel(idea, ch),
                "post_body": _post_body_for_channel(idea, idea_id, ch, page_url, monthly),
                "posting_steps": ch.get("posting_steps") or [],
            }
        )
    return jsonify(
        idea_id=idea_id,
        page_url=page_url,
        checkout_path=url_for("checkout_idea", idea_id=idea_id),
        monthly_jpy=monthly,
        title=str(idea.get("title", "")),
        category=str(idea.get("category", "")),
        kits=out_kits,
    )


def _price(plan: str) -> tuple[str, str]:
    """Returns (price_id, mode payment|subscription)."""
    plans = {
        "light": (os.environ.get("STRIPE_PRICE_LIGHT", "").strip(), "payment"),
        "standard": (os.environ.get("STRIPE_PRICE_STANDARD", "").strip(), "payment"),
        "retainer": (os.environ.get("STRIPE_PRICE_RETAINER", "").strip(), "subscription"),
    }
    if plan not in plans:
        abort(404)
    pid, mode = plans[plan]
    if not pid:
        abort(503, description="このプランの Stripe Price ID が未設定です（環境変数を確認）")
    return pid, mode


@app.route("/")
def index():
    key_ok = bool(os.environ.get("STRIPE_SECRET_KEY", "").strip())
    p_light = bool(os.environ.get("STRIPE_PRICE_LIGHT", "").strip())
    p_std = bool(os.environ.get("STRIPE_PRICE_STANDARD", "").strip())
    p_ret = bool(os.environ.get("STRIPE_PRICE_RETAINER", "").strip())
    cat = _catalog_raw()
    n_ideas = len(cat.get("ideas", []))
    return render_template(
        "landing.html",
        stripe_ready=key_ok and (p_light or p_std or p_ret),
        has_light=p_light,
        has_standard=p_std,
        has_retainer=p_ret,
        catalog_checkout_ok=key_ok and n_ideas > 0,
        idea_count=n_ideas,
        default_monthly_jpy=_resolved_default_monthly(cat),
    )


@app.route("/checkout/idea/<int:idea_id>")
def checkout_idea(idea_id: int):
    if not stripe.api_key:
        abort(503, description="STRIPE_SECRET_KEY が未設定です")
    catalog = _catalog_raw()
    idea = _get_idea(idea_id)
    if not idea:
        abort(404, description="該当する案がありません")
    amount = _idea_monthly_jpy(idea, catalog)
    base = _public_base()
    title = str(idea.get("title", ""))
    product_name = f"ニッチSaaS案 No.{idea_id}"
    if title:
        product_name = f"No.{idea_id} {title}"[:120]
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {
                    "price_data": {
                        "currency": "jpy",
                        "unit_amount": amount,
                        "recurring": {"interval": "month"},
                        "product_data": {
                            "name": product_name,
                            "metadata": {"idea_id": str(idea_id)},
                        },
                    },
                    "quantity": 1,
                }
            ],
            success_url=base + "/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=base + "/cancel",
            allow_promotion_codes=True,
            billing_address_collection="auto",
            locale="ja",
            subscription_data={
                "metadata": {
                    "idea_id": str(idea_id),
                    "idea_title": title[:200],
                },
            },
            metadata={"idea_id": str(idea_id)},
        )
    except stripe.error.StripeError as e:
        abort(502, description=str(e.user_message or e))

    return redirect(session.url, code=303)


@app.route("/checkout/<plan>")
def checkout(plan: str):
    if not stripe.api_key:
        abort(503, description="STRIPE_SECRET_KEY が未設定です")

    price_id, mode = _price(plan)
    base = _public_base()
    try:
        params: dict = {
            "mode": mode,
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": base + "/success?session_id={CHECKOUT_SESSION_ID}",
            "cancel_url": base + "/cancel",
            "allow_promotion_codes": True,
            "billing_address_collection": "auto",
            "locale": "ja",
        }
        if mode == "payment":
            params["customer_creation"] = "always"
        session = stripe.checkout.Session.create(**params)
    except stripe.error.StripeError as e:
        abort(502, description=str(e.user_message or e))

    return redirect(session.url, code=303)


@app.route("/success")
def success():
    session_id = request.args.get("session_id", "").strip()
    paid = False
    customer_email = None
    amount_total = None
    currency = None

    if session_id and stripe.api_key:
        try:
            s = stripe.checkout.Session.retrieve(session_id)
            pstat = getattr(s, "payment_status", None)
            st = getattr(s, "status", None)
            paid = pstat == "paid" or st == "complete"
            details = getattr(s, "customer_details", None)
            if details is not None:
                customer_email = getattr(details, "email", None)
            amount_total = getattr(s, "amount_total", None)
            cur = getattr(s, "currency", None) or ""
            currency = cur.upper() if cur else None
        except stripe.error.StripeError:
            paid = False

    delivery = os.environ.get("POST_PURCHASE_DELIVERY_URL", "").strip()
    amount_display = None
    if paid and amount_total is not None and currency:
        if currency == "JPY":
            amount_display = f"¥{int(amount_total):,}"
        else:
            amount_display = f"{amount_total / 100:.2f} {currency}"

    return render_template(
        "success.html",
        paid=paid,
        session_id=session_id if paid else "",
        customer_email=customer_email,
        amount_display=amount_display,
        delivery_url=delivery,
        dashboard_url=url_for("dashboard", _external=False),
        catalog_url=url_for("catalog_page", _external=False),
    )


@app.route("/cancel")
def cancel():
    return render_template("cancel.html")


@app.route("/dashboard")
def dashboard():
    path = TOOLS / "niche_saas_ideas_dashboard.html"
    if not path.is_file():
        abort(404)
    return send_file(path, mimetype="text/html; charset=utf-8")


@app.route("/assets/niche_dashboard.js")
def niche_dashboard_js():
    path = TOOLS / "niche_dashboard.js"
    if not path.is_file():
        abort(404)
    return send_file(path, mimetype="application/javascript; charset=utf-8")


@app.route("/health")
def health():
    cat = _catalog_raw()
    return jsonify(
        ok=True,
        stripe=bool(os.environ.get("STRIPE_SECRET_KEY", "").strip()),
        ideas_count=len(cat.get("ideas", [])),
        default_monthly_jpy=_resolved_default_monthly(cat),
        stripe_webhook_secret_set=bool(os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()),
        fulfillment_webhook_url_set=bool(os.environ.get("FULFILLMENT_WEBHOOK_URL", "").strip()),
    )


@app.route("/webhooks/stripe", methods=["POST"])
def stripe_webhook():
    """Stripe からのイベント。個別案購入（metadata.idea_id あり）完了時に任意URLへ転送。"""
    wh_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
    if not wh_secret:
        abort(404)
    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, wh_secret)
    except ValueError:
        abort(400)
    except stripe.error.SignatureVerificationError:
        abort(400)

    if event.get("type") == "checkout.session.completed":
        obj = event.get("data", {}).get("object") or {}
        md = obj.get("metadata") or {}
        idea_id = md.get("idea_id")
        if idea_id:
            details = obj.get("customer_details") or {}
            _post_fulfillment_webhook(
                {
                    "source": "stripe",
                    "stripe_event_type": event.get("type"),
                    "stripe_event_id": event.get("id"),
                    "checkout_session_id": obj.get("id"),
                    "mode": obj.get("mode"),
                    "idea_id": str(idea_id),
                    "customer_email": details.get("email"),
                    "amount_total": obj.get("amount_total"),
                    "currency": obj.get("currency"),
                }
            )
    return jsonify(received=True)


def main() -> None:
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes")
    if not os.environ.get("STRIPE_SECRET_KEY"):
        print("警告: STRIPE_SECRET_KEY 未設定。ランディングは表示されますが Checkout は 503 になります。", file=sys.stderr)
    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
