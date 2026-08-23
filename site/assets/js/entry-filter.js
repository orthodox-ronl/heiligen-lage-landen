(function () {
  const input = document.getElementById("heiligen-zoek");
  const table = document.getElementById("heiligen-table");
  const colHead = document.getElementById("heiligen-col-head");
  const dataEl = document.getElementById("heiligen-data");
  const empty = document.getElementById("heiligen-zoek-leeg");
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
    return out;
  });

  let sortMode = "naam";
  try {
    const stored = localStorage.getItem("heiligen-sort");
    if (stored === "naam" || stored === "datum" || stored === "plaats") {
      sortMode = stored;
    }
  } catch (_) {}

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

  function naamCell(e) {
    const icoon = e.icoon
      ? `<img class="list-icoon" src="${escapeHtml(siteUrl(e.icoon))}" alt="" width="28" height="28">`
      : "";
    const alts =
      e.alternatief && e.alternatief.length
        ? `<span class="meta">ook ${escapeHtml(e.alternatief.join(", "))}</span>`
        : "";
    return (
      `<span class="heiligen-namen">${icoon}` +
      `<a href="${escapeHtml(siteUrl(e.url))}">${escapeHtml(e.naam)}</a>${alts}</span>`
    );
  }

  function filteredEntries() {
    const q = input.value.trim().toLocaleLowerCase("nl");
    return entries.filter((e) => !q || zoekHay(e).includes(q));
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
    const sorted = rows.slice().sort((a, b) => a.naam.localeCompare(b.naam, "nl"));
    return sorted
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
      if (prevMonth && prevMonth !== mm) {
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
    let html = "";
    if (sortMode === "datum") html = renderDatum(rows);
    else if (sortMode === "plaats") html = renderPlaats(rows);
    else html = renderNaam(rows);
    table.innerHTML = html || "";
    const shown = table.querySelectorAll(".heiligen-row").length;
    if (empty) empty.hidden = shown > 0;

    const visiblePlaatsen = new Set();
    rows.forEach((e) => {
      (e.plaats_ids || []).forEach((id) => visiblePlaatsen.add(id));
    });
    document.dispatchEvent(
      new CustomEvent("heiligen-filter", {
        detail: {
          query: input.value.trim().toLocaleLowerCase("nl"),
          plaatsIds: Array.from(visiblePlaatsen),
        },
      })
    );
  }

  document.querySelectorAll("[data-heiligen-sort]").forEach((btn) => {
    btn.addEventListener("click", () => {
      sortMode = btn.dataset.heiligenSort || "naam";
      try {
        localStorage.setItem("heiligen-sort", sortMode);
      } catch (_) {}
      apply();
    });
  });

  const params = new URLSearchParams(window.location.search);
  const plaats = (params.get("plaats") || "").trim();
  if (plaats && !input.value) input.value = plaats;

  input.addEventListener("input", apply);
  apply();
})();
