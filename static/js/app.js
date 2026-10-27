/**
 * NutriCare AI — Frontend JavaScript
 * Handles tab switching, form submission, chat Q&A, and result rendering.
 */

// ── Helpers ──────────────────────────────────────────────────────────────────
const $  = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

function show(el)  { if (el) el.style.display = ""; }
function hide(el)  { if (el) el.style.display = "none"; }
function showEl(id) { show(document.getElementById(id)); }
function hideEl(id) { hide(document.getElementById(id)); }

function setHTML(id, html) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = html;
}

function showAlert(id, message, type = "danger") {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.innerHTML = `<span>${type === "danger" ? "⚠️" : "✅"}</span><span>${message}</span>`;
  el.style.display = "flex";
}

function hideAlert(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = "none";
}

// Simple markdown-like renderer (bold, headings, bullets)
function renderMarkdown(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    // headings
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/^## (.+)$/gm,  "<h2>$1</h2>")
    .replace(/^# (.+)$/gm,   "<h1>$1</h1>")
    // bold & italic
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    // horizontal rules
    .replace(/^[-─━]{3,}$/gm, "<hr>")
    // bullet lines
    .replace(/^[•\-] (.+)$/gm, "<li>$1</li>")
    .replace(/(<li>[\s\S]+?<\/li>)(?!\s*<li>)/g, "<ul>$&</ul>")
    // numbered list
    .replace(/^\d+\. (.+)$/gm, "<li>$1</li>")
    // line breaks
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br>")
    .replace(/^/, "<p>").replace(/$/, "</p>");
}

// ── Loading overlay ───────────────────────────────────────────────────────────
function showLoading(msg = "Generating your nutrition plan…") {
  document.getElementById("loadingMsg").textContent = msg;
  showEl("loadingOverlay");
  document.body.style.overflow = "hidden";
}

function hideLoading() {
  hideEl("loadingOverlay");
  document.body.style.overflow = "";
}

// ── Tabs ──────────────────────────────────────────────────────────────────────
function initTabs() {
  $$(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      $$(".tab-btn").forEach(b => b.classList.remove("active"));
      $$(".tab-panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(btn.dataset.tab).classList.add("active");
    });
  });
}

// ── Collect user context from plan form ───────────────────────────────────────
function getUserContext() {
  const getChecked = (name) =>
    Array.from($$(`input[name="${name}"]:checked`)).map(el => el.value);

  const getVal = (id) => (document.getElementById(id) || {}).value || "";

  return {
    name            : getVal("userName"),
    age             : getVal("userAge"),
    gender          : getVal("userGender"),
    city            : getVal("userCity"),
    country         : getVal("userCountry"),
    diet_preference : getVal("dietPreference"),
    activity_level  : getVal("activityLevel"),
    goals           : getChecked("goals"),
    medical_history : getChecked("medical"),
    allergies       : getChecked("allergies"),
  };
}

// ── Plan generation ───────────────────────────────────────────────────────────
function initPlanForm() {
  const form    = document.getElementById("planForm");
  const resultPanel = document.getElementById("planResult");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert("planError");
    resultPanel.classList.remove("show");

    const data = getUserContext();

    if (!data.name.trim()) { showAlert("planError", "Please enter your name."); return; }
    if (!data.age || isNaN(data.age) || data.age < 1 || data.age > 120) {
      showAlert("planError", "Please enter a valid age (1–120)."); return;
    }

    // Store context globally for Q&A tab
    window._userContext = data;

    showLoading("Analysing your profile and generating a personalised nutrition plan…");

    try {
      const resp = await fetch("/api/generate-plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      const result = await resp.json();
      hideLoading();

      if (!result.success) {
        showAlert("planError", result.error || "Failed to generate plan. Please try again.");
        return;
      }

      // Render warning (if any)
      const warnHTML = result.warning
        ? `<div class="warning-box">⚠️ <span>${result.warning}</span></div>`
        : "";

      // Render plan
      document.getElementById("planOutput").innerHTML =
        warnHTML +
        `<div class="plan-content">${renderMarkdown(result.plan)}</div>`;

      // Render disclaimer
      document.getElementById("disclaimerOutput").textContent = result.disclaimer || "";

      resultPanel.classList.add("show");
      resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });

    } catch (err) {
      hideLoading();
      showAlert("planError", "Network error: " + err.message);
    }
  });

  document.getElementById("resetForm").addEventListener("click", () => {
    form.reset();
    resultPanel.classList.remove("show");
    hideAlert("planError");
  });
}

// ── Chat / Q&A ────────────────────────────────────────────────────────────────
function initChat() {
  const chatWindow = document.getElementById("chatWindow");
  const chatInput  = document.getElementById("chatInput");
  const chatSend   = document.getElementById("chatSend");
  const chatForm   = document.getElementById("chatForm");

  if (!chatWindow) return;

  function appendMsg(role, text) {
    const div = document.createElement("div");
    div.className = `chat-msg ${role}`;
    const label = { user: "You", assistant: "NutriCare AI", system: "" }[role] || role;
    div.innerHTML = label
      ? `<div class="msg-label">${label}</div><div>${role === "assistant" ? renderMarkdown(text) : escapeHtml(text)}</div>`
      : `<div>${escapeHtml(text)}</div>`;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return div;
  }

  function escapeHtml(t) {
    return t.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }

  function appendLoader() {
    const div = document.createElement("div");
    div.className = "chat-msg assistant";
    div.innerHTML = `<div class="msg-label">NutriCare AI</div><div class="loader"><div class="spinner"></div> Thinking…</div>`;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return div;
  }

  async function sendQuery(query) {
    if (!query.trim()) return;

    chatInput.value = "";
    chatSend.disabled = true;
    appendMsg("user", query);

    const loaderEl = appendLoader();

    try {
      const resp = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          user_context: window._userContext || {},
        }),
      });

      const result = await resp.json();
      chatWindow.removeChild(loaderEl);

      if (!result.success) {
        appendMsg("system", "⚠️ " + (result.error || "Something went wrong."));
      } else {
        if (result.warning) appendMsg("system", "⚠️ " + result.warning);
        appendMsg("assistant", result.answer);
      }
    } catch (err) {
      chatWindow.removeChild(loaderEl);
      appendMsg("system", "Network error: " + err.message);
    } finally {
      chatSend.disabled = false;
      chatInput.focus();
    }
  }

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    sendQuery(chatInput.value.trim());
  });

  // Suggested questions
  $$(".suggested-q").forEach(btn => {
    btn.addEventListener("click", () => sendQuery(btn.textContent.trim()));
  });
}

// ── Smooth scroll for "Go to Q&A" ────────────────────────────────────────────
function initGoToChat() {
  const btn = document.getElementById("goToChat");
  if (!btn) return;
  btn.addEventListener("click", () => {
    $$(".tab-btn").forEach(b => b.classList.remove("active"));
    $$(".tab-panel").forEach(p => p.classList.remove("active"));
    document.querySelector('[data-tab="tab-qa"]').classList.add("active");
    document.getElementById("tab-qa").classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initPlanForm();
  initChat();
  initGoToChat();
});
