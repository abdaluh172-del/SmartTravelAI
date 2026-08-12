// سلوكيات مشتركة بين جميع الصفحات
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("navToggle");
  const nav = document.getElementById("mainNav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => nav.classList.toggle("open"));
  }

  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      try { await Api.logout(); } catch (err) { /* ignore */ }
      window.location.href = "/";
    });
  }
});

// أدوات مساعدة عامة
function fmtPrice(price, currency = "SAR") {
  const curLabel = currency === "SAR" ? "ريال" : currency;
  return `${Number(price).toLocaleString("ar-SA")} ${curLabel}`;
}

function fmtTime(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString("ar-SA", { hour: "2-digit", minute: "2-digit" });
  } catch (e) { return ""; }
}

function fmtDuration(minutes) {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${h} س ${m ? m + " د" : ""}`.trim();
}

function qs(params) {
  return Object.entries(params)
    .filter(([, v]) => v !== undefined && v !== null && v !== "")
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join("&");
}

function getSearchState() {
  try {
    return JSON.parse(sessionStorage.getItem("lastSearch") || "null");
  } catch (e) { return null; }
}

function setSearchState(state) {
  sessionStorage.setItem("lastSearch", JSON.stringify(state));
}
