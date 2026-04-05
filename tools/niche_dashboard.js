(function () {
  var catalogMonthly = 2000;
  var IDEAS = [];
  var META = {};
  var TOP20 = new Set();
  var LOW_COMP = new Set();
  var PATTERNS = {};
  var PRIORITY = {};

  function applyPayload(data) {
    META = data.meta || {};
    PATTERNS = META.patterns || {};
    TOP20 = new Set(META.top20 || []);
    LOW_COMP = new Set(META.low_competition || []);
    PRIORITY = META.priority || {};
    if (typeof data.default_monthly_jpy === "number") catalogMonthly = data.default_monthly_jpy;
    IDEAS = (data.ideas || []).map(function (it) {
      return {
        id: Number(it.id),
        category: it.category,
        title: it.title,
        sell: Number(it.sell),
        comp: Number(it.comp),
        recur: Number(it.recur),
        total: Number(it.sell) + Number(it.comp) + Number(it.recur),
      };
    });
    rebuildCategoryOptions();
  }

  function rebuildCategoryOptions() {
    var catSel = document.getElementById("cat");
    var cur = catSel.value;
    catSel.innerHTML = '<option value="">すべて</option>';
    var cats = [...new Set(IDEAS.map(function (x) { return x.category; }))];
    cats.sort();
    cats.forEach(function (c) {
      var o = document.createElement("option");
      o.value = c;
      o.textContent = c;
      catSel.appendChild(o);
    });
    if ([...catSel.options].some(function (o) { return o.value === cur; })) catSel.value = cur;
  }

  function patternLabels(id) {
    var out = [];
    var plabs = META.pattern_labels || {};
    Object.keys(PATTERNS).forEach(function (k) {
      var arr = PATTERNS[k];
      if (arr && arr.indexOf(id) !== -1) out.push({ key: k, name: plabs[k] || k });
    });
    return out;
  }

  function passesPattern(id, pk) {
    if (!pk) return true;
    var arr = PATTERNS[pk];
    return arr && arr.indexOf(id) !== -1;
  }

  function getFiltered() {
    var q = (document.getElementById("q").value || "").trim().toLowerCase();
    var cat = document.getElementById("cat").value;
    var minT = document.getElementById("minTotal").value;
    var onlyTop = document.getElementById("onlyTop20").checked;
    var onlyP = document.getElementById("onlyPri").checked;
    var onlyL = document.getElementById("onlyLow").checked;
    var pat = document.getElementById("pattern").value;
    var minNum = null;
    if (minT !== "" && !isNaN(Number(minT))) minNum = Number(minT);
    return IDEAS.filter(function (row) {
      if (onlyTop && !TOP20.has(row.id)) return false;
      if (
        onlyP &&
        PRIORITY[row.id] === undefined &&
        PRIORITY[String(row.id)] === undefined
      ) {
        return false;
      }
      if (onlyL && !LOW_COMP.has(row.id)) return false;
      if (cat && row.category !== cat) return false;
      if (minNum !== null && row.total < minNum) return false;
      if (!passesPattern(row.id, pat)) return false;
      if (q) {
        var hay = (row.title + " " + row.category + " " + row.id).toLowerCase();
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    });
  }

  function sortRows(rows, key) {
    var copy = rows.slice();
    if (key === "total-desc") {
      copy.sort(function (a, b) {
        return b.total - a.total || b.recur - a.recur || b.comp - a.comp || a.id - b.id;
      });
    } else if (key === "sell-desc") {
      copy.sort(function (a, b) {
        return b.sell - a.sell || b.total - a.total || a.id - b.id;
      });
    } else if (key === "comp-desc") {
      copy.sort(function (a, b) {
        return b.comp - a.comp || b.total - a.total || a.id - b.id;
      });
    } else if (key === "recur-desc") {
      copy.sort(function (a, b) {
        return b.recur - a.recur || b.total - a.total || a.id - b.id;
      });
    } else if (key === "id-asc") {
      copy.sort(function (a, b) {
        return a.id - b.id;
      });
    } else if (key === "title-asc") {
      copy.sort(function (a, b) {
        return a.title.localeCompare(b.title, "ja");
      });
    }
    return copy;
  }

  function priOrder(row) {
    var v = PRIORITY[row.id];
    if (v === undefined) v = PRIORITY[String(row.id)];
    return v;
  }

  function render() {
    var sortKey = document.getElementById("sort").value;
    var showArc = document.getElementById("toggleArchetype").checked;
    var rows = sortRows(getFiltered(), sortKey);
    var tb = document.getElementById("tbody");
    tb.innerHTML = "";
    document.getElementById("thArc").style.display = showArc ? "" : "none";
    rows.forEach(function (row) {
      var tr = document.createElement("tr");
      var badges = [];
      if (TOP20.has(row.id)) badges.push('<span class="badge badge-top">TOP20</span>');
      var po = priOrder(row);
      if (po !== undefined) badges.push('<span class="badge badge-pri">着手' + po + "</span>");
      if (LOW_COMP.has(row.id)) badges.push('<span class="badge badge-low">薄め</span>');
      var pl = patternLabels(row.id);
      var pcell = pl.map(function (p) { return p.name; }).join("・") || "—";
      var pHtml =
        '<td class="num">' +
        row.id +
        "</td>" +
        '<td class="cat">' +
        escapeHtml(row.category) +
        "</td>" +
        "<td>" +
        badges.join("") +
        escapeHtml(row.title) +
        "</td>" +
        '<td class="num">' +
        row.sell +
        "</td>" +
        '<td class="num">' +
        row.comp +
        "</td>" +
        '<td class="num">' +
        row.recur +
        "</td>" +
        '<td class="num total">' +
        row.total +
        "</td>" +
        '<td class="num"><a class="sub-link" href="/checkout/idea/' +
        row.id +
        '">¥' +
        Number(catalogMonthly).toLocaleString("ja-JP") +
        "/月</a></td>";
      if (showArc) {
        pHtml +=
          '<td style="font-size:0.85rem;color:var(--muted)">' +
          escapeHtml(pcell) +
          "</td>";
      }
      tr.innerHTML = pHtml;
      tb.appendChild(tr);
    });
    document.getElementById("count").textContent =
      "表示 " + rows.length + " / " + IDEAS.length + " 件（ideas_catalog.json）";
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function toCsv() {
    var sortKey = document.getElementById("sort").value;
    var rows = sortRows(getFiltered(), sortKey);
    var headers = [
      "No",
      "カテゴリ",
      "題名",
      "売りやすさ",
      "競争の薄さ",
      "継続化",
      "合計",
      "月額円",
      "購読URL",
      "TOP20",
      "着手順",
      "競争薄め候補",
      "継続パターン"
    ];
    var origin =
      typeof location !== "undefined" &&
      location.origin &&
      location.origin !== "null"
        ? location.origin
        : "";
    var lines = [headers.join(",")];
    rows.forEach(function (row) {
      var pl = patternLabels(row.id)
        .map(function (x) {
          return x.name;
        })
        .join("|");
      var subUrl = origin ? origin + "/checkout/idea/" + row.id : "";
      var po = priOrder(row);
      var cols = [
        row.id,
        csvCell(row.category),
        csvCell(row.title),
        row.sell,
        row.comp,
        row.recur,
        row.total,
        catalogMonthly,
        csvCell(subUrl),
        TOP20.has(row.id) ? 1 : 0,
        po != null ? po : "",
        LOW_COMP.has(row.id) ? 1 : 0,
        csvCell(pl),
      ];
      lines.push(cols.join(","));
    });
    return "\uFEFF" + lines.join("\r\n");
  }

  function csvCell(s) {
    var t = String(s);
    if (/[",\r\n]/.test(t)) return '"' + t.replace(/"/g, '""') + '"';
    return t;
  }

  function wireEvents() {
    document.getElementById("q").addEventListener("input", render);
    document.getElementById("cat").addEventListener("change", render);
    document.getElementById("sort").addEventListener("change", render);
    document.getElementById("minTotal").addEventListener("input", render);
    document.getElementById("onlyTop20").addEventListener("change", render);
    document.getElementById("onlyPri").addEventListener("change", render);
    document.getElementById("onlyLow").addEventListener("change", render);
    document.getElementById("pattern").addEventListener("change", render);
    document.getElementById("toggleArchetype").addEventListener("change", render);
    document.getElementById("csv").addEventListener("click", function () {
      var blob = new Blob([toCsv()], { type: "text/csv;charset=utf-8" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download =
        "niche_ideas_" + new Date().toISOString().slice(0, 10) + ".csv";
      a.click();
      URL.revokeObjectURL(a.href);
    });
  }

  function loadIdeas() {
    fetch("/api/ideas")
      .then(function (r) {
        if (!r.ok) throw new Error("api");
        return r.json();
      })
      .then(function (data) {
        applyPayload(data);
        wireEvents();
        render();
      })
      .catch(function () {
        document.getElementById("tbody").innerHTML =
          '<tr><td colspan="9" style="color:#f0a6a6;padding:1rem;">カタログを読み込めません。' +
          "<strong>http://127.0.0.1:5000/dashboard</strong> のようにサーバー経由で開いてください。</td></tr>";
        document.getElementById("count").textContent = "—";
      });
  }

  loadIdeas();
})();
