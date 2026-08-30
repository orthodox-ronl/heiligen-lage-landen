(function () {
  const input = document.getElementById("heiligen-zoek");
  const table = document.getElementById("heiligen-table");
  const colHead = document.getElementById("heiligen-col-head");
  const dataEl = document.getElementById("heiligen-data");
  const empty = document.getElementById("heiligen-zoek-leeg");
  const root = document.querySelector("[data-heiligen-index]");
  const kaartWrap = document.getElementById("heiligen-kaart-wrap");
  const kaartBalk = document.getElementById("heiligen-kaart-balk");
  const aantalEl = document.getElementById("heiligen-aantal");
  if (!input || !table || !dataEl) return;

  const MONTHS_SHORT = [
    "",
    "jan",
    "feb",
    "mrt",
    "apr",
    "mei",
    "jun",
    "jul",
    "aug",
    "sep",
    "okt",
    "nov",
    "dec",
  ];
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

  let entries = [];
  try {
    let parsed = JSON.parse(dataEl.textContent || "[]");
    // Hugo kan de payload soms als JSON-string inbedden.
    if (typeof parsed === "string") parsed = JSON.parse(parsed);
    entries = Array.isArray(parsed) ? parsed : [];
  } catch (_) {
    entries = [];
  }
  entries = entries.map((e) => {
    const out = { ...e };
    if (!Array.isArray(out.alternatief)) out.alternatief = [];
    if (!Array.isArray(out.plaats_ids)) out.plaats_ids = [];
    if (!Array.isArray(out.plaatsen)) out.plaatsen = [];
    if (!out.selectie) out.selectie = "nader-onderzoek";
    return out;
  });

  let sortMode = "naam";
  let selectieMode = "kalender";
  let weergaveMode = "lijst";
  let kaartOpen = false;
  let kaartOpenAtScroll = 0;
  try {
    const stored = localStorage.getItem("heiligen-sort");
    if (stored === "naam" || stored === "datum" || stored === "plaats") {
      sortMode = stored;
    }
    const sel = localStorage.getItem("heiligen-selectie");
    if (sel === "kalender" || sel === "alles") selectieMode = sel;
    const view = localStorage.getItem("heiligen-weergave");
    if (view === "lijst" || view === "kaart") weergaveMode = view;
    const open = localStorage.getItem("heiligen-kaart-open");
    if (open === "1") kaartOpen = true;
  } catch (_) {}
  const params = new URLSearchParams(window.location.search);
  if (params.get("weergave") === "kaart") weergaveMode = "kaart";
  if (params.get("weergave") === "lijst") weergaveMode = "lijst";
  if (params.get("toon") === "alles") selectieMode = "alles";
  if (params.get("toon") === "kalender") selectieMode = "kalender";

  function siteBase() {
    const fromBody = document.body && document.body.getAttribute("data-base");
    if (fromBody) {
      return fromBody.endsWith("/") ? fromBody : fromBody + "/";
    }
    return "/";
  }

  function siteUrl(path) {
    const rel = String(path || "").replace(/^\//, "");
    try {
      return new URL(rel, siteBase()).href;
    } catch (_) {
      return rel;
    }
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function dayNumber(mmdd) {
    if (!mmdd || !/^\d{2}-\d{2}$/.test(mmdd)) return "";
    return String(parseInt(mmdd.slice(3), 10));
  }

  function shortFeestdatum(mmdd) {
    if (!mmdd || !/^\d{2}-\d{2}$/.test(mmdd)) return "";
    const m = parseInt(mmdd.slice(0, 2), 10);
    return `${dayNumber(mmdd)} ${MONTHS_SHORT[m] || ""}`.trim();
  }

  function vierdatumOldHtml(mmdd) {
    const label = shortFeestdatum(mmdd);
    if (!label) return "";
    return (
      `<span class="vierdatum-oud" tabindex="0" data-info-tip="vierdatum-oud" ` +
      `title="Datum op de oude kalender">(${escapeHtml(label)})</span>`
    );
  }

  function feestdatumHtml(e) {
    const fd = e.feestdatum || "";
    if (!fd) return "";
    const oud = e.vierdatum_oud || "";
    const fdHtml = `<a href="${escapeHtml(datumHref(fd))}">${escapeHtml(
      shortFeestdatum(fd)
    )}</a>`;
    if (!oud || oud === fd) return fdHtml;
    return `${fdHtml} ${vierdatumOldHtml(oud)}`;
  }

  function datumHref(mmdd) {
    if (!mmdd) return "";
    try {
      return new URL(`datum/?dag=${mmdd}`, siteBase()).href;
    } catch (_) {
      return `/datum/?dag=${mmdd}`;
    }
  }

  function zoekHay(e) {
    const plaatsNamen = (e.plaatsen || []).map((p) => p.naam).join(" ");
    return [
      e.naam,
      ...(e.alternatief || []),
      ...(e.plaats_ids || []),
      plaatsNamen,
      e.locatie_zoek || "",
      e.feestdatum || "",
      e.selectie || "",
      selectieLabel(e),
    ]
      .join(" ")
      .toLocaleLowerCase("nl");
  }

  function plaatsHtml(e) {
    const items = e.plaatsen || [];
    if (!items.length) return "";
    return items
      .map((p) => {
        const cls = p.soort === "streek" ? ' class="meta-streek"' : "";
        return `<span${cls}>${escapeHtml(p.naam)}</span>`;
      })
      .join(", ");
  }

  function selectieOf(e) {
    return e.selectie || "nader-onderzoek";
  }

  function selectieLabel(e) {
    const sel = selectieOf(e);
    if (sel === "kandidaat-schrappen") return "kandidaat";
    if (sel === "nader-onderzoek") return "nader onderzoek";
    return "";
  }

  function naamCell(e) {
    const icoon = e.icoon
      ? `<img class="list-icoon" src="${escapeHtml(siteUrl(e.icoon))}" alt="" width="28" height="28">`
      : "";
    const alts =
      e.alternatief && e.alternatief.length
        ? `<span class="meta">ook ${escapeHtml(e.alternatief.join(", "))}</span>`
        : "";
    const cat = selectieLabel(e);
    const catHtml = cat
      ? `<span class="meta heiligen-selectie">${escapeHtml(cat)}</span>`
      : "";
    return (
      `<span class="heiligen-namen">${icoon}` +
      `<a href="${escapeHtml(siteUrl(e.url))}">${escapeHtml(e.naam)}</a>${alts}${catHtml}</span>`
    );
  }

  function groepKopHtml(label) {
    return (
      `<div class="list-month-break heiligen-groep" role="separator" aria-label="${escapeHtml(label)}">` +
      `<span class="list-month-break-label">${escapeHtml(label)}</span></div>`
    );
  }

  function inSelectie(e) {
    if (selectieMode === "kalender") return selectieOf(e) === "voldoet";
    return true;
  }

  function filteredEntries() {
    const q = input.value.trim().toLocaleLowerCase("nl");
    return entries.filter((e) => inSelectie(e) && (!q || zoekHay(e).includes(q)));
  }

  function pinColHead() {
    const head = document.querySelector(".heiligen-sticky-head");
    if (!head || !colHead) return;
    const bottom = head.getBoundingClientRect().bottom;
    document.documentElement.style.setProperty(
      "--heiligen-col-top",
      `${Math.round(bottom)}px`
    );
  }

  function persist(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (_) {}
  }

  function syncKaartLayout() {
    const open = weergaveMode === "kaart" || kaartOpen;
    if (root) {
      root.dataset.weergave = weergaveMode;
      root.dataset.selectie = selectieMode;
    }
    if (kaartWrap) {
      kaartWrap.hidden = !open;
      kaartWrap.classList.toggle("is-open", open);
      kaartWrap.classList.toggle("is-kaart-view", weergaveMode === "kaart");
    }
    if (kaartBalk) {
      kaartBalk.setAttribute("aria-expanded", open ? "true" : "false");
      kaartBalk.hidden = weergaveMode === "kaart";
    }
    document.dispatchEvent(
      new CustomEvent("heiligen-kaart-layout", {
        detail: { open: open, view: weergaveMode },
      })
    );
  }

  function updateKaartBalk(nPlaatsen) {
    if (!kaartBalk) return;
    const n = nPlaatsen || 0;
    const woord = n === 1 ? "plaats" : "plaatsen";
    if (weergaveMode === "kaart") {
      kaartBalk.textContent = `Kaart van plaatsen · ${n} ${woord}`;
      return;
    }
    if (kaartOpen) {
      kaartBalk.textContent = `Kaart verbergen · ${n} ${woord}`;
    } else {
      kaartBalk.textContent = `Kaart van plaatsen · ${n} ${woord}`;
    }
  }

  function updateColHead() {
    if (!colHead) return;
    colHead.classList.remove("is-sort-naam", "is-sort-datum", "is-sort-plaats");
    colHead.classList.add(`is-sort-${sortMode}`);
    if (sortMode === "datum") {
      colHead.innerHTML =
        `<span role="columnheader">Dag</span>` +
        `<span role="columnheader">Heiligen</span>` +
        `<span role="columnheader">Plaatsen</span>`;
    } else if (sortMode === "plaats") {
      colHead.innerHTML =
        `<span role="columnheader">Plaats</span>` +
        `<span role="columnheader">Heiligen</span>` +
        `<span role="columnheader">Feestdatum</span>`;
    } else {
      colHead.innerHTML =
        `<span role="columnheader">Naam</span>` +
        `<span role="columnheader">Plaatsen</span>` +
        `<span role="columnheader">Feestdatum</span>`;
    }
  }

  function monthBreakHtml(label) {
    return (
      `<div class="list-month-break" role="separator" aria-label="${escapeHtml(label)}">` +
      `<span class="list-month-break-label">${escapeHtml(label)}</span></div>`
    );
  }

  function renderNaam(rows) {
    const groepen = [
      {
        label: "In de kalender",
        rows: rows.filter((e) => selectieOf(e) === "voldoet"),
      },
      {
        label: "Nader onderzoek",
        rows: rows.filter((e) => selectieOf(e) === "nader-onderzoek"),
      },
      {
        label: "Kandidaat (niet in de kalender)",
        rows: rows.filter((e) => selectieOf(e) === "kandidaat-schrappen"),
      },
    ];
    const zichtbaar = groepen.filter((g) => g.rows.length);
    const toonKop = selectieMode === "alles" && zichtbaar.length > 1;
    let html = "";
    for (const g of zichtbaar) {
      if (toonKop) html += groepKopHtml(g.label);
      const sorted = g.rows
        .slice()
        .sort((a, b) => a.naam.localeCompare(b.naam, "nl"));
      html += sorted
        .map((e) => {
          const fdHtml = feestdatumHtml(e);
          return (
            `<div class="heiligen-row is-sort-naam" role="row">` +
            `<div role="cell">${naamCell(e)}</div>` +
            `<div role="cell">${plaatsHtml(e)}</div>` +
            `<div role="cell">${fdHtml}</div>` +
            `</div>`
          );
        })
        .join("");
    }
    return html;
  }

  function renderDatum(rows) {
    const byDay = new Map();
    for (const e of rows) {
      const fd = e.feestdatum || "";
      if (!fd) continue;
      if (!byDay.has(fd)) byDay.set(fd, []);
      byDay.get(fd).push(e);
    }
    const days = Array.from(byDay.keys()).sort();
    let html = "";
    let prevMonth = "";
    for (const fd of days) {
      const mm = fd.slice(0, 2);
      const monthNum = parseInt(mm, 10);
      if (prevMonth !== mm) {
        html += monthBreakHtml(MONTHS[monthNum] || mm);
      }
      prevMonth = mm;
      const group = byDay
        .get(fd)
        .slice()
        .sort((a, b) => a.naam.localeCompare(b.naam, "nl"));
      const plaatsen = [];
      const seen = new Set();
      for (const e of group) {
        for (const p of e.plaatsen || []) {
          const key = p.id || p.naam;
          if (seen.has(key)) continue;
          seen.add(key);
          plaatsen.push(p);
        }
      }
      const plaatsStr = plaatsen
        .map((p) => {
          const cls = p.soort === "streek" ? ' class="meta-streek"' : "";
          return `<span${cls}>${escapeHtml(p.naam)}</span>`;
        })
        .join(", ");
      html +=
        `<div class="heiligen-row is-sort-datum" role="row">` +
        `<div class="heiligen-cell-dag" role="cell">` +
        `<a href="${escapeHtml(datumHref(fd))}">${dayNumber(fd)}</a></div>` +
        `<div role="cell">${group.map((e) => naamCell(e)).join(" ")}</div>` +
        `<div role="cell">${plaatsStr}</div>` +
        `</div>`;
    }
    return html;
  }

  function renderPlaats(rows) {
    const byPlaats = new Map();
    for (const e of rows) {
      const plaatsen = e.plaatsen || [];
      if (!plaatsen.length) {
        const key = "";
        if (!byPlaats.has(key)) {
          byPlaats.set(key, { label: "—", soort: "", entries: [] });
        }
        byPlaats.get(key).entries.push(e);
        continue;
      }
      for (const p of plaatsen) {
        const key = p.id || p.naam;
        if (!byPlaats.has(key)) {
          byPlaats.set(key, {
            label: p.naam,
            soort: p.soort || "",
            entries: [],
          });
        }
        byPlaats.get(key).entries.push(e);
      }
    }
    const keys = Array.from(byPlaats.keys()).sort((a, b) => {
      const la = byPlaats.get(a).label;
      const lb = byPlaats.get(b).label;
      return la.localeCompare(lb, "nl");
    });
    return keys
      .map((key) => {
        const bucket = byPlaats.get(key);
        const group = bucket.entries
          .slice()
          .sort((a, b) => a.naam.localeCompare(b.naam, "nl"));
        const seen = new Set();
        const unique = [];
        for (const e of group) {
          if (seen.has(e.url)) continue;
          seen.add(e.url);
          unique.push(e);
        }
        const datums = Array.from(
          new Set(unique.map((e) => e.feestdatum).filter(Boolean))
        ).sort();
        const datumHtml = datums
          .map((fd) => {
            const entry = unique.find((e) => e.feestdatum === fd);
            return entry ? feestdatumHtml(entry) : "";
          })
          .filter(Boolean)
          .join(", ");
        const label =
          bucket.soort === "streek"
            ? `<em class="meta-streek">${escapeHtml(bucket.label)}</em>`
            : escapeHtml(bucket.label);
        return (
          `<div class="heiligen-row is-sort-plaats" role="row">` +
          `<div role="cell">${label}</div>` +
          `<div role="cell">${unique.map((e) => naamCell(e)).join(" ")}</div>` +
          `<div role="cell">${datumHtml}</div>` +
          `</div>`
        );
      })
      .join("");
  }

  function apply() {
    const rows = filteredEntries();
    updateColHead();
    document.querySelectorAll("[data-heiligen-sort]").forEach((btn) => {
      btn.setAttribute(
        "aria-pressed",
        btn.dataset.heiligenSort === sortMode ? "true" : "false"
      );
    });
    document.querySelectorAll("[data-heiligen-selectie]").forEach((btn) => {
      btn.setAttribute(
        "aria-pressed",
        btn.dataset.heiligenSelectie === selectieMode ? "true" : "false"
      );
    });
    document.querySelectorAll("[data-heiligen-weergave]").forEach((btn) => {
      btn.setAttribute(
        "aria-pressed",
        btn.dataset.heiligenWeergave === weergaveMode ? "true" : "false"
      );
    });
    if (aantalEl) aantalEl.textContent = String(rows.length);
    let html = "";
    if (sortMode === "datum") html = renderDatum(rows);
    else if (sortMode === "plaats") html = renderPlaats(rows);
    else html = renderNaam(rows);
    table.innerHTML = html || "";
    const shown = table.querySelectorAll(".heiligen-row").length;
    if (empty) empty.hidden = shown > 0;

    const visiblePlaatsen = new Set();
    const saintUrls = [];
    rows.forEach((e) => {
      saintUrls.push(e.url);
      (e.plaats_ids || []).forEach((id) => visiblePlaatsen.add(id));
    });
    updateKaartBalk(visiblePlaatsen.size);
    syncKaartLayout();
    pinColHead();
    document.dispatchEvent(
      new CustomEvent("heiligen-filter", {
        detail: {
          query: input.value.trim().toLocaleLowerCase("nl"),
          plaatsIds: Array.from(visiblePlaatsen),
          saintUrls: saintUrls,
        },
      })
    );
  }

  document.querySelectorAll("[data-heiligen-sort]").forEach((btn) => {
    btn.addEventListener("click", () => {
      sortMode = btn.dataset.heiligenSort || "naam";
      persist("heiligen-sort", sortMode);
      apply();
    });
  });

  document.querySelectorAll("[data-heiligen-selectie]").forEach((btn) => {
    btn.addEventListener("click", () => {
      selectieMode = btn.dataset.heiligenSelectie || "kalender";
      persist("heiligen-selectie", selectieMode);
      apply();
    });
  });

  document.querySelectorAll("[data-heiligen-weergave]").forEach((btn) => {
    btn.addEventListener("click", () => {
      weergaveMode = btn.dataset.heiligenWeergave || "lijst";
      persist("heiligen-weergave", weergaveMode);
      if (weergaveMode === "kaart") kaartOpen = true;
      if (weergaveMode === "kaart" || kaartOpen) {
        kaartOpenAtScroll = window.scrollY;
      }
      apply();
    });
  });

  if (kaartBalk) {
    kaartBalk.addEventListener("click", () => {
      if (weergaveMode === "kaart") return;
      kaartOpen = !kaartOpen;
      persist("heiligen-kaart-open", kaartOpen ? "1" : "0");
      if (kaartOpen) kaartOpenAtScroll = window.scrollY;
      apply();
    });
  }

  window.addEventListener(
    "scroll",
    () => {
      pinColHead();
      if (weergaveMode === "kaart" || !kaartOpen) return;
      if (window.scrollY < kaartOpenAtScroll + 80) return;
      kaartOpen = false;
      persist("heiligen-kaart-open", "0");
      apply();
    },
    { passive: true }
  );

  document.addEventListener("heiligen-plaats-zoek", (ev) => {
    const naam = (ev.detail && ev.detail.naam) || "";
    if (!naam) return;
    input.value = naam;
    apply();
  });

  const plaats = (params.get("plaats") || "").trim();
  if (plaats && !input.value) input.value = plaats;

  window.addEventListener("resize", pinColHead);
  input.addEventListener("input", apply);
  apply();
})();
