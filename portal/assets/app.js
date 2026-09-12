const i18n = {
  zh: {
    brand_sub: "文档收集库",
    theme_toggle: "切换深浅色主题",
    search_label: "搜索项目",
    search_placeholder: "搜索项目名称或简介…",
    count: (n) => `共 ${n} 个项目`,
    empty: "没有匹配的项目。",
    footer: "API 参考页在收集库模式下可能不完整；完整 API 请查看各项目上游仓库。",
    upstream: "上游仓库",
    open: "打开文档",
  },
  en: {
    brand_sub: "Docs collection",
    theme_toggle: "Toggle light / dark theme",
    search_label: "Search projects",
    search_placeholder: "Search by name or summary…",
    count: (n) => `${n} project${n === 1 ? "" : "s"}`,
    empty: "No matching projects.",
    footer: "API pages may be incomplete in collection mode; see each upstream repo for full API docs.",
    upstream: "Upstream",
    open: "Open docs",
  },
};

const THEME_KEY = "frog-docs-theme";

let projects = [];
let uiLang = "zh";

const grid = document.getElementById("project-grid");
const emptyState = document.getElementById("empty-state");
const countEl = document.getElementById("project-count");
const searchInput = document.getElementById("project-search");
const themeToggle = document.getElementById("theme-toggle");

function applyChrome() {
  const t = i18n[uiLang];
  document.documentElement.lang = uiLang === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (typeof t[key] === "string") el.textContent = t[key];
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
    const key = el.getAttribute("data-i18n-aria");
    if (typeof t[key] === "string") {
      el.setAttribute("aria-label", t[key]);
      el.setAttribute("title", t[key]);
    }
  });
  searchInput.placeholder = t.search_placeholder;
  emptyState.textContent = t.empty;
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.classList.toggle("is-active", btn.dataset.uiLang === uiLang);
  });
}

function applyTheme(theme, persist) {
  document.documentElement.dataset.theme = theme;
  if (!persist) return;
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch (err) {
    /* storage unavailable — keep the in-memory theme only */
  }
}

function summaryFor(project) {
  if (uiLang === "zh" && project.summary_zh) return project.summary_zh;
  return project.summary || "";
}

function render(filter = "") {
  const q = filter.trim().toLowerCase();
  const t = i18n[uiLang];
  const filtered = projects.filter((p) => {
    if (!q) return true;
    const hay = [p.id, p.title, p.summary, p.summary_zh].filter(Boolean).join(" ").toLowerCase();
    return hay.includes(q);
  });

  countEl.textContent = t.count(filtered.length);
  emptyState.classList.toggle("hidden", filtered.length > 0);
  grid.innerHTML = "";

  for (const project of filtered) {
    const card = document.createElement("article");
    card.className = "card";

    const langs = (project.languages || [])
      .map(
        (lang) =>
          `<a class="btn btn-primary" href="${lang.href}">${lang.label}</a>`
      )
      .join("");

    const upstream = project.upstream
      ? `<a class="btn btn-ghost" href="${project.upstream}" target="_blank" rel="noopener noreferrer">${t.upstream}</a>`
      : "";

    card.innerHTML = `
      <div class="card-head">
        <h2>${escapeHtml(project.title || project.id)}</h2>
        <span class="card-id">${escapeHtml(project.id)}</span>
      </div>
      <p>${escapeHtml(summaryFor(project))}</p>
      <div class="card-actions">
        ${langs}
        ${upstream}
      </div>
    `;
    grid.appendChild(card);
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function boot() {
  applyChrome();
  try {
    const res = await fetch("./projects.json", { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    projects = await res.json();
  } catch (err) {
    projects = [];
    emptyState.textContent =
      uiLang === "zh"
        ? "未能加载 projects.json，请先运行构建脚本。"
        : "Failed to load projects.json. Run the build script first.";
    emptyState.classList.remove("hidden");
    console.error(err);
  }
  render(searchInput.value);
}

document.querySelectorAll(".lang-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    uiLang = btn.dataset.uiLang;
    applyChrome();
    render(searchInput.value);
  });
});

themeToggle.addEventListener("click", () => {
  const next =
    document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(next, true);
});

/* Follow the OS theme until the visitor picks one explicitly. */
const colorScheme = window.matchMedia("(prefers-color-scheme: dark)");
colorScheme.addEventListener("change", (event) => {
  let saved = null;
  try {
    saved = localStorage.getItem(THEME_KEY);
  } catch (err) {
    saved = null;
  }
  if (saved !== "light" && saved !== "dark") {
    applyTheme(event.matches ? "dark" : "light", false);
  }
});

searchInput.addEventListener("input", () => render(searchInput.value));

boot();
