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
  let lastFilter = { query: "", plaatsIds: null, saintUrls: null };
  let saintsByPlaats = {};

  function saintVisible(h) {
    const urls = lastFilter.saintUrls;
    if (!urls || !urls.length) return true;
    return urls.indexOf(h.url) !== -1;
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

  function applyFilter() {
    const q = lastFilter.query || "";
    const ids = new Set(lastFilter.plaatsIds || []);
    const visible = [];
    markers.forEach((item) => {
      const saints = (saintsByPlaats[item.id] || []).filter(saintVisible);
      const show = saints.length > 0 && (!q || ids.has(item.id));
      if (show) {
        item.marker.setPopupContent(popupHtml(item.plaats, saints));
        if (!map.hasLayer(item.marker)) item.marker.addTo(map);
        visible.push(item.marker);
      } else if (map.hasLayer(item.marker)) {
        map.removeLayer(item.marker);
      }
    });
    if (q && visible.length) {
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

      (plaatsen || []).forEach((p) => {
        const saints = saintsByPlaats[p.id] || [];
        if (!saints.length) return;
        const isStreek = p.soort === "streek";
        const marker = L.marker([p.lat, p.lon], {
          title: p.naam,
          opacity: isStreek ? 0.85 : 1,
        });
        marker.bindPopup(popupHtml(p, saints));
        marker.on("click", () => {
          document.dispatchEvent(
            new CustomEvent("heiligen-plaats-zoek", {
              detail: { naam: p.naam, id: p.id },
            })
          );
        });
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
