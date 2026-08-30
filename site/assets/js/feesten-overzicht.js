(function () {
  const root = document.querySelector("[data-feesten-overzicht]");
  const list = document.getElementById("feesten-lijst");
  const hint = document.getElementById("feesten-rang-hint");
  if (!root || !list) return;

  const MODES = ["kerkelijk", "burgerlijk", "rang", "naam"];
  const STORAGE = "feesten-rangschikking";
  const MONTHS = [
    "",
    "januari",
    "februari",
    "maart",
    "april",
    "mei",
    "juni",
    "juli",
    "augustus",
    "september",
    "oktober",
    "november",
    "december",
  ];
  const RANG_ORDER = {
    grote: 0,
    "heer-moeder": 1,
    apostelen: 2,
    overig: 3,
    paascyclus: 4,
    omlijsting: 5,
  };
  const RANG_LABEL = {
    grote: "Grote feesten",
    "heer-moeder": "Feesten van de Heer en de Moeder Gods",
    apostelen: "Apostelen",
    overig: "Overige feesten",
    paascyclus: "Paascyclus",
    omlijsting: "Voorfeest, nafeest en synaxis",
  };
  const HINTS = {
    kerkelijk: "Van 1 september tot 31 augustus, zoals het synaxarion.",
    burgerlijk:
      "Van januari tot december, op de feestdatum (niet de vierdatum).",
    rang: "Eerst de grote feesten, daarna naar gewicht.",
    naam: "Op de Nederlandse naam, zoals het namenregister.",
  };

  const items = Array.from(list.querySelectorAll("li[data-feest]"));

  function cycleBucket(el) {
    const c = el.dataset.cyclus || "jaar";
    if (c === "wekelijks") return 2;
    if (c === "paascyclus") return 1;
    return 0;
  }

  function parseMmdd(mmdd) {
    if (!mmdd || !/^\d{2}-\d{2}$/.test(mmdd)) return [99, 99];
    return [parseInt(mmdd.slice(0, 2), 10), parseInt(mmdd.slice(3, 5), 10)];
  }

  function kerkMonth(m) {
    return (m + 12 - 9) % 12;
  }

  function rangWeight(el) {
    const r = el.dataset.rang || "overig";
    return r in RANG_ORDER ? RANG_ORDER[r] : 9;
  }

  function cmpParts(a, b) {
    const n = Math.max(a.length, b.length);
    for (let i = 0; i < n; i++) {
      const x = a[i];
      const y = b[i];
      if (x === y) continue;
      if (typeof x === "number" && typeof y === "number") return x - y;
      return String(x).localeCompare(String(y), "nl");
    }
    return 0;
  }

  function sortKey(el, mode) {
    const [m, d] = parseMmdd(el.dataset.mmdd || "");
    const naam = el.dataset.naam || "";
    const rang = rangWeight(el);
    const bucket = cycleBucket(el);
    const sortering = el.dataset.sortering || "";
    if (mode === "naam") {
      return [naam.toLocaleLowerCase("nl"), bucket, kerkMonth(m), d, rang];
    }
    if (mode === "rang") {
      return [rang, sortering, naam];
    }
    if (bucket !== 0) {
      return [bucket, sortering, rang, naam];
    }
    if (mode === "burgerlijk") {
      return [0, m, d, rang, naam];
    }
    return [0, kerkMonth(m), d, rang, naam];
  }

  function groupKey(el, mode) {
    if (mode === "naam") {
      const naam = (el.dataset.naam || "").trim();
      const ch = naam.charAt(0).toLocaleUpperCase("nl");
      return ch || "#";
    }
    if (mode === "rang") {
      return el.dataset.rang || "overig";
    }
    const bucket = cycleBucket(el);
    if (bucket === 1) return "paascyclus";
    if (bucket === 2) return "wekelijks";
    const [m] = parseMmdd(el.dataset.mmdd || "");
    if (m < 1 || m > 12) return "overig";
    return "m-" + String(m).padStart(2, "0");
  }

  function groupLabel(key, mode) {
    if (mode === "naam") return key;
    if (mode === "rang") return RANG_LABEL[key] || key;
    if (key === "paascyclus") return "Paascyclus";
    if (key === "wekelijks") return "Wekelijks";
    if (key.indexOf("m-") === 0) {
      const m = parseInt(key.slice(2), 10);
      return MONTHS[m] || key;
    }
    return key;
  }

  function readMode() {
    const q = new URLSearchParams(window.location.search).get("rangschikking");
    if (MODES.indexOf(q) !== -1) return q;
    try {
      const stored = localStorage.getItem(STORAGE);
      if (MODES.indexOf(stored) !== -1) return stored;
    } catch (_) {}
    return "kerkelijk";
  }

  function writeMode(mode) {
    try {
      localStorage.setItem(STORAGE, mode);
    } catch (_) {}
    const url = new URL(window.location.href);
    if (mode === "kerkelijk") url.searchParams.delete("rangschikking");
    else url.searchParams.set("rangschikking", mode);
    const want = url.pathname + url.search + url.hash;
    if (want !== window.location.pathname + window.location.search + window.location.hash) {
      window.history.replaceState({}, "", want);
    }
  }

  function apply(mode) {
    const sorted = items.slice().sort((a, b) =>
      cmpParts(sortKey(a, mode), sortKey(b, mode))
    );
    list.innerHTML = "";
    let prev = "";
    sorted.forEach((el) => {
      const key = groupKey(el, mode);
      if (key !== prev) {
        const li = document.createElement("li");
        li.className = "entry-list-groep";
        li.setAttribute("role", "presentation");
        li.textContent = groupLabel(key, mode);
        list.appendChild(li);
        prev = key;
      }
      list.appendChild(el);
    });
    document.querySelectorAll("[data-feesten-rangschikking]").forEach((btn) => {
      btn.setAttribute(
        "aria-pressed",
        btn.dataset.feestenRangschikking === mode ? "true" : "false"
      );
    });
    if (hint) hint.textContent = HINTS[mode] || HINTS.kerkelijk;
  }

  let mode = readMode();
  writeMode(mode);
  apply(mode);

  document.querySelectorAll("[data-feesten-rangschikking]").forEach((btn) => {
    btn.addEventListener("click", () => {
      mode = btn.dataset.feestenRangschikking || "kerkelijk";
      writeMode(mode);
      apply(mode);
    });
  });
})();
