/**
 * /oracle/reading/ — プロフィール → シャッフル → 3枚 → 再シャッフル → 5枚 → 長文鑑定
 */

import { buildFullDeck, shuffleDeck } from "./tarot-deck.js";
import { SPREAD_THREE, SPREAD_FIVE } from "./spread-config.js";
import { getCardMeaning } from "./card-meanings.js";
import { resolveCardImageUrl, CARD_IMAGE_EXTENSIONS } from "./card-images.js";

function getQueryParam(name) {
  return new URLSearchParams(window.location.search).get(name);
}

function phaseToStep(phaseId) {
  const map = {
    "phase-intro": 1,
    "phase-three": 2,
    "phase-five": 3,
    "phase-summary": 4,
  };
  return map[phaseId] ?? 1;
}

function setProgressStep(step) {
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById("step-" + i);
    if (el) el.classList.toggle("is-active", i === step);
  }
}

function showPhase(id) {
  document.querySelectorAll(".phase").forEach((el) => {
    const match = el.id === id;
    el.hidden = !match;
    el.classList.toggle("is-hidden", !match);
  });
  setProgressStep(phaseToStep(id));
}



function fakeShuffleDelay(ms, statusEl, message, done) {
  if (statusEl) statusEl.textContent = message || "シャッフル中…";
  setTimeout(() => {
    if (statusEl) statusEl.textContent = "";
    done();
  }, ms);
}

