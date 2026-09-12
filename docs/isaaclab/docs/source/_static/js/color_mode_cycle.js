/**
 * Restore click-to-cycle color mode (light → dark → auto) instead of the
 * pydata-sphinx-theme dropdown selector.
 */
(function () {
  const MODES = ["light", "dark", "auto"];
  const mql = window.matchMedia("(prefers-color-scheme: dark)");

  function resolvedTheme(mode) {
    return mode === "auto" ? (mql.matches ? "dark" : "light") : mode;
  }

  function syncAutoListener(mode) {
    mql.onchange =
      mode === "auto"
        ? function () {
            const theme = resolvedTheme("auto");
            document.documentElement.dataset.theme = theme;
            localStorage.setItem("theme", theme);
            document.querySelectorAll(".dropdown-menu").forEach(function (el) {
              el.classList.toggle("dropdown-menu-dark", theme === "dark");
            });
          }
        : null;
  }

  function applyMode(mode) {
    if (MODES.indexOf(mode) === -1) mode = "auto";
    const theme = resolvedTheme(mode);
    document.documentElement.dataset.mode = mode;
    document.documentElement.dataset.theme = theme;
    document.querySelectorAll(".dropdown-menu").forEach(function (el) {
      el.classList.toggle("dropdown-menu-dark", theme === "dark");
    });
    localStorage.setItem("mode", mode);
    localStorage.setItem("theme", theme);
    document.querySelectorAll(".theme-change-button").forEach(function (btn) {
      btn.classList.toggle("active", btn.dataset.mode === mode);
    });
    syncAutoListener(mode);
  }

  function cycleMode(event) {
    const btn = event.target.closest(".theme-switch-button");
    if (!btn) return;
    event.preventDefault();
    event.stopPropagation();
    if (typeof event.stopImmediatePropagation === "function") {
      event.stopImmediatePropagation();
    }
    const current =
      document.documentElement.dataset.mode ||
      localStorage.getItem("mode") ||
      "auto";
    const idx = MODES.indexOf(current);
    applyMode(MODES[(idx + 1) % MODES.length]);
  }

  function disarmDropdowns() {
    document.querySelectorAll(".theme-switch-button").forEach(function (btn) {
      btn.classList.remove("dropdown-toggle");
      btn.removeAttribute("data-bs-toggle");
      btn.setAttribute("aria-expanded", "false");
      btn.setAttribute("title", "Toggle color mode");
      btn.setAttribute("aria-label", "Toggle color mode");
    });
    document
      .querySelectorAll(".theme-switch-container > .dropdown-menu")
      .forEach(function (menu) {
        menu.hidden = true;
        menu.style.display = "none";
      });
  }

  // Capture phase so Bootstrap dropdown never opens.
  document.addEventListener("click", cycleMode, true);

  function boot() {
    disarmDropdowns();
    const mode =
      document.documentElement.dataset.mode ||
      localStorage.getItem("mode") ||
      "auto";
    if (mode) applyMode(mode);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
  window.addEventListener("load", disarmDropdowns);
})();
