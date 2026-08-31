(function () {
  const root = document.getElementById("heiligen-kaart");
  const wrap = document.getElementById("heiligen-kaart-wrap");
  const dataEl = document.getElementById("heiligen-data");
  if (!root || typeof L === "undefined") return;

  const base =
    (document.body && document.body.getAttribute("data-base")) ||
    document.baseURI ||
    "/";

  function dataUrl(name) {
    return new URL("data/" + name, base).href;
  }

  function siteUrl(path) {
    const rel = String(path || "").replace(/^\//, "");
    return new URL(rel, base).href;
  }

  const imagePath = new URL("vendor/leaflet/images/", base).href;
  L.Icon.Default.imagePath = imagePath;

  const STREEK_KLEUR = "#c9a227";
  const STREEK_RAND = "#5c4810";

  const NL_BE = L.latLngBounds([49.45, 2.4], [53.7, 7.25]);

  const map = L.map(root, { scrollWheelZoom: false });
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 18,
  }).addTo(map);
  map.fitBounds(NL_BE);

  map.getContainer().addEventListener(
    "wheel",
    (ev) => {
      if (!ev.ctrlKey) return;
      ev.preventDefault();
      const delta = ev.deltaY > 0 ? -1 : 1;
      map.setZoom(map.getZoom() + delta, { animate: false });
    },
    { passive: false }
  );

  const markers = [];
  let streekVlak = null;
  let lastFilter = { query: "", plaatsIds: null, saintUrls: null };
  let saintsByPlaats = {};
  let streekRecords = [];
  let kinderenByStreek = {};

  function saintVisible(h) {
    const urls = lastFilter.saintUrls;
    if (!urls || !urls.length) return true;
    return urls.indexOf(h.url) !== -1;
  }

  function norm(value) {
    return String(value || "")
      .trim()
      .toLocaleLowerCase("nl");
  }

  function matchesStreekQuery(streek, query) {
    const q = norm(query);
    if (!q) return false;
    if (norm(streek.naam) === q || norm(streek.id) === q) return true;
    return (streek.alternatief || []).some((a) => norm(a) === q);
  }

  function popupHtml(p, saints) {
    const visible = saints.filter(saintVisible);
    const items = visible
      .sort((a, b) => a.naam.localeCompare(b.naam, "nl"))
      .map(
        (h) =>
          `<li><a href="${siteUrl(h.url)}">${escapeHtml(h.naam)}</a></li>`
      )
      .join("");
    const heading = p.soort === "streek" ? "Streek" : "Plaats";
    return (
      `<p class="kaart-popup-titel">${heading}: ${escapeHtml(p.naam)}</p>` +
      `<ul class="kaart-popup-lijst">${items}</ul>`
    );
  }

  function zoekPlaats(p) {
    document.dispatchEvent(
      new CustomEvent("heiligen-plaats-zoek", {
        detail: { naam: p.naam, id: p.id },
      })
    );
  }

  function uniqueLatLngs(latlngs) {
    const seen = new Set();
    const out = [];
    latlngs.forEach((raw) => {
      const p = L.latLng(raw);
      const key = p.lat.toFixed(5) + "," + p.lng.toFixed(5);
      if (seen.has(key)) return;
      seen.add(key);
      out.push(p);
    });
    return out;
  }

  function cross(o, a, b) {
    return (a.lng - o.lng) * (b.lat - o.lat) - (a.lat - o.lat) * (b.lng - o.lng);
  }

  function convexHull(latlngs) {
    const pts = uniqueLatLngs(latlngs)
      .slice()
      .sort((a, b) => {
        if (a.lng === b.lng) return a.lat - b.lat;
        return a.lng - b.lng;
      });
    if (pts.length <= 2) return pts;
    const lower = [];
    pts.forEach((p) => {
      while (
        lower.length >= 2 &&
        cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0
      ) {
        lower.pop();
      }
      lower.push(p);
    });
    const upper = [];
    for (let i = pts.length - 1; i >= 0; i -= 1) {
      const p = pts[i];
      while (
        upper.length >= 2 &&
        cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0
      ) {
        upper.pop();
      }
      upper.push(p);
    }
    lower.pop();
    upper.pop();
    return lower.concat(upper);
  }

  function padLatLngs(latlngs, factor) {
    const bounds = L.latLngBounds(latlngs);
    const c = bounds.getCenter();
    return latlngs.map((p) =>
      L.latLng(
        c.lat + (p.lat - c.lat) * factor,
        c.lng + (p.lng - c.lng) * factor
      )
    );
  }

  function streekKinderen(streekId) {
    return (kinderenByStreek[streekId] || []).filter(
      (p) => (saintsByPlaats[p.id] || []).length
    );
  }

  function streekLatLng(streek) {
    const kids = streekKinderen(streek.id);
    if (!kids.length) return L.latLng(streek.lat, streek.lon);
    const lat = kids.reduce((sum, p) => sum + p.lat, 0) / kids.length;
    const lon = kids.reduce((sum, p) => sum + p.lon, 0) / kids.length;
    return L.latLng(lat, lon);
  }

  function streekStyle(selected) {
    return {
      radius: selected ? 14 : 12,
      color: STREEK_RAND,
      weight: selected ? 3 : 2,
      fillColor: STREEK_KLEUR,
      fillOpacity: selected ? 1 : 0.95,
      className: "kaart-streek-punt",
    };
  }

  function vlakStyle() {
    return {
      color: STREEK_RAND,
      weight: 2,
      dashArray: "7 5",
      fillColor: STREEK_KLEUR,
      fillOpacity: 0.4,
      className: "kaart-streek-vlak",
      interactive: true,
    };
  }

  function makeStreekVlak(streek) {
    const kids = streekKinderen(streek.id);
    const pts = uniqueLatLngs(
      kids.map((p) => [p.lat, p.lon]).concat([[streek.lat, streek.lon]])
    );
    const hull = convexHull(pts);
    let layer;
    if (hull.length >= 3) {
      layer = L.polygon(padLatLngs(hull, 1.28), vlakStyle());
    } else {
      const center = pts.length
        ? L.latLngBounds(pts).getCenter()
        : streekLatLng(streek);
      let radius = 28000;
      pts.forEach((p) => {
        radius = Math.max(radius, center.distanceTo(p) * 1.35);
      });
      layer = L.circle(center, Object.assign({ radius: radius }, vlakStyle()));
    }
    return layer;
  }

  function selectedStreekRecord() {
    const q = lastFilter.query || "";
    return streekRecords.find((s) => matchesStreekQuery(s, q)) || null;
  }

  function clearStreekVlak() {
    if (!streekVlak) return;
    map.removeLayer(streekVlak);
    streekVlak = null;
  }

  function applyFilter() {
    const q = lastFilter.query || "";
    const ids = new Set(lastFilter.plaatsIds || []);
    const gekozen = selectedStreekRecord();
    const kindIds = new Set(
      gekozen ? streekKinderen(gekozen.id).map((p) => p.id) : []
    );
    const visible = [];
    markers.forEach((item) => {
      const saints = (saintsByPlaats[item.id] || []).filter(saintVisible);
      const show = saints.length > 0 && (!q || ids.has(item.id));
      if (show) {
        item.marker.setPopupContent(popupHtml(item.plaats, saints));
        if (item.streek && item.marker.setStyle) {
          item.marker.setStyle(streekStyle(gekozen && gekozen.id === item.id));
        }
        if (!map.hasLayer(item.marker)) item.marker.addTo(map);
        const icon = item.marker._icon;
        if (icon) {
          icon.classList.toggle("is-streek-kind", kindIds.has(item.id));
        }
        visible.push(item.marker);
      } else if (map.hasLayer(item.marker)) {
        map.removeLayer(item.marker);
      }
    });

    clearStreekVlak();
    if (gekozen) {
      const saints = (saintsByPlaats[gekozen.id] || []).filter(saintVisible);
      streekVlak = makeStreekVlak(gekozen);
      streekVlak.bindPopup(popupHtml(gekozen, saints));
      streekVlak.on("click", () => zoekPlaats(gekozen));
      streekVlak.addTo(map);
      streekVlak.bringToBack();
    }

    if (gekozen && streekVlak) {
      const groep = visible.filter((m) => {
        const item = markers.find((it) => it.marker === m);
        return (
          item && (item.id === gekozen.id || item.plaats.streek === gekozen.id)
        );
      });
      const layers = groep.concat([streekVlak]);
      map.fitBounds(L.featureGroup(layers).getBounds().pad(0.22));
    } else if (q && visible.length) {
      map.fitBounds(L.featureGroup(visible).getBounds().pad(0.2));
    } else if (!q) {
      map.fitBounds(NL_BE);
    }
  }

  function invalidateSoon() {
    requestAnimationFrame(() => {
      map.invalidateSize();
      applyFilter();
    });
  }

  let heiligen = [];
  if (dataEl) {
    try {
      let parsed = JSON.parse(dataEl.textContent || "[]");
      if (typeof parsed === "string") parsed = JSON.parse(parsed);
      heiligen = Array.isArray(parsed) ? parsed : [];
    } catch (_) {
      heiligen = [];
    }
  }

  fetch(dataUrl("plaatsen.json"))
    .then((r) => r.json())
    .then((plaatsen) => {
      saintsByPlaats = {};
      heiligen.forEach((h) => {
        (h.plaats_ids || []).forEach((pid) => {
          (saintsByPlaats[pid] || (saintsByPlaats[pid] = [])).push(h);
        });
      });

      streekRecords = [];
      kinderenByStreek = {};
      (plaatsen || []).forEach((p) => {
        if (p.soort === "streek") streekRecords.push(p);
        if (p.streek) {
          (kinderenByStreek[p.streek] || (kinderenByStreek[p.streek] = [])).push(
            p
          );
        }
      });

      (plaatsen || []).forEach((p) => {
        const saints = saintsByPlaats[p.id] || [];
        if (!saints.length) return;
        const isStreek = p.soort === "streek";
        const marker = isStreek
          ? L.circleMarker(streekLatLng(p), streekStyle(false))
          : L.marker([p.lat, p.lon], { title: p.naam });
        if (isStreek) {
          marker.bindTooltip(p.naam, {
            permanent: true,
            direction: "right",
            offset: [10, 0],
            className: "kaart-streek-label",
            opacity: 1,
          });
        }
        marker.bindPopup(popupHtml(p, saints));
        marker.on("click", () => zoekPlaats(p));
        marker.addTo(map);
        markers.push({
          id: p.id,
          marker: marker,
          streek: isStreek,
          plaats: p,
        });
      });

      map.fitBounds(NL_BE);
      applyFilter();
      invalidateSoon();
    })
    .catch(() => {
      map.fitBounds(NL_BE);
    });

  document.addEventListener("heiligen-filter", (ev) => {
    lastFilter = ev.detail || lastFilter;
    applyFilter();
  });

  document.addEventListener("heiligen-kaart-layout", () => {
    if (wrap && wrap.hidden) return;
    invalidateSoon();
  });

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
})();