function cardMeta(card) {
  if (card.arcana === "major") return "大アルカナ";
  return `${card.suitJa} · ${card.rank}`;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderCardElement(card) {
  const meaning = getCardMeaning(card.id);
  const article = document.createElement("article");
  article.className = "tarot-card";
  article.setAttribute("data-arcana", card.arcana);
  if (card.suit) article.setAttribute("data-suit", card.suit);

  const face = document.createElement("div");
  face.className = "tarot-card__face";

  const img = document.createElement("img");
  img.className = "tarot-card__img is-hidden";
  img.alt = `${card.nameJa}のカード`;
  img.loading = "lazy";
  img.decoding = "async";

  const glyphDiv = document.createElement("div");
  glyphDiv.className = "tarot-card__glyph";
  glyphDiv.setAttribute("aria-hidden", "true");
  glyphDiv.textContent = card.glyph || "✦";

  let extIndex = 0;
  img.addEventListener("load", () => {
    img.classList.remove("is-hidden");
    glyphDiv.classList.add("is-behind-image");
  });
  img.addEventListener("error", () => {
    extIndex += 1;
    if (extIndex >= CARD_IMAGE_EXTENSIONS.length) {
      img.remove();
      return;
    }
    img.src = resolveCardImageUrl(card.id, CARD_IMAGE_EXTENSIONS[extIndex]);
  });
  img.src = resolveCardImageUrl(card.id, CARD_IMAGE_EXTENSIONS[0]);

  face.appendChild(img);
  face.appendChild(glyphDiv);

  const nameEl = document.createElement("div");
  nameEl.className = "tarot-card__name";
  nameEl.textContent = card.nameJa;

  const metaEl = document.createElement("div");
  metaEl.className = "tarot-card__meta";
  metaEl.textContent = cardMeta(card);

  article.appendChild(face);
  article.appendChild(nameEl);

  return article;
}

function renderSpread(container, definitions, cards) {
  if (!container) return;
  container.innerHTML = "";
  definitions.forEach((def, i) => {
    const card = cards[i];
    if (!card) return;
    const wrap = document.createElement("div");
    wrap.className = "spread-slot";
    wrap.setAttribute("role", "listitem");
    wrap.innerHTML = `
      <div class="spread-slot__label">${escapeHtml(def.label)}</div>
      <div class="spread-slot__hint">${escapeHtml(def.hint)}</div>
    `;
    wrap.appendChild(renderCardElement(card));
    container.appendChild(wrap);
  });
}

/** @returns {Date|null} */
function parseISODate(str) {
  if (!str || !/^\d{4}-\d{2}-\d{2}$/.test(str)) return null;
  const d = new Date(str + "T12:00:00");
  return Number.isNaN(d.getTime()) ? null : d;
}

function ageFromBirth(iso) {
  const b = parseISODate(iso);
  if (!b) return null;
  const t = new Date();
  let a = t.getFullYear() - b.getFullYear();
  const m = t.getMonth() - b.getMonth();
  if (m < 0 || (m === 0 && t.getDate() < b.getDate())) a--;
  return Math.max(0, a);
}

function ageBracketLabel(age) {
  if (age == null) return "（年齢未設定）";
  if (age < 22) return "20代前半より若い／学生〜社会人初期のような立ち上がりの時期";
  if (age < 30) return "20代後半〜30代手前：選択と試行が重なりやすい時期";
  if (age < 40) return "30代：責任と役割が具体化しやすい時期";
  if (age < 55) return "40〜50代：軸の再定義と長期設計が前面に出やすい時期";
  return "55歳以降：経験を資産に変え、取捨選択が円熟しやすい時期";
}

function hashString(str) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function addDays(base, n) {
  const d = new Date(base.getTime());
  d.setDate(d.getDate() + n);
  return d;
}

function formatJapaneseDate(d) {
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
}

/**
 * カード＋入力から決定的な「目安日付」を3つ
 * @param {string} seedStr
 */
function deriveMilestoneDates(seedStr) {
  const h = hashString(seedStr);
  const base = new Date();
  const offsets = [
    12 + (h % 38),
    40 + ((h >> 5) % 45),
    88 + ((h >> 10) % 70),
  ];
  const labels = [
    "気持ちや状況が「動き出しやすい」最初の窓",
    "対話・調整・決断が乗りやすい中盤の波",
    "区切りや新しい型が決まりやすい後半の節目",
  ];
  return offsets.map((off, i) => ({
    label: labels[i],
    dateStr: formatJapaneseDate(addDays(base, off)),
  }));
}

function cardArcanaPhrase(card) {
  return card.arcana === "major"
    ? "人生全体のテーマとして強く効いてくる大アルカナ"
    : "日常の感情・出来事・人間関係の機微を映す小アルカナ";
}

/**
 * カード1枚ごとの長文解説（6〜8段落）
 * @param {{ label: string, hint: string }} def
 * @param {import("./tarot-deck.js").TarotCard} card
 */
function expandedCardParagraph(def, card, profile) {
  const m = getCardMeaning(card.id);
  const kw = (m.keywords || []).length ? m.keywords.join("、") : "静かな推移、内面的な調整";
  const concernSnippet = profile.concern.trim().slice(0, 150);
  const arcanaType = cardArcanaPhrase(card);
  const ageTip = ageBracketLabel(profile.age);

  const paragraphs = [];

  paragraphs.push(
    `「${def.label}」の位置に「${card.nameJa}」が現れました。このカードが持つ雰囲気を一言で表すと「${kw}」です。タロットにおいて${arcanaType}に分類され、あなたの問いに対して特別な重みを持って応えています。`
  );

  paragraphs.push(m.gist);

  paragraphs.push(
    `あなたが「${concernSnippet}${profile.concern.length > 150 ? "…" : ""}」というテーマを持ち込んだとき、このカードは「${def.hint}」という角度から光を当てます。言い換えれば、今あなたが見落としがちな視点、あるいは無意識に避けている領域がここに映し出されています。`
  );

  paragraphs.push(
    `年齢帯のニュアンス（${ageTip}）を重ねると、このカードの意味合いは少し変化します。若い時期であれば「試行錯誤を恐れずに動く」ことが示唆されますし、経験を重ねた時期であれば「過去の成功パターンに固執しすぎていないか」を問いかけています。いずれにせよ、「${def.label}」として出たこのカードは、あなたの現在地を正確に映す鏡です。`
  );

  paragraphs.push(
    `実践的なアドバイスとしては、まず「${kw}」のキーワードを日常の中で意識してみてください。たとえば、仕事の場面では会議の発言、プライベートでは相手への声かけ——そこに「${card.nameJa}」のエネルギーを少しだけ取り入れるだけで、周囲の反応が変わり始めます。`
  );

  paragraphs.push(
    `このカードが示す時間感覚は、急ぎすぎず、かといって停滞もしないバランスです。「${def.label}」のポジションは特に「いま何を優先すべきか」を教えてくれます。焦って結論を出すのではなく、1週間〜2週間ほど様子を見ながら、自分の感情の動きを観察してください。`
  );

  if (card.arcana === "major") {
    paragraphs.push(
      `大アルカナである「${card.nameJa}」が出たということは、この問題があなたの人生全体のテーマと深く結びついている可能性があります。単なる一時的な悩みではなく、長期的な成長の課題として捉えると、対処の仕方も変わってくるでしょう。`
    );
  } else {
    paragraphs.push(
      `小アルカナの「${card.nameJa}」は、日常レベルでの具体的なヒントを与えています。大きな決断というよりも、毎日の小さな選択——返信のタイミング、言葉の選び方、行動の優先順位——に意識を向けることで、状況は着実に動き出します。`
    );
  }

  return paragraphs.map((p) => `<p>${escapeHtml(p)}</p>`).join("");
}

function partnerSection(profile) {
  if (!profile.partnerBirth || !profile.selfBirth) return "";
  const a = parseISODate(profile.selfBirth);
  const b = parseISODate(profile.partnerBirth);
  if (!a || !b) return "";
  const diffYears = Math.abs(a.getFullYear() - b.getFullYear());
  const diffMonths = Math.abs((a.getFullYear() - b.getFullYear()) * 12 + (a.getMonth() - b.getMonth()));
  let relationHint =
    "お二人の生年月日の差から、ペースの取り方にズレが出やすい／逆に補い合いやすい、という両面があります。";
  if (diffYears >= 8) {
    relationHint +=
      " 年齢や立場のステップ差が大きいほど、「期待の言語化」と「待つ期限の合意」が鍵になりやすいです。";
  } else if (diffYears <= 2) {
    relationHint +=
      " 近い世代同士は価値観の共鳴が出やすい一方、競争や比較が燃えやすいので、役割分担の明文化が有効です。";
  } else {
    relationHint +=
      " 中程度の差は、学び合いと刺激のバランスが取りやすい帯です。対話の頻度より「質（安心できる短時間）」を優先してください。";
  }
  return `<section class="pr-sec"><h3>ふたりの関係性のニュアンス</h3><p>${escapeHtml(
    relationHint
  )}</p><p>（生年月日の差・約${diffMonths}ヶ月単位のズレを参考にした読みです。絶対的な運命ではなく、コミュニケーション設計のヒントとしてお使いください。）</p></section>`;
}

function synthesisSection(profile, threeCards, fiveCards) {
  const s0 = threeCards[0];
  const s1 = threeCards[1];
  const s2 = threeCards[2];
  const f0 = fiveCards[0];
  const f1 = fiveCards[1];
  const f2 = fiveCards[2];
  const f3 = fiveCards[3];
  const f4 = fiveCards[4];
  const names = (c) => (c ? c.nameJa : "—");
  const concern = profile.concern.trim();

  const paragraphs = [];

  paragraphs.push(
    `いまのあなたは「${concern.slice(0, 200)}${concern.length > 200 ? "…" : ""}」というテーマを抱えています。3枚スプレッドで見ると、内側では「${names(s0)}」のエネルギーが流れ、外側には「${names(s1)}」という壁や課題があり、そこを突破するカギとして「${names(s2)}」が示されました。`
  );

  paragraphs.push(
    `5枚スプレッドはさらに深い層を掘り下げます。核心には「${names(f0)}」が鎮座しており、これはあなたの問題の根っこにある感情やパターンを象徴しています。見えにくい要素として「${names(f1)}」が浮かび上がりました。これは無意識に避けていること、あるいは「まだ気づいていないが、実はとても重要な要因」を指しています。`
  );

  paragraphs.push(
    `近い動きとして「${names(f2)}」が出ています。これは今後2〜3週間から1ヶ月ほどの間に起こりやすい変化の兆しです。取るとよい態度は「${names(f3)}」——このカードが示す姿勢を意識的に取り入れることで、流れに乗りやすくなります。そして全体のまとめとして「${names(f4)}」が現れました。これがこの鑑定全体を通して伝えたいメッセージの核です。`
  );

  paragraphs.push(
    `8枚のカードを総合すると、あなたにとって大切なのは「感情の揺れを否定しないこと」と「小さく分解して取り組むこと」です。${SPREAD_THREE[1].label}で示された「${names(s1)}」の課題は、一度に解決しようとすると挫折しやすい。だからこそ、${SPREAD_FIVE[3].label}の「${names(f3)}」が示す立ち位置——受け止め方や態度——を意識しながら、一つずつ向き合っていきましょう。`
  );

  paragraphs.push(
    `具体的なアクションとしては、次の3点をおすすめします。(1) 週に一度、「事実」と「感情」を分けて紙に書き出す。これだけで頭の中が整理され、次の一手が見えやすくなります。(2) 相手がいる場合は、要望を並べるのではなく「一番してほしいこと1つ」に絞って伝える。複数の要望は相手を混乱させるだけです。(3) 決断を急がない。後で示す目安の日付の前後1週間を「様子見の期間」として設け、自分の気持ちと周囲の反応を観察してください。`
  );

  if (profile.partnerBirth) {
    paragraphs.push(
      `あの人の生年月日も入れてくれたから、ふたりの関係性についても見てみたよ。「自分だけが頑張ってる」って感じること、ない？もしあるなら、それを言葉にして伝えてみて。相手も同じように感じてることがあるかもしれないし、話すことで初めて共有できる課題ってあるからね。`
    );
  } else {
    paragraphs.push(
      `あの人の生年月日は入ってないから、今回はあなた自身の気持ちや行動を中心に読んだよ。もしふたりの相性とかもっと深く知りたくなったら、また来てね。あの人の情報も入れてくれたら、関係性のヒントをもっと具体的に伝えられるから。`
    );
  }

  paragraphs.push(
    `最後にれんから伝えたいのは、「ひとりで抱え込まなくていいよ」ってこと。カードは道しるべ。最終的に選ぶのはあなた自身だけど、今日のカードが少しでもヒントになったら嬉しいな。小さな一歩でいいから、動いてみてね。応援してるよ。`
  );

  return `<section class="pr-sec"><h3>れんからのまとめ</h3>${paragraphs.map((p) => `<p>${escapeHtml(p)}</p>`).join("")}</section>`;
}

function datesSection(milestones) {
  const items = milestones
    .map(
      (m) =>
        `<li><strong>${escapeHtml(m.dateStr)}</strong> — ${escapeHtml(m.label)}。この前後1週間を「様子を見て微調整する期間」としてください。</li>`
    )
    .join("");
  return `<section class="pr-sec"><h3>流れが来やすい時期</h3><p>以下は、カードの並びとご入力内容から算出した目安です。</p><ul class="pr-date-list">${items}</ul></section>`;
}

/**
 * @param {import("./tarot-deck.js").TarotCard[]} threeCards
 * @param {import("./tarot-deck.js").TarotCard[]} fiveCards
 */
function buildReadingHtml(profile, threeCards, fiveCards) {
  const seedStr = [
    profile.concern,
    profile.selfBirth,
    profile.partnerBirth || "",
    ...threeCards.map((c) => c.id),
    ...fiveCards.map((c) => c.id),
  ].join("|");

  const milestones = deriveMilestoneDates(seedStr);

  let cardsHtml = "";
  cardsHtml += '<section class="pr-sec"><h3>3枚スプレッド — 現状・障害・アドバイス</h3>';
  SPREAD_THREE.forEach((def, i) => {
    const card = threeCards[i];
    if (!card) return;
    cardsHtml += `<div class="pr-card-block"><div class="pr-card-block__title">${escapeHtml(def.label)}：${escapeHtml(card.nameJa)}</div>${expandedCardParagraph(def, card, profile)}</div>`;
  });
  cardsHtml += "</section>";

  cardsHtml += '<section class="pr-sec"><h3>5枚スプレッド — 核心から示唆まで</h3>';
  SPREAD_FIVE.forEach((def, i) => {
    const card = fiveCards[i];
    if (!card) return;
    cardsHtml += `<div class="pr-card-block"><div class="pr-card-block__title">${escapeHtml(def.label)}：${escapeHtml(card.nameJa)}</div>${expandedCardParagraph(def, card, profile)}</div>`;
  });
  cardsHtml += "</section>";

  const inputBlock = "";

  const html =
    `<div class="pr-reading-root">` +
    inputBlock +
    cardsHtml +
    partnerSection(profile) +
    synthesisSection(profile, threeCards, fiveCards) +
    datesSection(milestones) +
`</div>`;

  return html;
}

function readProfileFromDom() {
  const concern = document.getElementById("concern")?.value || "";
  const selfBirth = document.getElementById("self-birth")?.value || "";
  const partnerBirth = document.getElementById("partner-birth")?.value || "";
  return {
    concern,
    selfBirth,
    partnerBirth,
    age: ageFromBirth(selfBirth),
  };
}

function validateIntro(profile, setError) {
  if (!profile.concern.trim()) {
    setError("悩み・聞きたいことを入力してください。");
    return false;
  }
  if (profile.concern.trim().length < 8) {
    setError("もう少しだけ具体的に書いてください（8文字以上）。");
    return false;
  }
  if (!profile.selfBirth) {
    setError("あなたの生年月日を選んでください。");
    return false;
  }
  if (!parseISODate(profile.selfBirth)) {
    setError("生年月日の形式が正しくありません。");
    return false;
  }
  setError("");
  return true;
}

const state = {
  pile: [],
  three: [],
  five: [],
  profile: null,
};


function wireButtons() {
  const btnStart = document.getElementById("btn-start");
  const btnToFive = document.getElementById("btn-to-five");
  const btnFinish = document.getElementById("btn-finish");
  const statusIntro = document.getElementById("shuffle-intro");
  const statusFive = document.getElementById("shuffle-five");
  const errEl = document.getElementById("form-error");

  const setError = (msg) => {
    if (errEl) errEl.textContent = msg;
  };

  btnStart?.addEventListener("click", () => {
    const profile = readProfileFromDom();
    if (!validateIntro(profile, setError)) return;
    state.profile = profile;
    btnStart.disabled = true;
    fakeShuffleDelay(520, statusIntro, "デッキをシャッフルしています…", () => {
      const deck = shuffleDeck(buildFullDeck());
      state.pile = deck;
      state.three = state.pile.splice(0, 3);
      state.five = [];
      renderSpread(document.getElementById("spread-three"), SPREAD_THREE, state.three);
      showPhase("phase-three");
    });
  });

  btnToFive?.addEventListener("click", () => {
    btnToFive.disabled = true;
    fakeShuffleDelay(560, statusFive, "残りのカードをシャッフルしています…", () => {
      state.pile = shuffleDeck(state.pile);
      state.five = state.pile.splice(0, 5);
      renderSpread(document.getElementById("spread-five"), SPREAD_FIVE, state.five);
      showPhase("phase-five");
    });
  });

  btnFinish?.addEventListener("click", () => {
    const profile = state.profile || readProfileFromDom();
    const html = buildReadingHtml(profile, state.three, state.five);
    const box = document.getElementById("summary-body");
    if (box) box.innerHTML = html;
    showPhase("phase-summary");
  });
}

showPhase("phase-intro");
wireButtons();
