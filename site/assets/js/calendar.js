(() => {
  const STORAGE_KEY = "kalender-stijl";
  const YEAR_KEY = "kalender-jaar";
  const INTRO_KEY = "site-intro-gezien";
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
  /** Korte maandnaam voor kalender-popover (3 letters). */
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
  /** ISO-weekdag 1=ma … 7=zo */
  const WEEKDAYS = [
    "",
    "Maandag",
    "Dinsdag",
    "Woensdag",
    "Donderdag",
    "Vrijdag",
    "Zaterdag",
    "Zondag",
  ];
  const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

  function siteBase() {
    const fromBody = document.body && document.body.getAttribute("data-base");
    if (fromBody) {
      return fromBody.endsWith("/") ? fromBody : fromBody + "/";
    }
    const path = window.location.pathname;
    if (path.endsWith("/")) return window.location.origin + path;
    const slash = path.lastIndexOf("/");
    return window.location.origin + path.slice(0, slash + 1);
  }

  function assetUrl(rel) {
    return new URL(rel.replace(/^\//, ""), siteBase()).href;
  }

  /** Stabiele URL naar een uitleg-onderwerp: site/content/uitleg/<id>.md */
  function achtergrondUrl(id) {
    return assetUrl(`uitleg/${id}/`);
  }

  function achtergrondLink(id, text, className) {
    const cls = className || "text-link";
    return (
      `<a class="${cls}" href="${achtergrondUrl(id)}" data-achtergrond="${id}">` +
      `${text}</a>`
    );
  }

  function getStyle() {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get("stijl");
    if (fromQuery === "juliaans" || fromQuery === "gregoriaans") {
      try {
        localStorage.setItem(STORAGE_KEY, fromQuery);
      } catch (_) {}
      return fromQuery;
    }
    try {
      return localStorage.getItem(STORAGE_KEY) || "gregoriaans";
    } catch (_) {
      return "gregoriaans";
    }
  }

  function setStyle(style) {
    try {
      localStorage.setItem(STORAGE_KEY, style);
    } catch (_) {}
    document.querySelectorAll(".style-btn[data-style]").forEach((btn) => {
      btn.setAttribute("aria-pressed", btn.dataset.style === style ? "true" : "false");
    });
  }

  function julianGregorianOffsetDays(year) {
    return Math.floor(year / 100) - Math.floor(year / 400) - 2;
  }

  function mmddFromDate(d) {
    return (
      String(d.getMonth() + 1).padStart(2, "0") +
      "-" +
      String(d.getDate()).padStart(2, "0")
    );
  }

  function addDays(d, n) {
    const x = new Date(d.getFullYear(), d.getMonth(), d.getDate());
    x.setDate(x.getDate() + n);
    return x;
  }

  function dateFromMmdd(year, mmdd) {
    const [m, d] = mmdd.split("-").map(Number);
    return new Date(year, m - 1, d);
  }

  /** Meeus’ Juliaans Pascha → wereldlijke datum. Spiegel van scripts/kalender.py. */
  function orthodoxPascha(year) {
    const a = year % 4;
    const b = year % 7;
    const c = year % 19;
    const d = (19 * c + 15) % 30;
    const e = (2 * a + 4 * b - d + 34) % 7;
    const month = Math.floor((d + e + 114) / 31);
    const day = ((d + e + 114) % 31) + 1;
    return addDays(new Date(year, month - 1, day), julianGregorianOffsetDays(year));
  }

  /** Slavische toon 1–8 (Moskou): Thomaszondag = 1; Lichte Week = 1. */
  function octoechosToon(d) {
    const civil = new Date(d.getFullYear(), d.getMonth(), d.getDate());
    let pascha = orthodoxPascha(civil.getFullYear());
    if (civil < pascha) pascha = orthodoxPascha(civil.getFullYear() - 1);
    const thomas = addDays(pascha, 7);
    if (civil >= pascha && civil < thomas) return 1;
    const utcCivil = Date.UTC(civil.getFullYear(), civil.getMonth(), civil.getDate());
    const utcThomas = Date.UTC(thomas.getFullYear(), thomas.getMonth(), thomas.getDate());
    const days = Math.round((utcCivil - utcThomas) / 86400000);
    return ((((Math.floor(days / 7) % 8) + 8) % 8) + 1);
  }

  /** Home, datumpagina en jaarkalender rekenen in wereldlijke (Gregoriaanse) datums. */
  function todayMmdd(_style) {
    return mmddFromDate(new Date());
  }

  function civilTodayMmdd() {
    return mmddFromDate(new Date());
  }

  function mmddInRange(mmdd, van, tot) {
    if (!van || !tot) return false;
    if (van <= tot) return van <= mmdd && mmdd <= tot;
    return mmdd >= van || mmdd <= tot;
  }

  function isoWeekdayFromMmdd(mmdd, year) {
    const js = dateFromMmdd(year, mmdd).getDay();
    return js === 0 ? 7 : js;
  }

  function liturgicalToCivil(year, mmdd) {
    return addDays(dateFromMmdd(year, mmdd), julianGregorianOffsetDays(year));
  }

  function civilToLiturgical(year, mmdd) {
    return addDays(dateFromMmdd(year, mmdd), -julianGregorianOffsetDays(year));
  }

  function liturgicalMmddOnCivil(civilMmdd, year, style) {
    if (style !== "juliaans") return civilMmdd;
    return mmddFromDate(civilToLiturgical(year, civilMmdd));
  }

  /** Wereldlijke MM-DD in `year` waarop een vaste feestdatum valt. */
  function civilMmddsForLiturgical(mmdd, year, style) {
    if (!mmdd) return [];
    if (style !== "juliaans") {
      return mmddExistsInYear(mmdd, year) ? [mmdd] : [];
    }
    const out = [];
    for (const y of [year - 1, year]) {
      const civil = liturgicalToCivil(y, mmdd);
      if (civil.getFullYear() === year) out.push(mmddFromDate(civil));
    }
    return out;
  }

  function iterPeriodMmdds(van, tot) {
    const days = [];
    if (!van || !tot) return days;
    const leap = 2024;
    const start = dateFromMmdd(leap, van);
    let end = dateFromMmdd(leap, tot);
    const wrap = start > end;
    if (wrap) end = new Date(leap, 11, 31);
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      days.push(mmddFromDate(d));
    }
    if (wrap) {
      const end2 = dateFromMmdd(leap, tot);
      for (let d = new Date(leap, 0, 1); d <= end2; d.setDate(d.getDate() + 1)) {
        days.push(mmddFromDate(d));
      }
    }
    return days;
  }

  function weekdagRelatiefMmdds(entry, year, style) {
    if (!entry || entry.vorm !== "weekdag_relatief") return [];
    const occ =
      style === "juliaans" ? entry.occurrences_oud : entry.occurrences;
    const v = (occ || {})[String(year)];
    if (!v) return [];
    return Array.isArray(v) ? v : [v];
  }

  function entryMatchesMmdd(entry, mmdd, year, style, allEntries) {
    if (!entry || !mmdd) return false;
    if (entry.vorm === "weekdagen") {
      if (isWeeklyFastSuppressed(allEntries || [], mmdd, year, style)) {
        return false;
      }
      return (entry.weekdagen || []).includes(isoWeekdayFromMmdd(mmdd, year));
    }
    if (entry.van && entry.tot && entry.vorm === "periode") {
      return mmddInRange(
        liturgicalMmddOnCivil(mmdd, year, style),
        entry.van,
        entry.tot
      );
    }
    if (entry.period_occurrences) {
      const p = entry.period_occurrences[String(year)];
      if (!p) return false;
      return mmddInRange(mmdd, p.van, p.tot);
    }
    if (entry.cyclus === "paascyclus" && entry.occurrences) {
      return entry.occurrences[String(year)] === mmdd;
    }
    if (entry.vorm === "weekdag_relatief") {
      return weekdagRelatiefMmdds(entry, year, style).includes(mmdd);
    }
    return civilMmddsForLiturgical(entry.feestdatum, year, style).includes(mmdd);
  }

  function isWeeklyFastSuppressed(entries, mmdd, year, style) {
    return (entries || []).some((e) => {
      if (!e || e.vorm === "weekdagen") return false;
      const suppresses =
        e.onderdrukt_wekelijks_vasten ||
        (e.soort === "vasten" && e.vorm !== "weekdagen");
      if (!suppresses) return false;
      if (e.van && e.tot && e.vorm === "periode") {
        return mmddInRange(
          liturgicalMmddOnCivil(mmdd, year, style),
          e.van,
          e.tot
        );
      }
      if (e.period_occurrences) {
        const p = e.period_occurrences[String(year)];
        if (!p) return false;
        return mmddInRange(mmdd, p.van, p.tot);
      }
      if (e.cyclus === "paascyclus" && e.occurrences) {
        return e.occurrences[String(year)] === mmdd;
      }
      if (e.vorm === "weekdag_relatief") {
        return weekdagRelatiefMmdds(e, year, style).includes(mmdd);
      }
      return civilMmddsForLiturgical(e.feestdatum, year, style).includes(mmdd);
    });
  }

  function entriesOnMmdd(entries, mmdd, style, year) {
    return (entries || []).filter((e) =>
      entryMatchesMmdd(e, mmdd, year, style, entries)
    );
  }

  /** Spiegel van scripts/vasten.py (period_daily_base / mix_vastenniveau).
   *  Norm: data/regels/vasten.yaml
   */
  const VASTEN_COMPARE_RANK = {
    streng: 0,
    wijn_olie: 1,
    lichter: 1,
    vis: 2,
    vrij: 3,
  };
  const VASTEN_LABELS = {
    streng: "streng",
    wijn_olie: "wijn en olie",
    vis: "vis",
    lichter: "lichter",
    vrij: "vastenvrij",
  };
  const VASTEN_UITLEG = {
    streng: "Geen vlees, zuivel, vis, wijn of olie.",
    wijn_olie: "Wijn en plantaardige olie zijn toegestaan; vis niet.",
    vis: "Vis, wijn en olie zijn toegestaan; vlees en zuivel niet.",
    lichter: "Alleen vlees is uitgesloten (zoals in de Boterweek, waar zuivel wel mag).",
    vrij: "Geen vasten, bijvoorbeeld in de Lichte Week, met Kerst of Theofanie.",
  };

  function entryNaam(entry) {
    return (entry && (entry.naam || (entry.namen && entry.namen.primair))) || "";
  }

  function isWeeklyEntry(entry) {
    return entry && entry.vorm === "weekdagen";
  }

  function isPeriodEntry(entry) {
    if (!entry || isWeeklyEntry(entry)) return false;
    if (entry.vorm === "periode" || entry.vorm === "periode_hybride") return true;
    if (entry.van && entry.tot) return true;
    if (entry.period_occurrences) return true;
    return false;
  }

  function entryObservances(entry) {
    if (entry.observances && entry.observances.length) return entry.observances;
    if (entry.soort === "heilige") return ["heilige"];
    if (entry.soort === "vasten") return ["vasten"];
    return ["feest"];
  }

  function moreLenientNiveau(a, b) {
    return VASTEN_COMPARE_RANK[a] >= VASTEN_COMPARE_RANK[b] ? a : b;
  }

  function stricterNiveau(a, b) {
    return VASTEN_COMPARE_RANK[a] <= VASTEN_COMPARE_RANK[b] ? a : b;
  }

  function vastenTekst(opts) {
    const niveau = opts.niveau;
    const bron = opts.bron;
    if (niveau === "vrij") return `Vastenvrij — ${bron}`;
    const label = VASTEN_LABELS[niveau] || niveau;
    let line = `Vasten: ${label} — ${bron}`;
    if (opts.versoepeldDoor) {
      line += `, versoepeld (${opts.versoepeldDoor})`;
    } else if (opts.weekend && opts.weekday === 6) {
      line += " (zaterdag)";
    } else if (opts.weekend && opts.weekday === 7) {
      line += " (zondag)";
    }
    return line;
  }

  function namedVastenPeriode(entry) {
    if (!entry || isWeeklyEntry(entry) || !isPeriodEntry(entry)) return null;
    return entry;
  }

  function packVasten(niveau, tekstOpts, periodeEntry) {
    return {
      niveau,
      tekst: vastenTekst(tekstOpts),
      periode: namedVastenPeriode(periodeEntry),
    };
  }

  function periodDailyBase(entry, weekday, inGroteWeek, mmdd) {
    const tag = entry.vastenniveau || "streng";
    if (tag === "vrij") return { niveau: "vrij", weekend: false };
    if (tag === "lichter" && entry.soort === "vasten") {
      let base;
      let weekend = false;
      if (weekday === 6 || weekday === 7) {
        base = "vis";
        weekend = true;
      } else if (weekday === 2 || weekday === 4) {
        base = "wijn_olie";
      } else {
        base = "streng";
      }
      if (
        entry.id === "geboorte-vasten" &&
        mmdd &&
        mmdd >= "12-20" &&
        mmdd <= "12-24" &&
        VASTEN_COMPARE_RANK[base] > VASTEN_COMPARE_RANK.wijn_olie
      ) {
        base = "wijn_olie";
      }
      return { niveau: base, weekend };
    }
    if (tag === "lichter") return { niveau: "lichter", weekend: false };
    if (
      (weekday === 6 || weekday === 7) &&
      VASTEN_COMPARE_RANK[tag] === VASTEN_COMPARE_RANK.streng &&
      !inGroteWeek
    ) {
      return { niveau: "wijn_olie", weekend: true };
    }
    return { niveau: tag, weekend: false };
  }

  function mixVastenniveau(dayEntries, weekday, mmdd) {
    const periods = (dayEntries || []).filter(
      (e) =>
        isPeriodEntry(e) &&
        (e.soort === "vasten" || e.vastenniveau)
    );
    const weekly = (dayEntries || []).filter(isWeeklyEntry);
    const dayFeasts = (dayEntries || []).filter(
      (e) => e.vastenniveau && !isPeriodEntry(e) && !isWeeklyEntry(e)
    );

    const vrijPeriods = periods.filter((e) => e.vastenniveau === "vrij");
    if (vrijPeriods.length) {
      return packVasten(
        "vrij",
        { niveau: "vrij", bron: entryNaam(vrijPeriods[0]) },
        vrijPeriods[0]
      );
    }

    const inGroteWeek = periods.some((e) => e.id === "grote-week");

    if (periods.length) {
      let baseEntry = periods[0];
      for (const e of periods) {
        const rank = VASTEN_COMPARE_RANK[e.vastenniveau || "streng"];
        const best = VASTEN_COMPARE_RANK[baseEntry.vastenniveau || "streng"];
        if (rank < best) baseEntry = e;
      }
      const daily = periodDailyBase(baseEntry, weekday, inGroteWeek, mmdd);
      let base = daily.niveau;
      let weekend = daily.weekend;
      const relaxers = dayFeasts.filter(
        (e) => VASTEN_COMPARE_RANK[e.vastenniveau] > VASTEN_COMPARE_RANK[base]
      );
      let versoepeld = null;
      let effective = base;
      if (relaxers.length) {
        versoepeld = relaxers[0];
        for (const e of relaxers) {
          if (
            VASTEN_COMPARE_RANK[e.vastenniveau] >
            VASTEN_COMPARE_RANK[versoepeld.vastenniveau]
          ) {
            versoepeld = e;
          }
        }
        effective = versoepeld.vastenniveau;
      }
      if (inGroteWeek && VASTEN_COMPARE_RANK[effective] > VASTEN_COMPARE_RANK.wijn_olie) {
        effective = "wijn_olie";
      }
      return packVasten(
        effective,
        {
          niveau: effective,
          bron: entryNaam(baseEntry),
          versoepeldDoor: versoepeld ? entryNaam(versoepeld) : null,
          weekend: weekend && !versoepeld,
          weekday,
        },
        baseEntry
      );
    }

    const tightening = dayFeasts.filter((e) =>
      entryObservances(e).includes("vasten")
    );
    const relaxing = dayFeasts.filter(
      (e) => !entryObservances(e).includes("vasten")
    );

    if (tightening.length) {
      let chosen = tightening[0];
      for (const e of tightening) {
        if (
          VASTEN_COMPARE_RANK[e.vastenniveau] <
          VASTEN_COMPARE_RANK[chosen.vastenniveau]
        ) {
          chosen = e;
        }
      }
      let niveau = chosen.vastenniveau;
      if (weekly.length) {
        niveau = stricterNiveau(
          niveau,
          weekly[0].vastenniveau || "wijn_olie"
        );
      }
      return packVasten(niveau, { niveau, bron: entryNaam(chosen) }, null);
    }

    if (weekly.length) {
      const weeklyLevel = weekly[0].vastenniveau || "wijn_olie";
      if (relaxing.length) {
        let chosen = relaxing[0];
        for (const e of relaxing) {
          if (
            VASTEN_COMPARE_RANK[e.vastenniveau] >
            VASTEN_COMPARE_RANK[chosen.vastenniveau]
          ) {
            chosen = e;
          }
        }
        const feastLevel = chosen.vastenniveau;
        const effective = moreLenientNiveau(weeklyLevel, feastLevel);
        if (effective === "vrij") {
          return packVasten(
            "vrij",
            { niveau: "vrij", bron: entryNaam(chosen) },
            chosen
          );
        }
        if (VASTEN_COMPARE_RANK[feastLevel] > VASTEN_COMPARE_RANK[weeklyLevel]) {
          return packVasten(
            effective,
            {
              niveau: effective,
              bron: entryNaam(weekly[0]),
              versoepeldDoor: entryNaam(chosen),
            },
            chosen
          );
        }
      }
      return packVasten(
        weeklyLevel,
        {
          niveau: weeklyLevel,
          bron: entryNaam(weekly[0]),
        },
        null
      );
    }

    const vrijFeasts = relaxing.filter((e) => e.vastenniveau === "vrij");
    if (vrijFeasts.length) {
      return packVasten(
        "vrij",
        {
          niveau: "vrij",
          bron: entryNaam(vrijFeasts[0]),
        },
        vrijFeasts[0]
      );
    }
    return null;
  }

  function kindLabel(entry) {
    if (entry.soort === "vasten") {
      if (entry.vorm === "weekdagen") return "Vasten (wekelijks)";
      if (entry.vorm === "periode" || entry.vorm === "periode_hybride") {
        return "Vastenperiode";
      }
      return "Vasten";
    }
    if (entry.cyclus === "paascyclus") return "Paascyclus";
    if (entry.vorm === "weekdag_relatief") return "Feest (weekdag t.o.v. anker)";
    if (entry.soort === "feest") return "Feest";
    return "Heilige";
  }

  function addObservances(set, entry) {
    const obs =
      entry.observances && entry.observances.length
        ? entry.observances
        : [
            entry.soort === "heilige"
              ? "heilige"
              : entry.soort === "vasten"
                ? "vasten"
                : "feest",
          ];
    for (const o of obs) set.add(o);
  }

  function label(mmdd) {
    const [m, d] = mmdd.split("-").map(Number);
    return `${d} ${MONTHS[m]}`;
  }

  function shortLabel(mmdd) {
    const [m, d] = mmdd.split("-").map(Number);
    return `${d} ${MONTHS_SHORT[m]}`;
  }

  function shiftMmdd(mmdd, deltaDays) {
    const [m, d] = mmdd.split("-").map(Number);
    // Schrikkeljaar: 29 februari blijft bereikbaar in de jaarcyclus.
    return mmddFromDate(addDays(new Date(2024, m - 1, d), deltaDays));
  }

  function parseDagParam(raw) {
    if (raw && /^\d{2}-\d{2}$/.test(raw)) return raw;
    return null;
  }

  function parseYearParam(raw, fallback) {
    if (raw && /^\d{4}$/.test(raw)) return parseInt(raw, 10);
    return fallback;
  }

  function parseDatumParam(raw) {
    if (!raw || !/^(\d{4})-(\d{2})-(\d{2})$/.test(raw)) return null;
    const m = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    return { year: parseInt(m[1], 10), mmdd: m[2] + "-" + m[3] };
  }

  let yearBounds = {
    min: new Date().getFullYear() - 2,
    max: new Date().getFullYear() + 5,
  };

  function yearBoundsFromEntries(entries) {
    let min = Infinity;
    let max = -Infinity;
    for (const e of entries || []) {
      for (const map of [e.occurrences, e.period_occurrences]) {
        if (!map) continue;
        for (const key of Object.keys(map)) {
          const y = parseInt(key, 10);
          if (!Number.isFinite(y)) continue;
          if (y < min) min = y;
          if (y > max) max = y;
        }
      }
    }
    const now = new Date().getFullYear();
    return {
      min: Number.isFinite(min) ? min : now - 2,
      max: Number.isFinite(max) ? max : now + 5,
    };
  }

  function clampYear(year) {
    return Math.min(yearBounds.max, Math.max(yearBounds.min, year));
  }

  function mmddExistsInYear(mmdd, year) {
    const [m, d] = mmdd.split("-").map(Number);
    const dt = new Date(year, m - 1, d);
    return (
      dt.getFullYear() === year &&
      dt.getMonth() === m - 1 &&
      dt.getDate() === d
    );
  }

  function getViewDate(style) {
    const params = new URLSearchParams(window.location.search);
    const todayYear = new Date().getFullYear();
    const today = todayMmdd(style);
    const parsed = parseDatumParam(params.get("datum"));
    if (parsed) {
      return { year: clampYear(parsed.year), mmdd: parsed.mmdd };
    }
    let year = parseYearParam(params.get("jaar"), todayYear);
    year = clampYear(year);
    const mmdd = parseDagParam(params.get("dag")) || today;
    return { year, mmdd };
  }

  function isViewToday(style) {
    const view = getViewDate(style);
    return (
      view.year === new Date().getFullYear() &&
      view.mmdd === todayMmdd(style)
    );
  }

  function daySurfaceHref(year, mmdd, style) {
    const isToday =
      year === new Date().getFullYear() && mmdd === todayMmdd(style);
    const stijl = style === "juliaans" ? { stijl: style } : {};
    if (isToday) return pageUrl("", stijl);
    return pageUrl("datum/", { datum: year + "-" + mmdd, ...stijl });
  }

  /** Home = vandaag; andere dagen = /datum/. */
  function redirectDaySurfaceIfNeeded(style) {
    const onHome = Boolean(document.querySelector("[data-home]"));
    const onDatum = Boolean(document.querySelector("[data-datum]"));
    if (!onHome && !onDatum) return false;
    const view = getViewDate(style);
    const isToday = isViewToday(style);
    if (onHome && !isToday) {
      window.location.replace(daySurfaceHref(view.year, view.mmdd, style));
      return true;
    }
    if (onDatum && isToday) {
      window.location.replace(daySurfaceHref(view.year, view.mmdd, style));
      return true;
    }
    return false;
  }

  function ensureCanonicalDatumUrl(style) {
    if (!document.querySelector("[data-datum]")) return;
    const view = getViewDate(style);
    const want = new URL(daySurfaceHref(view.year, view.mmdd, style));
    const here = new URL(window.location.href);
    if (here.pathname !== want.pathname) return;
    if (here.search === want.search) return;
    window.history.replaceState({}, "", want);
  }

  function setViewDate(year, mmdd) {
    const style = getStyle();
    year = clampYear(year);
    const target = daySurfaceHref(year, mmdd, style);
    const here = new URL(window.location.href);
    const next = new URL(target);
    if (here.pathname !== next.pathname) {
      window.location.assign(target);
      return;
    }
    window.history.pushState({}, "", target);
    refresh();
  }

  function shiftViewDate(year, mmdd, delta) {
    const [m, d] = mmdd.split("-").map(Number);
    const next = addDays(new Date(year, m - 1, d), delta);
    return { year: next.getFullYear(), mmdd: mmddFromDate(next) };
  }

  function pageUrl(path, params) {
    const u = new URL(assetUrl(path));
    Object.entries(params || {}).forEach(([k, v]) => {
      if (v != null && v !== "") u.searchParams.set(k, String(v));
    });
    const style = getStyle();
    if (style === "juliaans") u.searchParams.set("stijl", style);
    return u.href;
  }

  async function applyStyle(style) {
    const url = new URL(window.location.href);
    url.searchParams.set("stijl", style);
    // Wereldlijke dag in de URL blijft; Nieuw/Oud verplaatst de vaste feesten.
    window.history.replaceState({}, "", url);
    setStyle(style);
    await refresh();
  }

  function styleToggleHtml(ariaLabel) {
    return (
      `<span class="style-toggle" role="group" aria-label="${ariaLabel || "Kalenderstijl Nieuw/Oud"}">` +
      `<button type="button" data-style="gregoriaans" class="style-btn" title="Schakel naar Nieuwe/Gregoriaanse kalender">Nieuw</button>` +
      `<button type="button" data-style="juliaans" class="style-btn" title="Schakel naar Oude/Juliaanse kalender">Oud</button>` +
      `<button type="button" class="style-btn style-help" data-info-tip="nieuw-oud" title="Uitleg Nieuw/Oud">?</button>` +
      `</span>`
    );
  }

  function fillPageTitleRow(navEl, titleNavInnerHtml, opts) {
    const row = navEl.closest(".page-title-row");
    if (!row) return null;
    const includeStyle = !opts || opts.includeStyleToggle !== false;
    const id = navEl.id || "";
    const dataTitle = navEl.dataset.title || "";
    row.innerHTML =
      `<span class="title-nav"` +
      (id ? ` id="${id}"` : "") +
      (dataTitle ? ` data-title="${dataTitle.replace(/"/g, "&quot;")}"` : "") +
      `>${titleNavInnerHtml}</span>` +
      (includeStyle ? styleToggleHtml("Kalenderstijl Nieuw/Oud") : "");
    setStyle(getStyle());
    wireInfoTips(row);
    return row;
  }

  function dayTitleParts(view, style) {
    const weekday = WEEKDAYS[isoWeekdayFromMmdd(view.mmdd, view.year)] || "";
    const datePart = `${shortLabel(view.mmdd)} ${view.year}`;
    const toon = octoechosToon(dateFromMmdd(view.year, view.mmdd));
    const today = isViewToday(style) ? " (vandaag)" : "";
    return { weekday, datePart, toon, today };
  }

  function dayTitleText(view, style) {
    const p = dayTitleParts(view, style);
    return `${p.weekday}, ${p.datePart}${p.today} (Toon ${p.toon})`;
  }

  function dayTitleHtml(view, style) {
    const p = dayTitleParts(view, style);
    return `${escapeHtml(p.weekday)}, ${escapeHtml(p.datePart)}${escapeHtml(p.today)}`;
  }

  function dayToonHtml(view, style) {
    const p = dayTitleParts(view, style);
    return (
      `<span class="title-toon">(` +
      `<a class="text-link" href="${achtergrondUrl("toon")}" ` +
      `data-achtergrond="toon" data-info-tip="toon">Toon ${p.toon}</a>)</span>`
    );
  }

  function titleNavHtml(opts) {
    const prevDis = opts.prevDisabled ? " disabled" : "";
    const nextDis = opts.nextDisabled ? " disabled" : "";
    const unit = opts.unit || "dag"; // dag | maand | jaar
    const prevTitle =
      unit === "jaar" ? "Vorig jaar" : unit === "maand" ? "Vorige maand" : "Vorige dag";
    const nextTitle =
      unit === "jaar"
        ? "Volgend jaar"
        : unit === "maand"
          ? "Volgende maand"
          : "Volgende dag";
    const prevBody =
      unit === "jaar"
        ? "Ga naar het vorige jaar in deze kalender."
        : unit === "maand"
          ? "Ga naar de vorige maand in het lezingenrooster."
          : "Ga naar de vorige dag.";
    const nextBody =
      unit === "jaar"
        ? "Ga naar het volgende jaar in deze kalender."
        : unit === "maand"
          ? "Ga naar de volgende maand in het lezingenrooster."
          : "Ga naar de volgende dag.";
    return (
      `<button type="button" class="title-step" data-${opts.deltaAttr}="-1" ` +
      `aria-label="${opts.prevLabel}"${prevDis} ` +
      `data-info-tip="nav" data-info-title="${prevTitle}" data-info-body="${prevBody}">‹</button>` +
      `<span class="title-nav-label" tabindex="0" data-info-tip="titel" ` +
      `data-info-unit="${unit}">${opts.titleHtml}</span>` +
      `<button type="button" class="title-step" data-${opts.deltaAttr}="1" ` +
      `aria-label="${opts.nextLabel}"${nextDis} ` +
      `data-info-tip="nav" data-info-title="${nextTitle}" data-info-body="${nextBody}">›</button>` +
      (opts.afterHtml || "")
    );
  }

  function updateHeading(style) {
    const heading = document.getElementById("today-heading");
    if (!heading) return;
    const view = getViewDate(style);
    const navHtml = titleNavHtml({
      titleHtml: dayTitleHtml(view, style),
      afterHtml: dayToonHtml(view, style),
      prevLabel: "Vorige dag",
      nextLabel: "Volgende dag",
      deltaAttr: "day-delta",
      unit: "dag",
      prevDisabled: false,
      nextDisabled: false,
    });
    const row = heading.closest(".page-title-row");
    if (row) {
      // Nieuw/Oud staat in de inhoudsbox, niet in de (wereldlijke) titel.
      fillPageTitleRow(heading, navHtml, { includeStyleToggle: false });
      const fresh = document.getElementById("today-heading");
      if (fresh) wireDaySteps(fresh);
    } else {
      heading.classList.add("title-nav");
      heading.innerHTML = navHtml;
      wireInfoTips(heading);
      wireDaySteps(heading);
    }
  }

  function wireDaySteps(root) {
    (root || document).querySelectorAll("[data-day-delta]").forEach((btn) => {
      if (btn.dataset.boundDay === "1") return;
      btn.dataset.boundDay = "1";
      btn.addEventListener("click", (ev) => {
        ev.preventDefault();
        ev.stopPropagation();
        const delta = Number(btn.dataset.dayDelta);
        if (!delta) return;
        const style = getStyle();
        const view = getViewDate(style);
        const next = shiftViewDate(view.year, view.mmdd, delta);
        if (next.year < yearBounds.min || next.year > yearBounds.max) return;
        setViewDate(next.year, next.mmdd);
      });
    });
  }

  let infoCloseTimer = null;
  let infoAnchor = null;
  let introTimer = null;
  let introActive = false;

  function nieuwOudTitle(style) {
    return style === "juliaans"
      ? "Oude kalender (Juliaans)"
      : "Nieuwe/Gregoriaanse kalender";
  }

  function fillNieuwOudMeer(meer) {
    if (!meer) return;
    meer.hidden = false;
    meer.innerHTML = achtergrondLink("nieuw-oud", "Meer over Nieuw/Oud");
  }

  /** Titel-popover: tekst past bij dag-, maand- of jaarnavigatie. */
  function fillTitelPopover(trigger, title, body, meer) {
    const style = getStyle();
    const unit = (trigger && trigger.dataset.infoUnit) || "dag";
    title.textContent = nieuwOudTitle(style);

    if (unit === "jaar") {
      // Raster is altijd burgerlijk; inhoud hangt van Nieuw/Oud af.
      body.innerHTML =
        `<p>Deze jaarkalender toont burgerlijke datums — zoals op een ` +
        `Nederlandse agenda (1&nbsp;januari is nieuwjaarsdag). Wat er op een ` +
        `dag staat, hangt af van uw keuze Nieuw of Oud: met Nieuw valt Kerst ` +
        `op 25&nbsp;december, met Oud op 7&nbsp;januari.</p>`;
      fillNieuwOudMeer(meer);
      return;
    }

    if (unit === "maand") {
      const monthName = MONTHS[parseInt(roosterMonth, 10)] || "";
      const waar =
        monthName != null && monthName !== ""
          ? `In ${monthName} ${viewYear}`
          : "In deze maand";
      body.innerHTML =
        style === "juliaans"
          ? `<p>${waar} ziet u burgerlijke datums. De inhoud van elke dag ` +
            `volgt de <strong>oude</strong> (Juliaanse) kalender.</p>`
          : `<p>${waar} ziet u burgerlijke datums. De inhoud van elke dag ` +
            `volgt de <strong>nieuwe</strong> (Gregoriaanse) kalender.</p>`;
      fillNieuwOudMeer(meer);
      return;
    }

    // dag (home / datumpagina)
    const view = getViewDate(style);
    const julianOnView = mmddFromDate(
      civilToLiturgical(view.year, view.mmdd)
    );
    const dayPhrase = isViewToday(style)
      ? `Vandaag is het burgerlijk ${label(view.mmdd)}`
      : `Deze dag is burgerlijk ${label(view.mmdd)} ${view.year}`;
    if (style === "juliaans") {
      body.innerHTML =
        `<p>${dayPhrase}. Volgens de oude telling is dat ` +
        `${label(julianOnView)}.</p>` +
        `<p>We tonen hier wat die dag volgens de <strong>oude</strong> ` +
        `(Juliaanse) kalender wordt gevast, gelezen en gevierd.</p>`;
    } else {
      body.innerHTML =
        `<p>${dayPhrase}. ` +
        `(Volgens de oude telling is dat ${label(julianOnView)}.)</p>` +
        `<p>We tonen hier wat die dag volgens de <strong>nieuwe</strong> ` +
        `(Gregoriaanse) kalender wordt gevast, gelezen en gevierd.</p>`;
    }
    fillNieuwOudMeer(meer);
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function dutchEnList(items) {
    const parts = (items || [])
      .map((s) => escapeHtml(String(s || "").trim()))
      .filter(Boolean);
    if (parts.length === 0) return "";
    if (parts.length === 1) return parts[0];
    if (parts.length === 2) return `${parts[0]} en ${parts[1]}`;
    return `${parts.slice(0, -1).join(", ")} en ${parts[parts.length - 1]}`;
  }

  /** Spiegel van scripts/bijbel.py — houd de boekcodes gelijk. */
  const BOEK_OSIS = {
    "1 Joh.": "1JN",
    "2 Joh.": "2JN",
    "3 Joh.": "3JN",
    "1 Kor.": "1CO",
    "2 Kor.": "2CO",
    "1 Petr.": "1PE",
    "2 Petr.": "2PE",
    "1 Tess.": "1TH",
    "2 Tess.": "2TH",
    "1 Tim.": "1TI",
    "2 Tim.": "2TI",
    "Ef.": "EPH",
    "Fil.": "PHP",
    "Gal.": "GAL",
    "Hand.": "ACT",
    "Heb.": "HEB",
    "Jak.": "JAS",
    "Joh.": "JHN",
    "Jud.": "JUD",
    "Kol.": "COL",
    "Luc.": "LUK",
    "Mark.": "MRK",
    "Matt.": "MAT",
    "Rom.": "ROM",
    "Tit.": "TIT",
  };
  const BIJBEL_VERTALINGEN = [
    ["HSV", "HSV"],
    ["NBV", "NBV"],
    ["NBV21", "NBV21"],
    ["BGT", "BGT (Gewone Taal)"],
    ["NBG51", "NBG51"],
    ["NFB", "NFB (Fries)"],
    ["UTT", "UTT (Oekraïens)"],
  ];
  const BIJBEL_STORAGE = "bijbel-vertaling";

  function bibleTranslation() {
    const ids = BIJBEL_VERTALINGEN.map((row) => row[0]);
    try {
      const stored = localStorage.getItem(BIJBEL_STORAGE);
      if (stored && ids.includes(stored)) return stored;
    } catch (_) {}
    return "HSV";
  }

  function osisHoofdstuk(ref) {
    const text = String(ref || "").trim();
    if (!text) return "";
    const lower = text.toLowerCase();
    const boeken = Object.keys(BOEK_OSIS).sort((a, b) => b.length - a.length);
    for (const boek of boeken) {
      if (lower.startsWith(boek.toLowerCase())) {
        const rest = text.slice(boek.length).trim();
        const m = rest.match(/^(\d+)/);
        if (!m) return "";
        return `${BOEK_OSIS[boek]}.${m[1]}`;
      }
    }
    return "";
  }

  function refDelen(ref) {
    const delen = [];
    let buf = "";
    String(ref || "")
      .split(";")
      .forEach((raw) => {
        const piece = raw.trim();
        if (!piece) return;
        if (buf && !osisHoofdstuk(piece)) buf = `${buf}; ${piece}`;
        else if (buf) {
          delen.push(buf);
          buf = piece;
        } else buf = piece;
      });
    if (buf) delen.push(buf);
    return delen;
  }

  function bibleUrl(osis) {
    return `https://www.debijbel.nl/bijbel/${bibleTranslation()}/${osis}`;
  }

  function bibleLinkHtml(ref) {
    return refDelen(ref)
      .map((deel) => {
        const text = escapeHtml(deel);
        const osis = osisHoofdstuk(deel);
        if (!osis) return text;
        return (
          `<a class="bijbel-link" data-osis="${osis}" href="${bibleUrl(osis)}" ` +
          `target="_blank" rel="noopener noreferrer">${text}</a>`
        );
      })
      .join("; ");
  }

  function refsHtml(arr) {
    return (arr || [])
      .map((x) => x.ref)
      .filter(Boolean)
      .map(bibleLinkHtml)
      .join("; ");
  }

  function bijbelVertalingSelectHtml() {
    const cur = bibleTranslation();
    const opts = BIJBEL_VERTALINGEN.map(([id, label]) => {
      const sel = id === cur ? " selected" : "";
      return `<option value="${id}"${sel}>${label}</option>`;
    }).join("");
    return (
      `<p class="bijbel-vertaling-rij">` +
      `<label>Vertaling <select class="bijbel-vertaling">${opts}</select></label>` +
      `</p>`
    );
  }

  function wireBijbelVertaling(root) {
    (root || document).querySelectorAll("select.bijbel-vertaling").forEach((sel) => {
      sel.onchange = () => {
        try {
          localStorage.setItem(BIJBEL_STORAGE, sel.value);
        } catch (_) {}
        document.querySelectorAll("select.bijbel-vertaling").forEach((other) => {
          other.value = sel.value;
        });
        document.querySelectorAll("a.bijbel-link[data-osis]").forEach((a) => {
          a.setAttribute("href", bibleUrl(a.getAttribute("data-osis")));
        });
      };
    });
  }

  function isPopoverFeast(entry) {
    if (!entry) return false;
    if (entry.soort === "heilige") return false;
    if (entry.soort === "vasten") return false;
    if (entry.vorm === "weekdagen") return false;
    return true;
  }

  function isPopoverSaint(entry) {
    return entry && entry.soort === "heilige";
  }

  function vastenBadgeHtml(niveau, interactive) {
    const text = VASTEN_LABELS[niveau] || niveau;
    const tip = interactive
      ? ` tabindex="0" data-info-tip="vasten-niveau" data-info-niveau="${escapeHtml(niveau)}" title="Uitleg ${escapeHtml(text)}"`
      : "";
    return (
      `<span class="vasten-badge vasten-badge-${escapeHtml(niveau)}"${tip}>` +
      `${escapeHtml(text)}</span>`
    );
  }

  function popoverListHtml(items) {
    if (!items.length) return "";
    return (
      `<ul class="day-popover-list">` +
      items.map((n) => `<li>${escapeHtml(n)}</li>`).join("") +
      `</ul>`
    );
  }

  /** Jaarkalender: preview bij hover over een dagcel. */
  function fillKalenderDagPopover(mmdd, titleEl, bodyEl, meerEl) {
    const style = getStyle();
    const year = viewYear;
    const matched = entriesOnMmdd(calendarEntries, mmdd, style, year);
    const feasts = matched
      .filter(isPopoverFeast)
      .map(entryNaam)
      .filter(Boolean)
      .sort((a, b) => a.localeCompare(b, "nl"));
    const saints = matched
      .filter(isPopoverSaint)
      .map(entryNaam)
      .filter(Boolean)
      .sort((a, b) => a.localeCompare(b, "nl"));
    const weekday = isoWeekdayFromMmdd(mmdd, year);
    const vasten = mixVastenniveau(matched, weekday, mmdd);
    const vastenNiveau = vasten ? vasten.niveau : "vrij";

    titleEl.innerHTML =
      `<span class="day-popover-date">${escapeHtml(shortLabel(mmdd))}</span>` +
      vastenBadgeHtml(vastenNiveau);
    if (meerEl) {
      meerEl.hidden = true;
      meerEl.innerHTML = "";
    }

    const items = feasts.concat(saints);
    if (items.length) {
      bodyEl.innerHTML = popoverListHtml(items);
    } else {
      bodyEl.innerHTML =
        `<p class="muted day-popover-empty">Geen feesten of heiligen van de Lage Landen op deze dag. ` +
        achtergrondLink(
          "heiligen",
          "Waarom niet iedere heilige hier staat"
        ) +
        `</p>`;
    }
  }

  function fillInfoPopover(trigger) {
    const body = document.getElementById("info-popover-body");
    const title = document.getElementById("info-popover-title");
    const meer = document.getElementById("info-popover-meer");
    if (!body || !title) return;
    const kind = (trigger && trigger.dataset.infoTip) || "nav";
    if (kind === "kalender-dag") {
      fillKalenderDagPopover(
        trigger.dataset.dayMmdd,
        title,
        body,
        meer
      );
      return;
    }
    if (kind === "toon") {
      title.textContent = "Toon van de week";
      body.innerHTML =
        `<p>Naast de datum staat de toon van de week (1 tot 8) voor de ` +
        `Slavische zangpraktijk. Dat helpt bij de Octoechos; het typikon ` +
        `van uw parochie blijft leidend.</p>`;
      if (meer) {
        meer.hidden = false;
        meer.innerHTML = achtergrondLink("toon", "Meer over de toon");
      }
      return;
    }
    if (kind === "titel") {
      fillTitelPopover(trigger, title, body, meer);
      return;
    }
    if (kind === "heiligen-criterium") {
      title.textContent = "Heiligen van de Lage Landen";
      body.innerHTML =
        `<p>Alleen heiligen die in de Lage Landen hebben gewerkt, of na het ` +
        `schisma de Orthodoxie hier hebben opgebouwd. Niet iedere heilige ` +
        `van de Kerk staat in deze kalender. Patroon van een parochie is ` +
        `daarvoor niet genoeg.</p>`;
      if (meer) {
        meer.hidden = false;
        meer.innerHTML = achtergrondLink(
          "heiligen",
          "Meer over wie erin staat"
        );
      }
      return;
    }
    if (kind === "site") {
      title.textContent = "Over deze kalender";
      body.innerHTML =
        `<p>Praktisch hulpmiddel voor orthodoxe gelovigen in de Lage Landen ` +
        `(vooral de Russische traditie). Gedachtenissen beperken zich tot ` +
        `de Heiligen van de Lage Landen.</p>` +
        `<p>De site is nog jong. Hij ziet er al bruikbaar uit, maar de ` +
        `teksten zijn nog niet nagekeken door mensen die van huis uit ` +
        `orthodox zijn. We zoeken die toets; tot die tijd is dit geen ` +
        `officieel kerkelijk oordeel.</p>`;
      if (meer) {
        meer.hidden = false;
        meer.innerHTML =
          `<a class="text-link" href="${assetUrl("uitleg/")}">Meer uitleg</a>`;
      }
      return;
    }
    if (kind === "betekenis-goedkeuring") {
      title.textContent = "Over deze betekenistekst";
      let items = [];
      try {
        items = JSON.parse(trigger.dataset.goedkeuring || "[]");
      } catch (_) {
        items = [];
      }
      if (!Array.isArray(items) || items.length === 0) {
        let bronnen = [];
        try {
          bronnen = JSON.parse(trigger.dataset.betekenisBronnen || "[]");
        } catch (_) {
          bronnen = [];
        }
        const bronZin = dutchEnList(bronnen);
        if (bronZin) {
          body.innerHTML =
            `<p>Deze uitleg is ontleend aan ${bronZin}. We zoeken nog ` +
            `iemand die van huis uit orthodox is om de tekst te toetsen.</p>`;
        } else {
          body.innerHTML =
            `<p>We zoeken nog iemand die van huis uit orthodox is om deze ` +
            `uitleg te toetsen.</p>`;
        }
      } else {
        const lis = items.map((it) => {
          const naam = escapeHtml(
            String((it && it.naam) || "").trim() || "Onbekend"
          );
          const org = String((it && it.organisatie) || "").trim();
          const opm = String((it && it.opmerking) || "").trim();
          const dat = String((it && it.datum) || "").trim();
          let line = `<strong>${naam}</strong>`;
          if (org) line += ` (${escapeHtml(org)})`;
          if (dat) line += ` — ${escapeHtml(dat)}`;
          if (opm) line += `. ${escapeHtml(opm)}`;
          return `<li>${line}</li>`;
        });
        body.innerHTML =
          `<p>Deze uitleg is goedgekeurd door:</p>` +
          `<ul>${lis.join("")}</ul>`;
      }
      if (meer) {
        meer.hidden = true;
        meer.innerHTML = "";
      }
      return;
    }
    if (kind === "vasten-niveau") {
      const niveau = (trigger && trigger.dataset.infoNiveau) || "vrij";
      const labelText = VASTEN_LABELS[niveau] || niveau;
      const uitleg = VASTEN_UITLEG[niveau] || "";
      title.textContent = labelText;
      body.innerHTML = `<p>${escapeHtml(uitleg)}</p>`;
      if (meer) {
        meer.hidden = false;
        meer.innerHTML = achtergrondLink("vasten", "Meer over vasten");
      }
      return;
    }
    if (kind === "vierdatum-oud") {
      title.textContent = "Oude kalender";
      body.innerHTML =
        `<p>De datum <em>voor</em> de haakjes is de burgerlijke dag ` +
        `(Nederlandse agenda) waarop <strong>nieuwe-kalenderparochies</strong> ` +
        `vieren of vasten.</p>` +
        `<p>Tussen haakjes staat alleen de burgerlijke dag waarop ` +
        `<strong>oude-kalenderparochies</strong> hetzelfde houden. ` +
        `Dat is geen tweede feestdatum: het feest heet in beide kalenders ` +
        `hetzelfde (Kerst blijft 25&nbsp;december).</p>` +
        `<p>Geen haakjes: nieuw en oud vallen op dezelfde burgerlijke dag ` +
        `(Pascha en wat daarvan afhangt).</p>`;
      fillNieuwOudMeer(meer);
      return;
    }
    if (kind === "nieuw-oud") {
      // Knop «?» naast Nieuw/Oud: situatief, geankerd op vandaag.
      const style = getStyle();
      const civilToday = civilTodayMmdd();
      const now = new Date();
      const julianToday = mmddFromDate(
        civilToLiturgical(now.getFullYear(), civilToday)
      );
      title.textContent = nieuwOudTitle(style);
      if (style === "juliaans") {
        body.innerHTML =
          `<p>U heeft de <strong>oude</strong> (Juliaanse) kalender gekozen. ` +
          `Volgens die telling is het vandaag ${label(julianToday)}. ` +
          `Wat u op deze pagina ziet, hoort bij die oude telling — zoals ` +
          `veel Orthodoxe parochies en kloosters die volgen.</p>`;
      } else {
        body.innerHTML =
          `<p>U heeft de <strong>nieuwe</strong> (Gregoriaanse) kalender ` +
          `gekozen. Die valt samen met de burgerlijke datum; vandaag is het ` +
          `${label(civilToday)}. Wat u hier ziet, hoort bij die nieuwe ` +
          `telling.</p>`;
      }
      fillNieuwOudMeer(meer);
      return;
    }
    title.textContent = (trigger && trigger.dataset.infoTitle) || "Navigatie";
    body.innerHTML = `<p>${(trigger && trigger.dataset.infoBody) || ""}</p>`;
    if (meer) {
      meer.hidden = true;
      meer.innerHTML = "";
    }
  }

  function positionInfoPopover(trigger) {
    const dlg = document.getElementById("info-popover");
    if (!dlg || !trigger) return;
    dlg.style.left = "0px";
    dlg.style.top = "0px";
    const gap = 8;
    const rect = trigger.getBoundingClientRect();
    const pop = dlg.getBoundingClientRect();
    let left = rect.left;
    let top = rect.bottom + gap;
    if (left + pop.width > window.innerWidth - 8) {
      left = Math.max(8, window.innerWidth - pop.width - 8);
    }
    if (top + pop.height > window.innerHeight - 8) {
      top = Math.max(8, rect.top - pop.height - gap);
    }
    dlg.style.left = `${Math.max(8, left)}px`;
    dlg.style.top = `${top}px`;
  }

  function cancelIntroTimer() {
    if (introTimer) {
      clearTimeout(introTimer);
      introTimer = null;
    }
    introActive = false;
  }

  function closeInfoPopover() {
    const dlg = document.getElementById("info-popover");
    if (!dlg) return;
    cancelIntroTimer();
    dlg.hidden = true;
    dlg.classList.remove("is-day-preview");
    infoAnchor = null;
  }

  function cancelInfoClose() {
    if (infoCloseTimer) {
      clearTimeout(infoCloseTimer);
      infoCloseTimer = null;
    }
  }

  function scheduleInfoClose() {
    if (introActive) return;
    cancelInfoClose();
    infoCloseTimer = setTimeout(closeInfoPopover, 180);
  }

  function openInfoPopover(trigger) {
    const dlg = document.getElementById("info-popover");
    if (!dlg || !trigger) return;
    cancelInfoClose();
    infoAnchor = trigger;
    dlg.classList.toggle(
      "is-day-preview",
      trigger.dataset.infoTip === "kalender-dag"
    );
    fillInfoPopover(trigger);
    dlg.hidden = false;
    positionInfoPopover(trigger);
    requestAnimationFrame(() => positionInfoPopover(trigger));
  }

  function canHover() {
    try {
      return window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    } catch (_) {
      return true;
    }
  }

  function wireInfoTips(root) {
    (root || document).querySelectorAll("[data-info-tip]").forEach((el) => {
      if (el.dataset.boundInfo === "1") return;
      el.dataset.boundInfo = "1";
      const isKalenderDag = el.dataset.infoTip === "kalender-dag";
      if (isKalenderDag) {
        // Desktop: hover-preview. Telefoon: tik gaat naar de datumpagina.
        if (canHover()) {
          el.addEventListener("mouseenter", () => openInfoPopover(el));
          el.addEventListener("mouseleave", scheduleInfoClose);
        }
        return;
      }
      el.addEventListener("mouseenter", () => openInfoPopover(el));
      el.addEventListener("mouseleave", scheduleInfoClose);
      el.addEventListener("focus", () => openInfoPopover(el));
      el.addEventListener("blur", scheduleInfoClose);
      el.addEventListener("click", (ev) => {
        // Navigatieknoppen (‹ ›) moeten gewoon klikken.
        if (el.classList.contains("title-step")) return;
        ev.preventDefault();
        ev.stopPropagation();
        const dlg = document.getElementById("info-popover");
        if (dlg && !dlg.hidden && infoAnchor === el) {
          closeInfoPopover();
        } else {
          openInfoPopover(el);
        }
      });
    });
    const dlg = document.getElementById("info-popover");
    if (dlg && dlg.dataset.boundHover !== "1") {
      dlg.dataset.boundHover = "1";
      dlg.addEventListener("mouseenter", () => {
        cancelIntroTimer();
        cancelInfoClose();
      });
      dlg.addEventListener("mouseleave", scheduleInfoClose);
    }
  }

  function prefersReducedMotion() {
    try {
      return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    } catch (_) {
      return false;
    }
  }

  function markIntroSeen() {
    try {
      localStorage.setItem(INTRO_KEY, "1");
    } catch (_) {}
  }

  function maybeShowSiteIntro() {
    if (!document.body || document.body.getAttribute("data-home") !== "true") {
      return;
    }
    if (prefersReducedMotion()) return;
    try {
      if (localStorage.getItem(INTRO_KEY) === "1") return;
    } catch (_) {}
    const trigger = document.querySelector(".brand-mark[data-info-tip='site']");
    if (!trigger) return;
    introActive = true;
    markIntroSeen();
    openInfoPopover(trigger);
    introTimer = setTimeout(() => {
      introTimer = null;
      introActive = false;
      closeInfoPopover();
    }, 8000);
  }

  function firstLetter(name) {
    const ch = (name || "").trim().charAt(0).toUpperCase();
    return LETTERS.includes(ch) ? ch : "#";
  }

  async function loadEntries() {
    const url = assetUrl("data/entries.json");
    const res = await fetch(url);
    if (!res.ok) throw new Error(`entries.json (${res.status}) ${url}`);
    return res.json();
  }

  let lezingenIndex = null;

  async function loadLezingenIndex() {
    if (lezingenIndex) return lezingenIndex;
    const url = assetUrl("data/lezingen-dagen.json");
    const res = await fetch(url);
    if (!res.ok) {
      lezingenIndex = { nieuw: {}, oud: {} };
      return lezingenIndex;
    }
    lezingenIndex = await res.json();
    return lezingenIndex;
  }

  function lezingenForDay(year, civilMmdd, style) {
    const stil = style === "juliaans" ? "oud" : "nieuw";
    let keyMmdd = civilMmdd;
    let keyYear = year;
    if (style === "juliaans") {
      const lit = civilToLiturgical(year, civilMmdd);
      keyMmdd = mmddFromDate(lit);
      keyYear = lit.getFullYear();
    }
    const root = lezingenIndex || {};
    return ((root[stil] || {})[String(keyYear)] || {})[keyMmdd] || null;
  }

  function isDayTypeFeast(entry) {
    if (!entry || entry.soort !== "feest") return false;
    if (isWeeklyEntry(entry) || isPeriodEntry(entry)) return false;
    return true;
  }

  function entryHref(entry) {
    return assetUrl((entry.url || "").replace(/^\//, ""));
  }

  function renderVastenClusterHtml(vasten) {
    const niveau = (vasten && vasten.niveau) || "vrij";
    const periode = vasten && vasten.periode;
    const periodeNaam = periode ? entryNaam(periode) : "";
    let periodeHtml = "";
    if (periode && periodeNaam) {
      const href = entryHref(periode);
      periodeHtml =
        ` <span class="today-vasten-periode">(` +
        `<a href="${href}">${escapeHtml(periodeNaam)}</a>)</span>`;
    }
    return (
      `<span class="today-vasten">` +
      vastenBadgeHtml(niveau, true) +
      periodeHtml +
      `</span>`
    );
  }

  function renderDagtypeHtml(matched, lez) {
    const feasts = (matched || [])
      .filter(isDayTypeFeast)
      .filter((e) => entryNaam(e));
    feasts.sort((a, b) => {
      const ac = a.cyclus === "paascyclus" ? 0 : 1;
      const bc = b.cyclus === "paascyclus" ? 0 : 1;
      if (ac !== bc) return ac - bc;
      return entryNaam(a).localeCompare(entryNaam(b), "nl");
    });
    let inner;
    if (feasts.length) {
      inner = feasts
        .map(
          (e) =>
            `<a href="${entryHref(e)}">${escapeHtml(entryNaam(e))}</a>`
        )
        .join(" · ");
    } else if (lez && lez.daglabel) {
      inner = escapeHtml(lez.daglabel);
    } else {
      return "";
    }
    return `<p class="today-dagtype">${inner}</p>`;
  }

  function renderLezingenHtml(lez) {
    if (!lez || (lez.status !== "gevonden" && lez.status !== "geen_liturgie")) {
      return (
        `<div class="day-lezingen" id="day-lezingen">` +
        `<p class="muted">Geen Apostel of Evangelie van de dag bekend.</p></div>`
      );
    }
    if (lez.status === "geen_liturgie") {
      return (
        `<div class="day-lezingen" id="day-lezingen">` +
        `<p class="muted">Geen liturgie met Apostel/Evangelie van de dag.</p></div>`
      );
    }
    const apostel = refsHtml(lez.apostel);
    const evangelie = refsHtml(lez.evangelie);
    if (!apostel && !evangelie) {
      return (
        `<div class="day-lezingen" id="day-lezingen">` +
        `<p class="muted">Geen Apostel of Evangelie van de dag bekend.</p></div>`
      );
    }
    return (
      `<div class="day-lezingen" id="day-lezingen">` +
      `<ul>` +
      (apostel ? `<li><strong>Apostel:</strong> ${apostel}</li>` : "") +
      (evangelie
        ? `<li><strong>Evangelie:</strong> ${evangelie}</li>`
        : "") +
      `</ul>` +
      bijbelVertalingSelectHtml() +
      `</div>`
    );
  }

  function renderHeiligenHtml(matched) {
    const saints = (matched || [])
      .filter((e) => e.soort === "heilige")
      .filter((e) => entryNaam(e))
      .sort((a, b) => entryNaam(a).localeCompare(entryNaam(b), "nl"));
    if (!saints.length) {
      return (
        `<p class="muted today-geen-heilige">` +
        achtergrondLink(
          "heiligen",
          "(Geen feest/gedachtenis van een Heilige van de Lage Landen)"
        ) +
        `</p>`
      );
    }
    const items = saints
      .map((e) => {
        const icoon = e.icoon
          ? `<img class="today-heilige-icoon" src="${assetUrl(e.icoon.replace(/^\//, ""))}" alt="" width="32" height="32">`
          : "";
        return (
          `<li>` +
          icoon +
          `<a href="${entryHref(e)}">${escapeHtml(entryNaam(e))}</a>` +
          `</li>`
        );
      })
      .join("");
    const titel =
      saints.length === 1 ? "Heilige van de dag" : "Heiligen van de dag";
    return (
      `<div class="today-heiligen-blok">` +
      `<h2 class="today-heiligen-title">${titel}</h2>` +
      `<ul class="today-heiligen">${items}</ul>` +
      `</div>`
    );
  }

  function renderToday(entries, style) {
    const cardEntries = document.getElementById("today-entries");
    if (!cardEntries) return;
    updateHeading(style);
    const view = getViewDate(style);
    let bodyHtml;
    if (!mmddExistsInYear(view.mmdd, view.year)) {
      bodyHtml =
        `<div class="today-card-bar">` +
        renderVastenClusterHtml({ niveau: "vrij" }) +
        styleToggleHtml("Kalenderstijl Nieuw/Oud") +
        `</div>` +
        `<p>${label(view.mmdd)} valt niet in ${view.year}.</p>`;
    } else {
      const matched = entriesOnMmdd(entries, view.mmdd, style, view.year);
      const weekday = isoWeekdayFromMmdd(view.mmdd, view.year);
      const vasten =
        mixVastenniveau(matched, weekday, view.mmdd) || { niveau: "vrij" };
      const lez = lezingenForDay(view.year, view.mmdd, style);
      bodyHtml =
        `<div class="today-card-bar">` +
        renderVastenClusterHtml(vasten) +
        styleToggleHtml("Kalenderstijl Nieuw/Oud") +
        `</div>` +
        renderDagtypeHtml(matched, lez) +
        renderLezingenHtml(lez) +
        renderHeiligenHtml(matched);
    }
    cardEntries.innerHTML = bodyHtml;
    setStyle(style);
    wireInfoTips(cardEntries);
    wireBijbelVertaling(cardEntries);
    if (
      document.querySelector("[data-datum]") ||
      document.querySelector("[data-home]")
    ) {
      const site = document.title.includes(" · ")
        ? document.title.slice(document.title.lastIndexOf(" · ") + 3)
        : document.title;
      document.title = `${dayTitleText(view, style)} · ${site}`;
    }
  }

  function isNarrowViewport() {
    return window.matchMedia("(max-width: 40rem)").matches;
  }

  function closeWeergavePanel(prefix) {
    const panel = document.getElementById(`${prefix}-weergave-panel`);
    const trigger = document.getElementById(`${prefix}-weergave-trigger`);
    const overlay = document.getElementById(`${prefix}-weergave-overlay`);
    if (panel) {
      panel.hidden = true;
      panel.classList.remove("is-sheet");
    }
    if (trigger) trigger.setAttribute("aria-expanded", "false");
    if (overlay) {
      overlay.hidden = true;
      overlay.classList.remove("is-open");
    }
  }

  function openWeergavePanel(prefix) {
    const panel = document.getElementById(`${prefix}-weergave-panel`);
    const trigger = document.getElementById(`${prefix}-weergave-trigger`);
    const overlay = document.getElementById(`${prefix}-weergave-overlay`);
    if (!panel) return;
    ["rooster", "synaxarion"].forEach((other) => {
      if (other !== prefix) closeWeergavePanel(other);
    });
    panel.hidden = false;
    if (isNarrowViewport()) {
      panel.classList.add("is-sheet");
      if (overlay) {
        overlay.hidden = false;
        overlay.classList.add("is-open");
      }
    } else {
      panel.classList.remove("is-sheet");
      if (overlay) {
        overlay.hidden = true;
        overlay.classList.remove("is-open");
      }
    }
    if (trigger) trigger.setAttribute("aria-expanded", "true");
  }

  function toggleWeergavePanel(prefix) {
    const panel = document.getElementById(`${prefix}-weergave-panel`);
    if (!panel || panel.hidden) openWeergavePanel(prefix);
    else closeWeergavePanel(prefix);
  }

  function wireWeergavePanel(prefix) {
    const trigger = document.getElementById(`${prefix}-weergave-trigger`);
    const panel = document.getElementById(`${prefix}-weergave-panel`);
    const overlay = document.getElementById(`${prefix}-weergave-overlay`);
    if (!trigger || !panel || trigger.dataset.boundWeergave === "1") return;
    trigger.dataset.boundWeergave = "1";
    trigger.addEventListener("click", () => toggleWeergavePanel(prefix));
    panel.querySelectorAll("[data-weergave-close]").forEach((btn) => {
      btn.addEventListener("click", () => closeWeergavePanel(prefix));
    });
    if (overlay) {
      overlay.addEventListener("click", () => closeWeergavePanel(prefix));
    }
  }

  function closeAllWeergavePanels() {
    closeWeergavePanel("rooster");
    closeWeergavePanel("synaxarion");
  }

  function renderRooster(style) {
    const root = document.getElementById("rooster-tables");
    const actionBar = document.getElementById("rooster-action-bar");
    const panelBody = document.getElementById("rooster-weergave-body");
    const summary = document.getElementById("rooster-weergave-summary");
    const heading = document.getElementById("rooster-heading");
    if (!root || !actionBar) return;

    if (heading) heading.textContent = "Lezingenrooster";
    wireWeergavePanel("rooster");

    const stil = style === "juliaans" ? "oud" : "nieuw";
    const monthNum = parseInt(roosterMonth, 10);
    const monthName = MONTHS[monthNum];

    actionBar.innerHTML =
      `<button type="button" class="title-step" data-month-delta="-1" ` +
      `aria-label="Vorige maand">‹</button>` +
      `<span class="action-bar-label">${monthName} ${viewYear}</span>` +
      `<button type="button" class="title-step" data-month-delta="1" ` +
      `aria-label="Volgende maand">›</button>`;
    wireRoosterMonthSteps(actionBar);

    if (summary) summary.textContent = bibleTranslation();
    if (panelBody) {
      panelBody.innerHTML = bijbelVertalingSelectHtml();
      wireBijbelVertaling(panelBody);
      panelBody.querySelectorAll("select.bijbel-vertaling").forEach((sel) => {
        sel.addEventListener("change", () => {
          const sum = document.getElementById("rooster-weergave-summary");
          if (sum) sum.textContent = bibleTranslation();
        });
      });
    }

    const daysInMonth = new Date(viewYear, monthNum, 0).getDate();
    let html =
      `<div class="table-wrap"><table class="rooster-table">` +
      `<thead><tr>` +
      `<th scope="col">Datum</th>` +
      `<th scope="col">Liturgische dag</th>` +
      `<th scope="col">Apostel</th>` +
      `<th scope="col">Evangelie</th>` +
      `</tr></thead><tbody>`;
    let rows = 0;
    for (let day = 1; day <= daysInMonth; day++) {
      const civilMmdd =
        String(monthNum).padStart(2, "0") + "-" + String(day).padStart(2, "0");
      let keyMmdd = civilMmdd;
      let keyYear = viewYear;
      if (style === "juliaans") {
        const lit = civilToLiturgical(viewYear, civilMmdd);
        keyMmdd = mmddFromDate(lit);
        keyYear = lit.getFullYear();
      }
      const yearBucket =
        ((lezingenIndex || {})[stil] || {})[String(keyYear)] || {};
      const lez = yearBucket[keyMmdd] || null;
      const dagUrl = daySurfaceHref(viewYear, civilMmdd, style);
      let apostel = refsHtml(lez && lez.apostel);
      let evangelie = refsHtml(lez && lez.evangelie);
      const status = (lez && lez.status) || "onbekend";
      if (status === "geen_liturgie") {
        apostel = apostel || "—";
        evangelie = evangelie || "(geen liturgie)";
      } else if (status === "onbekend") {
        apostel = apostel || "—";
        evangelie = evangelie || "—";
      }
      html +=
        `<tr>` +
        `<td><a href="${dagUrl}">${label(civilMmdd)}</a></td>` +
        `<td>${(lez && lez.daglabel) || ""}</td>` +
        `<td>${apostel}</td>` +
        `<td>${evangelie}</td>` +
        `</tr>`;
      rows += 1;
    }
    html += `</tbody></table></div>`;
    root.innerHTML =
      rows > 0
        ? html
        : `<p class="muted">Geen lezingengegevens voor ${monthName} ${viewYear}.</p>`;
  }

  function wireRoosterMonthSteps(root) {
    (root || document).querySelectorAll("[data-month-delta]").forEach((btn) => {
      if (btn.dataset.boundMonth === "1") return;
      btn.dataset.boundMonth = "1";
      btn.addEventListener("click", (ev) => {
        ev.preventDefault();
        ev.stopPropagation();
        if (btn.disabled) return;
        const delta = Number(btn.dataset.monthDelta);
        if (!delta) return;
        let m = parseInt(roosterMonth, 10) + delta;
        let y = viewYear;
        if (m < 1) {
          m = 12;
          y = clampYear(y - 1);
        } else if (m > 12) {
          m = 1;
          y = clampYear(y + 1);
        }
        viewYear = y;
        roosterMonth = String(m).padStart(2, "0");
        try {
          localStorage.setItem(YEAR_KEY, String(viewYear));
        } catch (_) {}
        const url = new URL(window.location.href);
        url.searchParams.set("maand", roosterMonth);
        if (url.searchParams.has("jaar")) {
          url.searchParams.set("jaar", String(viewYear));
        }
        window.history.replaceState({}, "", url);
        renderRooster(getStyle());
      });
    });
  }

  function initRooster(style) {
    if (!document.querySelector("[data-lezingenrooster]")) return;
    const params = new URLSearchParams(window.location.search);
    const m = params.get("maand");
    const y = params.get("jaar");
    if (y && /^\d{4}$/.test(y)) {
      viewYear = clampYear(parseInt(y, 10));
    }
    if (m && /^\d{2}$/.test(m) && Number(m) >= 1 && Number(m) <= 12) {
      roosterMonth = m;
    } else {
      const now = new Date();
      if (viewYear === now.getFullYear()) {
        roosterMonth = String(now.getMonth() + 1).padStart(2, "0");
      }
    }
    renderRooster(style);
  }

  function dayClass(kinds) {
    const hasF = kinds.has("feest");
    const hasH = kinds.has("heilige");
    const hasV = kinds.has("vasten");
    if (hasF && hasH && hasV) return "day-feest-heilige-vasten";
    if (hasF && hasV) return "day-feest-vasten";
    if (hasH && hasV) return "day-heilige-vasten";
    if (hasF && hasH) return "day-beide";
    if (hasV) return "day-vasten";
    if (hasF) return "day-feest";
    if (hasH) return "day-heilige";
    return "";
  }

  let viewYear = new Date().getFullYear();
  let calendarEntries = [];
  let roosterMonth = String(new Date().getMonth() + 1).padStart(2, "0");
  try {
    const stored = localStorage.getItem(YEAR_KEY);
    if (stored) viewYear = parseInt(stored, 10) || viewYear;
  } catch (_) {}

  function markDay(byDay, mmdd, entry) {
    if (!mmdd) return;
    if (!byDay.has(mmdd)) byDay.set(mmdd, new Set());
    addObservances(byDay.get(mmdd), entry);
  }

  function updateKalenderHeading(entries, style) {
    const nav = document.getElementById("kalender-title-nav");
    if (!nav) return;
    const title = nav.dataset.title || "Jaarkalender";
    fillPageTitleRow(
      nav,
      titleNavHtml({
        titleHtml:
          `<span class="kalender-title-word">${title}</span> ` +
          `<span class="year-label">${viewYear}</span>`,
        prevLabel: "Vorig jaar",
        nextLabel: "Volgend jaar",
        deltaAttr: "year-delta",
        unit: "jaar",
        prevDisabled: viewYear <= yearBounds.min,
        nextDisabled: viewYear >= yearBounds.max,
      })
    );
    const fresh = document.getElementById("kalender-title-nav");
    if (fresh) wireYearSteps(fresh, entries, style);
  }

  function wireYearSteps(root, entries, style) {
    (root || document).querySelectorAll("[data-year-delta]").forEach((btn) => {
      if (btn.dataset.boundYear === "1") return;
      btn.dataset.boundYear = "1";
      btn.addEventListener("click", (ev) => {
        ev.preventDefault();
        ev.stopPropagation();
        if (btn.disabled) return;
        const delta = Number(btn.dataset.yearDelta);
        if (!delta) return;
        const next = clampYear(viewYear + delta);
        if (next === viewYear) return;
        viewYear = next;
        try {
          localStorage.setItem(YEAR_KEY, String(viewYear));
        } catch (_) {}
        renderYearGrid(entries, style);
      });
    });
  }

  function renderYearGrid(entries, style) {
    const root = document.getElementById("year-grid");
    if (!root) return;
    updateKalenderHeading(entries, style);

    const byDay = new Map();
    for (const e of entries) {
      if (!e) continue;
      if (e.vorm === "weekdagen") {
        const daysInYear =
          (viewYear % 4 === 0 && viewYear % 100 !== 0) || viewYear % 400 === 0
            ? 366
            : 365;
        for (let i = 0; i < daysInYear; i++) {
          const d = new Date(viewYear, 0, 1 + i);
          const iso = d.getDay() === 0 ? 7 : d.getDay();
          if (!(e.weekdagen || []).includes(iso)) continue;
          const mmdd = mmddFromDate(d);
          if (isWeeklyFastSuppressed(entries, mmdd, viewYear, style)) {
            continue;
          }
          markDay(byDay, mmdd, e);
        }
        continue;
      }
      if (e.period_occurrences) {
        const p = e.period_occurrences[String(viewYear)];
        if (!p) continue;
        const start = dateFromMmdd(viewYear, p.van);
        const end = dateFromMmdd(viewYear, p.tot);
        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
          markDay(byDay, mmddFromDate(d), e);
        }
        continue;
      }
      if (e.vorm === "periode" && e.van && e.tot) {
        for (const lit of iterPeriodMmdds(e.van, e.tot)) {
          for (const civil of civilMmddsForLiturgical(lit, viewYear, style)) {
            markDay(byDay, civil, e);
          }
        }
        continue;
      }
      if (e.cyclus === "paascyclus") {
        markDay(byDay, (e.occurrences || {})[String(viewYear)] || null, e);
        continue;
      }
      if (e.vorm === "weekdag_relatief") {
        for (const mm of weekdagRelatiefMmdds(e, viewYear, style)) {
          markDay(byDay, mm, e);
        }
        continue;
      }
      for (const civil of civilMmddsForLiturgical(e.feestdatum, viewYear, style)) {
        markDay(byDay, civil, e);
      }
    }

    const civilToday = civilTodayMmdd();
    const nowYear = new Date().getFullYear();
    const nowMonth = new Date().getMonth() + 1;
    const dow = ["ma", "di", "wo", "do", "vr", "za", "zo"];
    let html = "";
    for (let month = 1; month <= 12; month++) {
      const isCurrentMonth = viewYear === nowYear && month === nowMonth;
      html +=
        `<section class="month-card${isCurrentMonth ? " is-current-month" : ""}" ` +
        `id="month-${String(month).padStart(2, "0")}">` +
        `<h2>${MONTHS[month]} ${viewYear}` +
        (isCurrentMonth ? `<span class="month-now-label">deze maand</span>` : "") +
        `</h2><div class="month-days">`;
      for (const d of dow) html += `<div class="dow">${d}</div>`;
      const first = new Date(viewYear, month - 1, 1);
      let start = (first.getDay() + 6) % 7;
      for (let i = 0; i < start; i++) html += `<div></div>`;
      const daysInMonth = new Date(viewYear, month, 0).getDate();
      for (let day = 1; day <= daysInMonth; day++) {
        const mmdd =
          String(month).padStart(2, "0") + "-" + String(day).padStart(2, "0");
        const kinds = byDay.get(mmdd) || new Set();
        const color = dayClass(kinds);
        const has = kinds.size > 0;
        const isToday = viewYear === nowYear && mmdd === civilToday;
        const cls = ["day", has ? "has-entry" : "", color, isToday ? "is-today" : ""]
          .filter(Boolean)
          .join(" ");
        const ariaToday = isToday ? ` aria-label="${day} ${MONTHS[month]}, vandaag"` : "";
        html +=
          `<a class="${cls}" href="${daySurfaceHref(viewYear, mmdd, style)}" ` +
          `data-info-tip="kalender-dag" data-day-mmdd="${mmdd}"${ariaToday}>${day}</a>`;
      }
      html += `</div></section>`;
    }
    root.innerHTML = html;
    wireInfoTips(root);
    scrollKalenderToCurrentMonth();
  }

  /** Op telefoon: start bij de huidige maand als we het lopende jaar tonen. */
  function scrollKalenderToCurrentMonth() {
    if (!document.querySelector("[data-kalender]")) return;
    if (viewYear !== new Date().getFullYear()) return;
    const monthId = `month-${String(new Date().getMonth() + 1).padStart(2, "0")}`;
    const el = document.getElementById(monthId);
    if (!el) return;
    requestAnimationFrame(() => {
      el.scrollIntoView({ block: "start", behavior: "auto" });
    });
  }

  /* ---- Synaxarion ---- */
  let browseMode = "maand";
  let activeLetter = "A";
  let activeMonth = String(new Date().getMonth() + 1).padStart(2, "0");
  let searchQuery = "";

  function isFixedCycleEntry(entry) {
    if (!entry) return false;
    if (entry.cyclus === "paascyclus") return false;
    if (entry.vorm === "weekdagen") return false;
    if (entry.vorm === "weekdag_relatief") return false;
    return true;
  }

  function fixedEntryOnMmdd(entry, mmdd) {
    if (!isFixedCycleEntry(entry)) return false;
    if (entry.van && entry.tot) {
      return mmddInRange(mmdd, entry.van, entry.tot);
    }
    return entry.feestdatum === mmdd;
  }

  function matchesSearch(entry, q) {
    if (!q) return true;
    const hay = [entry.naam, ...(entry.alternatief || [])]
      .join(" ")
      .toLocaleLowerCase("nl");
    return hay.includes(q);
  }

  function checkedShows(name) {
    return Array.from(
      document.querySelectorAll(`input[name="${name}"]:checked`)
    ).map((el) => el.value);
  }

  function filterEntries(entries, shows) {
    return entries.filter((e) => shows.includes(e.soort));
  }

  function entryFixedSortKey(entry) {
    if (entry.van) return entry.van;
    return entry.feestdatum || "99-99";
  }

  function entryTouchesMonthFixed(entry, mm) {
    if (entry.van && entry.tot) {
      for (const part of [entry.van, entry.tot]) {
        if (part.startsWith(mm + "-")) return true;
      }
      if (entry.van <= entry.tot) {
        return entry.van.slice(0, 2) <= mm && entry.tot.slice(0, 2) >= mm;
      }
      return entry.van.slice(0, 2) <= mm || entry.tot.slice(0, 2) >= mm;
    }
    return Boolean(entry.feestdatum && entry.feestdatum.startsWith(mm + "-"));
  }

  function getSynaxarionDag() {
    return parseDagParam(new URLSearchParams(window.location.search).get("dag"));
  }

  function setSynaxarionDag(mmdd) {
    const url = new URL(window.location.href);
    if (mmdd) url.searchParams.set("dag", mmdd);
    else url.searchParams.delete("dag");
    window.history.pushState({}, "", url);
    refresh();
  }

  function entryWhenLabel(e) {
    if (e.van && e.tot) return `${label(e.van)} – ${label(e.tot)}`;
    if (e.feestdatum) return label(e.feestdatum);
    return "—";
  }

  function entryThumbHtml(e) {
    if (!e.icoon) return "";
    return (
      `<img class="list-icoon" src="${assetUrl(String(e.icoon).replace(/^\//, ""))}" ` +
      `alt="" width="28" height="28">`
    );
  }

  function synaxarionTableHtml(rows) {
    if (!rows.length) {
      return "<p>Geen vaste feesten, heiligen of vasten voor deze selectie.</p>";
    }
    // Groepeer opeenvolgende rijen met dezelfde datumlabel → één cel met rowspan.
    const groups = [];
    for (const row of rows) {
      const key = row.whenKey != null ? row.whenKey : row.whenHtml;
      const last = groups[groups.length - 1];
      if (last && last.key === key) {
        last.entries.push(row.entry);
      } else {
        groups.push({
          key,
          whenHtml: row.whenHtml,
          entries: [row.entry],
        });
      }
    }
    const body = groups
      .map((group) => {
        const span = group.entries.length;
        return group.entries
          .map((entry, i) => {
            const thumb = entryThumbHtml(entry);
            const href = assetUrl(String(entry.url || "").replace(/^\//, ""));
            const dateCell =
              i === 0
                ? `<td${span > 1 ? ` rowspan="${span}"` : ""} class="synaxarion-date-cell">${group.whenHtml}</td>`
                : "";
            return (
              `<tr>` +
              dateCell +
              `<td>${thumb}<a href="${href}">${escapeHtml(entry.naam)}</a></td>` +
              `<td>${escapeHtml(kindLabel(entry))}</td>` +
              `</tr>`
            );
          })
          .join("");
      })
      .join("");
    return (
      `<table class="synaxarion-table">` +
      `<thead><tr>` +
      `<th scope="col">Datum</th>` +
      `<th scope="col">Naam</th>` +
      `<th scope="col">Soort</th>` +
      `</tr></thead><tbody>${body}</tbody></table>`
    );
  }

  function synaxarionWeergaveSummary() {
    const shows = checkedShows("show");
    const parts = [];
    if (shows.includes("heilige")) parts.push("heiligen");
    if (shows.includes("feest")) parts.push("feesten");
    if (shows.includes("vasten")) parts.push("vasten");
    let text = parts.length ? parts.join("+") : "niets";
    if (searchQuery) text += " · zoek";
    else text += browseMode === "letter" ? " · alfabet" : " · maanden";
    return text;
  }

  function updateSynaxarionWeergaveSummary() {
    const summary = document.getElementById("synaxarion-weergave-summary");
    if (summary) summary.textContent = synaxarionWeergaveSummary();
  }

  function renderSynaxarionDay(entries, mmdd) {
    const dayRoot = document.getElementById("synaxarion-day");
    const browse = document.getElementById("synaxarion-browse");
    const heading = document.getElementById("synaxarion-heading");
    const nav = document.getElementById("synaxarion-day-nav");
    const list = document.getElementById("synaxarion-day-entries");
    if (!dayRoot || !list) return;
    if (browse) browse.hidden = true;
    dayRoot.hidden = false;
    if (heading) heading.textContent = label(mmdd);
    closeWeergavePanel("synaxarion");
    const prev = shiftMmdd(mmdd, -1);
    const next = shiftMmdd(mmdd, 1);
    const thisYear = clampYear(new Date().getFullYear());
    const datumHref = daySurfaceHref(thisYear, mmdd, getStyle());
    if (nav) {
      nav.innerHTML =
        `<a href="${pageUrl("synaxarion/", {})}">← Synaxarion</a> · ` +
        `<button type="button" class="text-link" data-synaxarion-delta="-1">vorige dag</button> · ` +
        `<button type="button" class="text-link" data-synaxarion-delta="1">volgende dag</button> · ` +
        `<a href="${datumHref}">Deze dag in ${thisYear}</a>`;
      nav.querySelectorAll("[data-synaxarion-delta]").forEach((btn) => {
        btn.addEventListener("click", (ev) => {
          ev.preventDefault();
          const delta = Number(btn.dataset.synaxarionDelta);
          setSynaxarionDag(delta < 0 ? prev : next);
        });
      });
    }
    const shows = checkedShows("show");
    const matched = filterEntries(entries, shows)
      .filter((e) => isFixedCycleEntry(e) && fixedEntryOnMmdd(e, mmdd))
      .sort(
        (a, b) =>
          entryFixedSortKey(a).localeCompare(entryFixedSortKey(b)) ||
          a.naam.localeCompare(b.naam, "nl")
      );
    if (!matched.length) {
      list.innerHTML =
        `<p class="muted today-geen-heilige">` +
        achtergrondLink(
          "heiligen",
          "(Geen feest/gedachtenis van een Heilige van de Lage Landen)"
        ) +
        "</p>";
      } else {
      const whenHtml = escapeHtml(label(mmdd));
      list.innerHTML = synaxarionTableHtml(
        matched.map((entry) => ({ whenHtml, whenKey: mmdd, entry }))
      );
    }
    const site = document.title.includes(" · ")
      ? document.title.slice(document.title.lastIndexOf(" · ") + 3)
      : document.title;
    document.title = `${label(mmdd)} · ${site}`;
  }

  function renderSynaxarionBrowse(entries) {
    const dayRoot = document.getElementById("synaxarion-day");
    const browse = document.getElementById("synaxarion-browse");
    const heading = document.getElementById("synaxarion-heading");
    const list = document.getElementById("synaxarion-list");
    const hint = document.getElementById("synaxarion-hint");
    const letterNav = document.getElementById("letter-nav");
    const monthNav = document.getElementById("month-nav");
    if (!list) return;
    if (dayRoot) dayRoot.hidden = true;
    if (browse) browse.hidden = false;
    if (heading) heading.textContent = "Synaxarion";
    wireWeergavePanel("synaxarion");
    updateSynaxarionWeergaveSummary();

    const shows = checkedShows("show");
    const filtered = filterEntries(entries, shows)
      .filter(isFixedCycleEntry)
      .filter((e) => matchesSearch(e, searchQuery));

    if (letterNav) {
      letterNav.hidden = browseMode !== "letter" || Boolean(searchQuery);
      letterNav.innerHTML = LETTERS.map((L) => {
        const count = filtered.filter((e) => firstLetter(e.naam) === L).length;
        const pressed = L === activeLetter ? "true" : "false";
        return `<button type="button" class="letter-btn" data-letter="${L}" aria-pressed="${pressed}" ${count ? "" : "disabled"}>${L}</button>`;
      }).join("");
      letterNav.querySelectorAll(".letter-btn").forEach((btn) => {
        btn.onclick = () => {
          activeLetter = btn.dataset.letter;
          renderSynaxarionBrowse(entries);
        };
      });
    }

    if (monthNav) {
      monthNav.hidden = browseMode !== "maand" || Boolean(searchQuery);
      monthNav.innerHTML = MONTHS.slice(1)
        .map((name, i) => {
          const mm = String(i + 1).padStart(2, "0");
          const count = filtered.filter((e) => entryTouchesMonthFixed(e, mm))
            .length;
          const pressed = mm === activeMonth ? "true" : "false";
          return `<button type="button" class="letter-btn" data-month="${mm}" aria-pressed="${pressed}" ${count ? "" : "disabled"}>${name.slice(0, 3)}</button>`;
        })
        .join("");
      monthNav.querySelectorAll(".letter-btn").forEach((btn) => {
        btn.onclick = () => {
          activeMonth = btn.dataset.month;
          renderSynaxarionBrowse(entries);
        };
      });
      const pressed = monthNav.querySelector('[aria-pressed="true"]');
      if (pressed && typeof pressed.scrollIntoView === "function") {
        pressed.scrollIntoView({ inline: "center", block: "nearest" });
      }
    }

    if (searchQuery) {
      const subset = filtered
        .slice()
        .sort(
          (a, b) =>
            entryFixedSortKey(a).localeCompare(entryFixedSortKey(b)) ||
            a.naam.localeCompare(b.naam, "nl")
        );
      if (hint) {
        hint.hidden = false;
        hint.textContent = `Zoekresultaten: ${subset.length} item(s).`;
      }
      list.innerHTML = synaxarionTableHtml(
        subset.map((entry) => ({
          whenHtml: escapeHtml(entryWhenLabel(entry)),
          whenKey: entryFixedSortKey(entry) + "\0" + entryWhenLabel(entry),
          entry,
        }))
      );
      return;
    }

    if (browseMode === "letter") {
      const subset = filtered
        .filter((e) => firstLetter(e.naam) === activeLetter)
        .sort(
          (a, b) =>
            entryFixedSortKey(a).localeCompare(entryFixedSortKey(b)) ||
            a.naam.localeCompare(b.naam, "nl")
        );
      if (hint) {
        hint.hidden = false;
        hint.textContent = `Letter ${activeLetter}: ${subset.length} item(s).`;
      }
      list.innerHTML = synaxarionTableHtml(
        subset.map((entry) => ({
          whenHtml: escapeHtml(entryWhenLabel(entry)),
          whenKey: entryFixedSortKey(entry) + "\0" + entryWhenLabel(entry),
          entry,
        }))
      );
      return;
    }

    const daysInMonth = new Date(2024, parseInt(activeMonth, 10), 0).getDate();
    const rows = [];
    for (let day = 1; day <= daysInMonth; day++) {
      const mmdd = activeMonth + "-" + String(day).padStart(2, "0");
      const dayEntries = filtered
        .filter((e) => fixedEntryOnMmdd(e, mmdd))
        .sort((a, b) => a.naam.localeCompare(b.naam, "nl"));
      if (!dayEntries.length) continue;
      const whenHtml =
        `<a href="${pageUrl("synaxarion/", { dag: mmdd })}">${label(mmdd)}</a>`;
      dayEntries.forEach((entry) => {
        rows.push({ whenHtml, whenKey: mmdd, entry });
      });
    }
    if (hint) {
      hint.textContent = "";
      hint.hidden = true;
    }
    list.innerHTML = rows.length
      ? synaxarionTableHtml(rows)
      : "<p>Geen vaste dagen in deze maand.</p>";
  }

  function renderSynaxarion(entries) {
    if (!document.querySelector("[data-synaxarion]")) return;
    const dag = getSynaxarionDag();
    if (dag) renderSynaxarionDay(entries, dag);
    else renderSynaxarionBrowse(entries);
  }

  function initSynaxarion(entries) {
    const root = document.querySelector("[data-synaxarion]");
    if (!root) return;
    if (root.dataset.boundSynaxarion !== "1") {
      root.dataset.boundSynaxarion = "1";
      document.querySelectorAll(".browse-mode .style-btn").forEach((btn) => {
        btn.onclick = () => {
          browseMode = btn.dataset.browse;
          document.querySelectorAll(".browse-mode .style-btn").forEach((b) => {
            b.setAttribute("aria-pressed", b === btn ? "true" : "false");
          });
          renderSynaxarionBrowse(entries);
        };
      });
      document.querySelectorAll('input[name="show"]').forEach((el) => {
        el.addEventListener("change", () => {
          updateSynaxarionWeergaveSummary();
          renderSynaxarion(entries);
        });
      });
      const search = document.getElementById("synaxarion-search");
      if (search) {
        search.addEventListener("input", () => {
          searchQuery = (search.value || "").trim().toLocaleLowerCase("nl");
          updateSynaxarionWeergaveSummary();
          renderSynaxarionBrowse(entries);
        });
      }
    }
    renderSynaxarion(entries);
  }

  /* ---- Agenda ICS ---- */
  function icsStyleToJs(stijl) {
    return stijl === "oud" ? "juliaans" : "gregoriaans";
  }

  function isRandFeest(entry) {
    const id = (entry && entry.id) || "";
    return (
      id.startsWith("voorfeest-") ||
      id.startsWith("nafeest-") ||
      id.startsWith("synaxis-") ||
      id.startsWith("teruggave-")
    );
  }

  function feastWeight(entry) {
    const id = (entry && entry.id) || "";
    const naam = entryNaam(entry);
    if (id === "pascha") return [0, naam];
    if (
      id.startsWith("grote-") ||
      id === "palmzondag" ||
      id === "theofanie" ||
      id === "kerst"
    ) {
      return [1, naam];
    }
    return [2, naam];
  }

  function pickOneFeast(list) {
    return list.slice().sort((a, b) => {
      const [wa, na] = feastWeight(a);
      const [wb, nb] = feastWeight(b);
      if (wa !== wb) return wa - wb;
      return na.localeCompare(nb, "nl");
    })[0];
  }

  function icsKopFeesten(dayEntries) {
    const feesten = (dayEntries || []).filter(isDayTypeFeast);
    const named = feesten.filter((e) => !isRandFeest(e));
    const rand = feesten.filter(isRandFeest);
    if (named.length) return [pickOneFeast(named)];
    if (rand.length) {
      const synaxis = rand.filter((e) => (e.id || "").startsWith("synaxis-"));
      const pool = synaxis.length ? synaxis : rand;
      return [pickOneFeast(pool)];
    }
    return [];
  }

  function icsKopHeiligen(dayEntries) {
    return (dayEntries || [])
      .filter((e) => e.soort === "heilige")
      .slice()
      .sort((a, b) => entryNaam(a).localeCompare(entryNaam(b), "nl"));
  }

  function vastenBronNaam(vasten, matched) {
    if (vasten && vasten.periode) return entryNaam(vasten.periode);
    const weekly = (matched || []).filter(isWeeklyEntry);
    if (weekly.length) return entryNaam(weekly[0]);
    const t = (vasten && vasten.tekst) || "";
    const i = t.indexOf(" — ");
    if (i >= 0) return t.slice(i + 3).split(",")[0].trim();
    return "";
  }

  /** Spiegel van scripts/ics.py day_title (Python is normatief). */
  function icsDayTitle(dayEntries, shows, weekday, mmdd, year, style) {
    const kinds = new Set(shows || []);
    const visible = (dayEntries || []).filter(
      (e) => kinds.has(e.soort) && (e.soort === "heilige" || e.soort === "feest")
    );
    const vasten = mixVastenniveau(dayEntries, weekday, mmdd);
    const showVasten = kinds.has("vasten") && vasten;
    let kop = icsKopFeesten(visible);
    let headline = kop.map(entryNaam).join(", ");
    if (!headline && kinds.has("feest") && year && style && mmdd) {
      const lez = lezingenForDay(year, mmdd, style);
      if (lez && lez.daglabel) headline = lez.daglabel;
    }
    if (!headline) {
      kop = icsKopHeiligen(visible);
      headline = kop.map(entryNaam).join(", ");
    }
    if (!headline && !showVasten) return null;
    if (!showVasten) return headline || null;
    const label = VASTEN_LABELS[vasten.niveau] || vasten.niveau;
    if (headline) return `${headline} · ${label}`;
    const bron = vastenBronNaam(vasten, dayEntries);
    return bron ? `${label} · ${bron}` : label;
  }

  function startOfIsoWeek(d) {
    const x = new Date(d.getFullYear(), d.getMonth(), d.getDate());
    const wd = x.getDay() || 7;
    x.setDate(x.getDate() - (wd - 1));
    return x;
  }

  function renderAgendaVoorbeeld(shows, stijl) {
    const list = document.getElementById("ics-voorbeeld-week");
    if (!list) return;
    if (!shows.length) {
      list.innerHTML =
        "<li class=\"muted\">Kies minstens één soort dag.</li>";
      return;
    }
    const style = icsStyleToJs(stijl);
    const start = startOfIsoWeek(new Date());
    const days = ["ma", "di", "wo", "do", "vr", "za", "zo"];
    const items = [];
    for (let i = 0; i < 7; i++) {
      const d = addDays(start, i);
      const year = d.getFullYear();
      const mmdd = mmddFromDate(d);
      const matched = entriesOnMmdd(calendarEntries, mmdd, style, year);
      const weekday = isoWeekdayFromMmdd(mmdd, year);
      const title = icsDayTitle(matched, shows, weekday, mmdd, year, style);
      const dag = `${days[i]} ${d.getDate()} ${MONTHS[d.getMonth() + 1]}`;
      const tekst = title
        ? escapeHtml(title)
        : "<span class=\"muted\">niets op deze dag</span>";
      items.push(
        `<li><span class="agenda-voorbeeld-dag">${escapeHtml(dag)}</span>` +
          `<span class="agenda-voorbeeld-titel">${tekst}</span></li>`
      );
    }
    list.innerHTML = items.join("");
  }

  function webcalUrl(httpsUrl) {
    return httpsUrl.replace(/^https:/i, "webcal:");
  }

  function icsFilename() {
    const shows = checkedShows("ics-show");
    const stijl =
      (document.querySelector('input[name="ics-stijl"]:checked') || {}).value ||
      "nieuw";
    if (!shows.length) return null;
    const set = new Set(shows);
    const mapping = [
      [["heilige", "feest", "vasten"], "alles"],
      [["heilige"], "heiligen"],
      [["feest"], "feesten"],
      [["vasten"], "vasten"],
      [["heilige", "feest"], "heiligen-feesten"],
      [["heilige", "vasten"], "heiligen-vasten"],
      [["feest", "vasten"], "feesten-vasten"],
    ];
    let key = null;
    for (const [need, name] of mapping) {
      if (need.length === set.size && need.every((k) => set.has(k))) {
        key = name;
        break;
      }
    }
    return key ? `${key}-${stijl}.ics` : null;
  }

  function icsModus() {
    return (
      (document.querySelector('input[name="ics-modus"]:checked') || {}).value ||
      "abonneren"
    );
  }

  function nlOpsomming(items) {
    if (!items.length) return "";
    if (items.length === 1) return items[0];
    if (items.length === 2) return `${items[0]} en ${items[1]}`;
    return `${items.slice(0, -1).join(", ")} en ${items[items.length - 1]}`;
  }

  function agendaSamenvatting(shows, stijl, modus, heeftBestand) {
    if (!shows.length || !heeftBestand) {
      return "Kies minstens één soort dag. Daarna krijgt de knop hieronder een betekenis.";
    }
    const labels = { heilige: "heiligen", feest: "feesten", vasten: "vasten" };
    const wat = nlOpsomming(shows.map((s) => labels[s] || s));
    const kal =
      stijl === "oud" ? "de oude kalender" : "de nieuwe kalender";
    if (modus === "downloaden") {
      return `De knop downloadt ${wat} volgens ${kal} als bestand.`;
    }
    return `De knop kopieert de link voor ${wat} volgens ${kal}. Plak die in uw agenda-app; de stappen staan hieronder.`;
  }

  function setHidden(el, hidden) {
    if (!el) return;
    el.hidden = hidden;
  }

  async function copyAgendaUrl(url) {
    const input = document.getElementById("ics-url");
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(url);
        return true;
      } catch {
        /* val terug op het zichtbare veld */
      }
    }
    if (!input) return false;
    input.focus();
    input.select();
    try {
      return document.execCommand("copy");
    } catch {
      return false;
    }
  }

  function updateAgendaUi() {
    if (!document.querySelector("[data-agenda]")) return;
    const file = icsFilename();
    const shows = checkedShows("ics-show");
    const stijl =
      (document.querySelector('input[name="ics-stijl"]:checked') || {}).value ||
      "nieuw";
    const modus = icsModus();
    const url = file ? assetUrl("ics/" + file) : "";
    const download = document.getElementById("ics-download");
    const copyBtn = document.getElementById("ics-copy");
    const samenvatting = document.getElementById("ics-samenvatting");
    const status = document.getElementById("ics-status");
    const urlRow = document.getElementById("ics-url-row");
    const urlInput = document.getElementById("ics-url");
    const howtoAbo = document.getElementById("ics-howto-abonneren");
    const howtoDl = document.getElementById("ics-howto-downloaden");
    const webcal = document.getElementById("ics-webcal");
    const klaar = Boolean(file);

    renderAgendaVoorbeeld(shows, stijl);

    if (samenvatting) {
      samenvatting.textContent = agendaSamenvatting(
        shows,
        stijl,
        modus,
        klaar
      );
    }
    if (status && status.dataset.sticky !== "1") {
      status.textContent = "";
    }

    if (urlInput) urlInput.value = url;
    setHidden(urlRow, !(klaar && modus === "abonneren"));
    setHidden(howtoAbo, modus !== "abonneren");
    setHidden(howtoDl, modus !== "downloaden");

    if (download) {
      const toonDownload = klaar && modus === "downloaden";
      setHidden(download, !toonDownload);
      if (toonDownload) {
        download.href = url;
        download.setAttribute("download", file);
        download.classList.remove("is-disabled");
        download.textContent = "Download de kalender";
      } else {
        download.removeAttribute("href");
        download.removeAttribute("download");
      }
    }
    if (copyBtn) {
      const toonCopy = klaar && modus === "abonneren";
      setHidden(copyBtn, !toonCopy);
      copyBtn.disabled = !toonCopy;
      copyBtn.classList.toggle("is-disabled", !toonCopy);
      if (toonCopy && copyBtn.dataset.copied !== "1") {
        copyBtn.textContent = "Kopieer de agenda-link";
      }
    }
    if (webcal) {
      const toonWebcal = klaar && modus === "abonneren";
      setHidden(webcal, !toonWebcal);
      if (toonWebcal) {
        webcal.href = webcalUrl(url);
        webcal.classList.remove("is-disabled");
      } else {
        webcal.removeAttribute("href");
      }
    }
    if (!klaar) {
      if (download) {
        setHidden(download, true);
      }
      if (copyBtn) {
        setHidden(copyBtn, true);
      }
      if (webcal) {
        setHidden(webcal, true);
      }
    }
  }

  function initAgenda() {
    const root = document.querySelector("[data-agenda]");
    if (!root) return;
    if (root.dataset.boundAgenda !== "1") {
      root.dataset.boundAgenda = "1";
      root
        .querySelectorAll(
          'input[name="ics-show"], input[name="ics-stijl"], input[name="ics-modus"]'
        )
        .forEach((el) => el.addEventListener("change", updateAgendaUi));
      const copyBtn = document.getElementById("ics-copy");
      if (copyBtn) {
        copyBtn.addEventListener("click", async () => {
          const file = icsFilename();
          if (!file) return;
          const url = assetUrl("ics/" + file);
          const ok = await copyAgendaUrl(url);
          const status = document.getElementById("ics-status");
          copyBtn.dataset.copied = "1";
          copyBtn.textContent = ok
            ? "Link gekopieerd"
            : "Kopieer de link hieronder";
          if (status) {
            status.dataset.sticky = "1";
            status.textContent = ok
              ? "De agenda-link staat op het klembord. Plak die in de stappen hieronder."
              : "Selecteer de agenda-link hieronder en kopieer die zelf (Ctrl+C of Cmd+C).";
          }
          window.setTimeout(() => {
            copyBtn.dataset.copied = "0";
            copyBtn.textContent = "Kopieer de agenda-link";
            if (status) {
              status.dataset.sticky = "0";
              status.textContent = "";
            }
          }, 4000);
        });
      }
    }
    updateAgendaUi();
  }

  async function refresh() {
    const style = getStyle();
    setStyle(style);
    if (redirectDaySurfaceIfNeeded(style)) return;
    ensureCanonicalDatumUrl(style);
    updateHeading(style);
    try {
      const entries = await loadEntries();
      calendarEntries = entries;
      yearBounds = yearBoundsFromEntries(entries);
      viewYear = clampYear(viewYear);
      renderToday(entries, style);
      renderYearGrid(entries, style);
      initSynaxarion(entries);
      initAgenda();
      try {
        await loadLezingenIndex();
        initRooster(style);
        // Herteken vandaag/datum en agendavoorbeeld als lezingen nu beschikbaar zijn.
        if (document.getElementById("today-entries")) {
          renderToday(entries, style);
        }
        initAgenda();
      } catch (lezErr) {
        console.error(lezErr);
        const roost = document.getElementById("rooster-tables");
        if (roost) {
          roost.innerHTML =
            "<p class=\"muted\">Lezingengegevens konden niet worden geladen.</p>";
        }
      }
    } catch (err) {
      const cardEntries = document.getElementById("today-entries");
      if (cardEntries) {
        cardEntries.innerHTML =
          "<p>Kon kalenderdata niet laden. Vernieuw de pagina of probeer later opnieuw.</p>";
      }
      console.error(err);
    }
  }

  document.addEventListener("click", (e) => {
    const dlg = document.getElementById("info-popover");
    if (dlg && !dlg.hidden) {
      const t = e.target;
      if (
        !dlg.contains(t) &&
        !(t.closest && t.closest("[data-info-tip]"))
      ) {
        closeInfoPopover();
      }
    }
    const btn = e.target.closest && e.target.closest(".style-btn[data-style]");
    if (!btn) return;
    e.preventDefault();
    applyStyle(btn.dataset.style);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeInfoPopover();
      closeAllWeergavePanels();
    }
  });

  window.addEventListener("popstate", () => {
    refresh();
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      wireInfoTips(document);
      maybeShowSiteIntro();
      refresh();
    });
  } else {
    wireInfoTips(document);
    maybeShowSiteIntro();
    refresh();
  }
})();
