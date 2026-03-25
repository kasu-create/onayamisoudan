const MAJOR_ARCANA = [
  "The Fool",
  "The Magician",
  "The High Priestess",
  "The Empress",
  "The Emperor",
  "The Hierophant",
  "The Lovers",
  "The Chariot",
  "Strength",
  "The Hermit",
  "Wheel of Fortune",
  "Justice",
  "The Hanged Man",
  "Death",
  "Temperance",
  "The Devil",
  "The Tower",
  "The Star",
  "The Moon",
  "The Sun",
  "Judgement",
  "The World",
];

const RANKS = [
  "Ace",
  "Two",
  "Three",
  "Four",
  "Five",
  "Six",
  "Seven",
  "Eight",
  "Nine",
  "Ten",
  "Page",
  "Knight",
  "Queen",
  "King",
];

const SUITS = ["Wands", "Cups", "Swords", "Pentacles"];

const cards = (() => {
  const data = [];
  MAJOR_ARCANA.forEach((name) =>
    data.push({ title: name, subtitle: "Major Arcana" })
  );
  SUITS.forEach((suit) =>
    RANKS.forEach((rank) =>
      data.push({ title: `${rank} of ${suit}`, subtitle: "Minor Arcana" })
    )
  );
  return data.map((c, i) => ({
    ...c,
    no: String(i + 1).padStart(2, "0"),
    file: `./assets/cards/${String(i + 1).padStart(2, "0")}_${slugify(c.title)}.svg`,
  }));
})();

function slugify(v) {
  return v.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

const drawBtn = document.getElementById("draw-one");
const toggleBtn = document.getElementById("toggle-list");
const drawResult = document.getElementById("draw-result");
const gallerySection = document.getElementById("gallery-section");
const gallery = document.getElementById("gallery");

drawBtn.addEventListener("click", drawOne);
toggleBtn.addEventListener("click", toggleGallery);

renderGallery();

function drawOne() {
  const i = Math.floor(Math.random() * cards.length);
  const c = cards[i];
  drawResult.innerHTML = `
    <img src="${c.file}" alt="${c.title}" loading="lazy" />
    <div class="name">${c.no}. ${c.title}</div>
    <div>${c.subtitle}</div>
  `;
}

function toggleGallery() {
  gallerySection.classList.toggle("hidden");
  toggleBtn.textContent = gallerySection.classList.contains("hidden")
    ? "78枚を表示"
    : "一覧を閉じる";
}

function renderGallery() {
  const frag = document.createDocumentFragment();
  cards.forEach((c) => {
    const item = document.createElement("article");
    item.className = "card";
    item.innerHTML = `
      <img src="${c.file}" alt="${c.title}" loading="lazy" />
      <p>${c.no}. ${c.title}</p>
    `;
    frag.appendChild(item);
  });
  gallery.appendChild(frag);
}
