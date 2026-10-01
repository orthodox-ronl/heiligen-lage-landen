(function () {
  const STORAGE_KEY = "site-theme";

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    document.querySelectorAll("[data-theme-set]").forEach((btn) => {
      btn.setAttribute(
        "aria-pressed",
        btn.dataset.themeSet === theme ? "true" : "false",
      );
    });
  }

  function markExternalLinks() {
    document.querySelectorAll("a[href]").forEach((a) => {
      const href = a.getAttribute("href");
      if (!href || href.startsWith("#") || href.startsWith("mailto:")) {
        return;
      }
      let absolute;
      try {
        absolute = new URL(href, window.location.href);
      } catch (_) {
        return;
      }
      if (absolute.protocol !== "http:" && absolute.protocol !== "https:") {
        return;
      }
      if (absolute.origin === window.location.origin) {
        return;
      }
      a.target = "_blank";
      const rel = new Set((a.getAttribute("rel") || "").split(/\s+/).filter(Boolean));
      rel.add("noopener");
      rel.add("noreferrer");
      a.setAttribute("rel", [...rel].join(" "));
    });
  }

  function init() {
    let theme = "dark";
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === "light" || stored === "dark") {
        theme = stored;
      }
    } catch (_) {
      /* localStorage unavailable */
    }
    applyTheme(theme);

    document.querySelectorAll("[data-theme-set]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const next = btn.dataset.themeSet;
        applyTheme(next);
        try {
          localStorage.setItem(STORAGE_KEY, next);
        } catch (_) {
          /* localStorage unavailable */
        }
      });
    });

    markExternalLinks();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
