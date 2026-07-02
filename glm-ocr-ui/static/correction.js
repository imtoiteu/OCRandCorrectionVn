/* Vietnamese OCR Correction page. Talks only to /api/correction/* (+ reuses
   /api/documents/<id>/ocr-images for the Image tab). Never touches raw OCR. */
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  let CFG = null, RESULT = null, DOC_ID = null, mdEditing = false;

  async function api(url, opts) {
    const r = await fetch(url, Object.assign({ credentials: "same-origin", headers: { "Content-Type": "application/json" } }, opts || {}));
    let j = null; try { j = await r.json(); } catch (e) {}
    if (!r.ok || (j && j.success === false)) throw new Error((j && j.error) || ("HTTP " + r.status));
    return j;
  }

  function populateModels(providerId) {
    const prov = (CFG.providers || []).find(p => p.id === providerId);
    const sel = $("vc-model"); sel.innerHTML = "";
    (prov ? prov.models : []).forEach(m => {
      const o = document.createElement("option");
      o.value = m.id; o.textContent = m.label + (m.hf ? "  ·  " + m.hf : "");
      sel.appendChild(o);
    });
  }

  async function init() {
    CFG = await api("/api/correction/config");
    const d = CFG.defaults;
    $("vc-enabled-note").textContent = d.enabled ? "" : "(disabled)";
    // providers
    const ps = $("vc-provider"); ps.innerHTML = "";
    (CFG.providers || []).forEach(p => {
      const o = document.createElement("option"); o.value = p.id; o.textContent = p.label; ps.appendChild(o);
    });
    ps.value = d.provider; populateModels(d.provider);
    $("vc-model").value = d.model;
    $("vc-model-path").value = d.model_path || "../models/nano-protonx-legal-tc";
    $("vc-device").value = d.device;
    $("vc-beams").value = d.num_beams; $("vc-maxtok").value = d.max_new_tokens;
    ps.onchange = () => populateModels(ps.value);
    // documents
    try {
      const dd = await api("/api/correction/documents");
      const sel = $("vc-doc"); sel.innerHTML = "";
      (dd.documents || []).forEach(x => {
        const o = document.createElement("option");
        o.value = x.id;
        o.textContent = `#${x.id} ${x.filename}` + (x.has_ocr_json ? "" : "  (no OCR JSON)") + (x.has_corrected ? "  ✓corrected" : "");
        o.disabled = !x.has_ocr_json;
        sel.appendChild(o);
      });
      if (!sel.value && sel.options.length) sel.selectedIndex = 0;
    } catch (e) { /* leave empty */ }

    $("vc-source").onchange = onSource; onSource();
    $("vc-run").onclick = run;
    $("vc-save").onclick = save;
    $("vc-md-edit").onclick = toggleMdEdit;
    document.querySelectorAll(".vc-tab[data-pane]").forEach(t => t.onclick = () => showTab(t.dataset.pane));
  }

  function onSource() {
    const s = $("vc-source").value;
    $("vc-doc-row").style.display = s === "document" ? "" : "none";
    $("vc-paste-row").style.display = s === "document" ? "none" : "";
    $("vc-paste-label").textContent = s === "json" ? "OCR JSON" : "Markdown / text";
    $("vc-paste").placeholder = s === "json"
      ? '[[{"index":0,"label":"text","content":"HÓA DỘN"}]]'
      : "Paste OCR Markdown or plain text…";
  }

  function showTab(pane) {
    document.querySelectorAll(".vc-tab[data-pane]").forEach(t => t.classList.toggle("active", t.dataset.pane === pane));
    document.querySelectorAll(".vc-pane").forEach(p => p.classList.remove("active"));
    $("pane-" + pane).classList.add("active");
    if (pane === "img") loadImage();
  }

  function status(el, msg, cls) { const e = $(el); e.textContent = msg || ""; e.className = "vc-status" + (cls ? " " + cls : ""); }

  async function run() {
    const s = $("vc-source").value;
    const payload = {
      provider: $("vc-provider").value, model: $("vc-model").value,
      model_path: $("vc-model-path").value.trim(),
      device: $("vc-device").value,
      num_beams: parseInt($("vc-beams").value, 10) || undefined,
      max_new_tokens: parseInt($("vc-maxtok").value, 10) || undefined,
    };
    DOC_ID = null;
    if (s === "document") {
      DOC_ID = parseInt($("vc-doc").value, 10);
      if (!DOC_ID) { status("vc-status", "Pick a document with OCR JSON.", "err"); return; }
      payload.doc_id = DOC_ID;
    } else if (s === "json") {
      payload.ocr_json = $("vc-paste").value;
    } else {
      payload.text = $("vc-paste").value; payload.markdown = $("vc-paste").value;
    }
    $("vc-run").disabled = true;
    status("vc-status", "Running correction… (first model load can be slow on CPU)", "busy");
    try {
      const j = await api("/api/correction/run", { method: "POST", body: JSON.stringify(payload) });
      RESULT = j.result; render(j);
      status("vc-status", `Done · ${RESULT.counts.changed} changed / ${RESULT.counts.skipped} protected · ${RESULT.timing.provider_seconds}s`, "ok");
      $("vc-save").disabled = !DOC_ID;
    } catch (e) {
      status("vc-status", "Error: " + e.message, "err");
    } finally { $("vc-run").disabled = false; }
  }

  function render(j) {
    const r = j.result;
    // Markdown
    mdEditing = false; $("vc-md-editor").style.display = "none"; $("vc-md-view").style.display = "";
    $("vc-md-view").contentEditable = "false"; $("vc-md-edit").textContent = "✎ Edit";
    $("vc-md-view").innerHTML = window.marked ? marked.parse(r.corrected_markdown || "") : esc(r.corrected_markdown);
    $("vc-md-editor").value = r.corrected_markdown || "";
    // Source/Text
    $("vc-src-editor").value = r.corrected_text || "";
    // JSON
    $("vc-json").textContent = JSON.stringify(r.corrected_json, null, 2);
    // report
    renderReport(r);
    showTab("md");
  }

  function renderReport(r) {
    const v = r.validation || { checks: [], passed: false };
    let html = `<b>Validation:</b> ${v.passed ? '<span class="vc-check ok">PASSED</span>' : '<span class="vc-check bad">FAILED</span>'} `;
    html += (v.checks || []).map(c => `<span class="vc-check ${c.ok ? "ok" : "bad"}" title="${esc(c.detail)}">${esc(c.name)}</span>`).join("");
    html += `<div style="margin-top:8px;"><b>Changed spans (${(r.changed || []).length})</b></div>`;
    if ((r.changed || []).length) {
      html += "<table class='vc-spans'>" + r.changed.map(s =>
        `<tr><td>idx ${esc(s.block_index)}<br><span class='vc-note'>${esc(s.classification)}${s.status === "rejected_mask" ? " · mask-reject" : ""}</span></td>
             <td><span class='vc-del'>${esc(s.before)}</span><br><span class='vc-add'>${esc(s.after)}</span></td></tr>`).join("") + "</table>";
    }
    const byCat = {};
    (r.skipped || []).forEach(s => { (byCat[s.classification] = byCat[s.classification] || []).push(s.before); });
    html += `<div style="margin-top:8px;"><b>Protected / skipped</b></div>`;
    html += Object.keys(byCat).sort().map(k => `<div class='vc-note'><b>${esc(k)}</b>: ${esc(byCat[k].slice(0, 8).join(" · "))}</div>`).join("") || "<span class='vc-note'>(none)</span>";
    $("vc-report").innerHTML = html;
  }

  function toggleMdEdit() {
    mdEditing = !mdEditing;
    if (mdEditing) {
      $("vc-md-view").style.display = "none"; $("vc-md-editor").style.display = "";
      $("vc-md-edit").textContent = "✔ Preview";
    } else {
      $("vc-md-view").style.display = ""; $("vc-md-editor").style.display = "none";
      $("vc-md-edit").textContent = "✎ Edit";
      $("vc-md-view").innerHTML = window.marked ? marked.parse($("vc-md-editor").value) : esc($("vc-md-editor").value);
    }
  }

  async function loadImage() {
    const box = $("vc-imgs");
    if (!DOC_ID) { box.innerHTML = "<span class='vc-note'>Image view is available for existing OCR documents only.</span>"; return; }
    box.innerHTML = "<span class='vc-note'>Loading image…</span>";
    try {
      const j = await api(`/api/documents/${DOC_ID}/ocr-images`);
      const imgs = (j && j.images) || [];
      box.innerHTML = imgs.length
        ? imgs.map(im => `<div><div class='vc-note'>${esc(im.kind || "image")}${im.page ? " · p" + im.page : ""}</div><img src="${im.src}" alt=""></div>`).join("")
        : "<span class='vc-note'>No annotated image stored for this document.</span>";
    } catch (e) { box.innerHTML = "<span class='vc-note'>Could not load image: " + esc(e.message) + "</span>"; }
  }

  async function save() {
    if (!DOC_ID || !RESULT) return;
    const md = mdEditing ? $("vc-md-editor").value : ($("vc-md-editor").value || RESULT.corrected_markdown);
    const payload = {
      doc_id: DOC_ID,
      corrected_json: RESULT.corrected_json,
      corrected_markdown: md,
      meta: { provider: $("vc-provider").value, model: $("vc-model").value, device: $("vc-device").value,
              timing: RESULT.timing, validation_passed: RESULT.validation.passed, edited: mdEditing || false },
    };
    status("vc-save-status", "Saving…", "busy");
    try {
      const j = await api("/api/correction/save", { method: "POST", body: JSON.stringify(payload) });
      status("vc-save-status", "Saved: " + (j.saved || []).join(", "), "ok");
    } catch (e) { status("vc-save-status", "Save failed: " + e.message, "err"); }
  }

  document.addEventListener("DOMContentLoaded", () => { init().catch(e => status("vc-status", "Init error: " + e.message, "err")); });
})();
