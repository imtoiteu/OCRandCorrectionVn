/* PaddleOCR Studio — app.js */

// ── Toast ──────────────────────────────────────────────
const Toast = {
  show(msg, type = 'info', ms = 3500) {
    const ico = { success:'✅', error:'❌', info:'ℹ️' };
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<span>${ico[type]||'ℹ️'}</span><span>${msg}</span>`;
    document.getElementById('toast-wrap').appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; el.style.transition = 'opacity .3s';
      setTimeout(() => el.remove(), 300); }, ms);
  }
};

// ── Clipboard ──────────────────────────────────────────
// Reliable copy for modern browsers AND http:// LAN origins. The async Clipboard API
// only exists in a secure context (https or localhost); on a plain-http LAN IP it is
// undefined (or rejects), so we fall back to a hidden-textarea execCommand.
// Returns true on success, false on failure.
async function copyTextToClipboard(text) {
  text = text == null ? '' : String(text);
  if (navigator.clipboard && window.isSecureContext) {
    try { await navigator.clipboard.writeText(text); return true; }
    catch (_) { /* fall through to the legacy path below */ }
  }
  try {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed'; ta.style.top = '0'; ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select(); ta.setSelectionRange(0, ta.value.length);
    const ok = document.execCommand('copy');
    document.body.removeChild(ta);
    return ok;
  } catch (_) { return false; }
}

// Copy + toast feedback. Empty/whitespace content → info toast (nothing copied);
// success → green message (custom or "Copied!"); failure → red "Failed to copy".
async function copyWithToast(text, successMsg) {
  const s = text == null ? '' : String(text);
  if (!s.trim()) { Toast.show(t('copy_nothing'), 'info'); return false; }
  const ok = await copyTextToClipboard(s);
  Toast.show(ok ? (successMsg || t('copied')) : t('copy_failed'), ok ? 'success' : 'error');
  return ok;
}

// Safe JSON parse — if the server returns an HTML error page instead of JSON
// (Flask 500 without a custom error handler), .json() throws a SyntaxError that
// appears as "Unexpected token '<'". safeJson() catches that and returns a
// structured error object so the caller can show a readable toast.
async function safeJson(resp) {
  const text = await resp.text();
  try {
    return JSON.parse(text);
  } catch (_) {
    // Strip HTML tags to extract the useful part of the error message.
    const plain = text.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 200);
    return { success: false, error: `Server error (HTTP ${resp.status}): ${plain}` };
  }
}

// ── API ────────────────────────────────────────────────
const API = {
  async upload(file) {
    const fd = new FormData(); fd.append('file', file);
    const r = await fetch('/api/upload', { method: 'POST', body: fd });
    return r.json();
  },
  async ocrPage(fileId, page, engine = 'auto', aiEnhancement = false, previewOnly = false) {
    const r = await fetch('/api/ocr/page', { method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ file_id: fileId, page, engine: engine, ai_enhancement: aiEnhancement, preview_only: previewOnly }) });
    return safeJson(r);
  },
  async ocrAll(fileId, engine = 'auto', aiEnhancement = false) {
    const r = await fetch('/api/ocr/all', { method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ file_id: fileId, engine: engine, ai_enhancement: aiEnhancement }) });
    return safeJson(r);
  },
  async readText(fileId) {
    return (await fetch('/api/read-text', { method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ file_id: fileId }) })).json();
  },
  async getDocText(docId) {                       // G1: persisted artifacts for a document
    return (await fetch(`/api/documents/${docId}/text`)).json();
  },
  async getOcrImages(docId) {                      // lazy: base64 extracted-image artifacts
    return (await fetch(`/api/documents/${docId}/ocr-images`)).json();
  }
};

// ── Shared state ───────────────────────────────────────
const State = {
  ocrText: '',           // last OCR full text (used by the OCR result downloads/copy)
  setOcrText(t) { this.ocrText = t; }
};

// ── Download ───────────────────────────────────────────
function dlTxt(text, name = 'result.txt') {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type:'text/plain' }));
  a.download = name; a.click();
}
function dlBlob(text, name, mime = 'text/plain') {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], { type: mime }));
  a.download = name; a.click();
}

// ── Minimal HTML sanitizer for rendering model-produced tables (own-document,
//    same-user context). Strips active content and event/URL handlers. ────────
function sanitizeHtml(html) {
  const tmp = document.createElement('div');
  tmp.innerHTML = String(html || '');
  tmp.querySelectorAll('script,style,iframe,object,embed,link,meta').forEach(n => n.remove());
  tmp.querySelectorAll('*').forEach(el => {
    [...el.attributes].forEach(a => {
      const n = a.name.toLowerCase();
      if (n.startsWith('on') ||
          ((n === 'href' || n === 'src') && /^\s*javascript:/i.test(a.value))) {
        el.removeAttribute(a.name);
      }
    });
  });
  return tmp.innerHTML;
}

// ── LaTeX → HTML via vendored KaTeX (offline). Returns null on failure so the
//    caller can leave the original delimiters in place. ────────────────────────
function katexToHtml(tex, displayMode) {
  try {
    if (window.katex) {
      return window.katex.renderToString(tex, { displayMode, throwOnError: false, strict: false });
    }
  } catch (_) { /* fall through */ }
  return null;
}

// ── Markdown → sanitized HTML (vendored marked; raw HTML tables pass through),
//    with offline KaTeX math rendering. GLM/Modern emit LaTeX ($…$, $$…$$, \(…\),
//    \[…\]); marked has no math support AND mangles backslashes (the \\ row breaks
//    in arrays/matrices collapse to \), so math is rendered with KaTeX BEFORE marked
//    tokenizes — swapped out for placeholders, then the trusted KaTeX HTML is
//    restored after marked + sanitize. `math` is gated on real markdown so bare `$`
//    in plain text (currency) is never mistaken for inline math. ─────────────────
function renderMarkdown(md, math) {
  let src = String(md || '');
  if (!src.trim()) return '';
  const store = [];
  // Private-use sentinels survive HTML round-trips and are never markdown-special.
  const stash = (html) => '\uE000' + (store.push(html) - 1) + '\uE001';
  if (math && window.katex) {
    // Display math first ($$…$$, \[…\]), then inline ($…$, \(…\)).
    src = src.replace(/\$\$([\s\S]+?)\$\$/g,   (m, t) => { const h = katexToHtml(t.trim(), true);  return h ? '\n\n' + stash(h) + '\n\n' : m; });
    src = src.replace(/\\\[([\s\S]+?)\\\]/g,   (m, t) => { const h = katexToHtml(t.trim(), true);  return h ? '\n\n' + stash(h) + '\n\n' : m; });
    src = src.replace(/\$(?!\$)((?:\\.|[^$\\\n])+?)\$/g, (m, t) => { const h = katexToHtml(t, false); return h ? stash(h) : m; });
    src = src.replace(/\\\(([\s\S]+?)\\\)/g,   (m, t) => { const h = katexToHtml(t, false); return h ? stash(h) : m; });
  }
  let html = null;
  try {
    if (window.marked) html = window.marked.parse ? window.marked.parse(src) : window.marked(src);
  } catch (_) { /* fall through to escaped plaintext */ }
  if (html == null) html = '<pre>' + esc(src) + '</pre>';
  html = sanitizeHtml(html);
  // Restore trusted KaTeX HTML (we generated it; KaTeX never emits scripts/handlers).
  if (store.length) html = html.replace(/\uE000(\d+)\uE001/g, (_, i) => store[+i] || '');
  return html;
}

// ── Router ─────────────────────────────────────────────
// Hash-based router: location.hash is the single source of truth for SPA view
// state, so browser Back/Forward (and bookmarks/refresh) work natively. Admin is
// a separate server-rendered app at /admin/* and is reached by real navigation.
const Router = {
  current: null,
  views: {},
  register(name, el) { this.views[name] = el; },
  _show(name) {
    Object.entries(this.views).forEach(([n, el]) => el.classList.toggle('v-hidden', n !== name));
    this.current = name;
    document.querySelectorAll('.nav-link').forEach(l =>
      l.classList.toggle('active', l.dataset.view === name));
  },
  // Navigate by setting the hash (optionally with a deep-link arg). The hashchange
  // listener calls _render(); calling with the current hash re-renders in place.
  goto(name, arg) {
    const hash = '#' + name + (arg ? '/' + encodeURIComponent(arg) : '');
    if (location.hash === hash) this._render();
    else location.hash = hash;
  },
  back() { history.back(); },
  // Render the view + run any deep-link handler from the current hash.
  _render() {
    const raw = (location.hash || '').replace(/^#/, '');
    const slash = raw.indexOf('/');
    const name  = (slash === -1 ? raw : raw.slice(0, slash)) || 'home';
    const arg   = slash === -1 ? null : decodeURIComponent(raw.slice(slash + 1));
    const view  = this.views[name] ? name : 'home';
    this._show(view);
    // Deep links reuse existing open paths (loaders, NOT navigators — no goto here).
    if (view === 'ocr' && arg && typeof OCRView !== 'undefined') {
      OCRView._openFromFileId(arg);
    }
  },
  init() {
    window.addEventListener('hashchange', () => this._render());
    this._render();
  }
};

// ══════════════════════════════════════════════════════
// OCR View
// ══════════════════════════════════════════════════════
const OCRView = {
  fileId: null, isPdf: false, pageCount: 1, currentPage: 1,
  pages: {}, zoom: 1, rotate: 0, canvas: null,
  ocrEngine: 'glmocr', _sessionEngine: 'glmocr',  // default = ⭐ Recommended; _sessionEngine remembers a manual pick across in-app navigation
  ocrAi: false, ocrLayout: 'enhanced', ocrSelectionMode: false,
  ocrView: 'md',      // active result tab: md | raw | images | json
  _abortCtrl: null,   // active AbortController for the current OCR fetch
  // Cache of the current page's renderable artifacts (driven by the OCR response /
  // restored artifacts), so tab switches and downloads don't recompute.
  _plainText: '', _markdown: '', _hasRealMd: false, _images: [], _jsonText: '',
  _curDocId: null,    // document id (for lazy image fetch when restoring a saved doc)

  init() {
    this.canvas = new OCRCanvas(
      document.getElementById('overlay-canvas'),
      document.getElementById('preview-img')
    );
    this.canvas.onHover  = (i, e) => this._hover(i, e);
    this.canvas.onSelect = i => this._select(i);
    this.canvas.onRegionSelect = rect => this._onRegionSelect(rect);

    document.getElementById('ocr-file-input').addEventListener('change', e => {
      if (e.target.files[0]) this._upload(e.target.files[0]);
    });
    const dz = document.getElementById('ocr-drop-zone');
    const fi = document.getElementById('ocr-file-input');
    dz.addEventListener('click', () => fi.click());
    dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('drag-over'); });
    dz.addEventListener('dragleave', () => dz.classList.remove('drag-over'));
    dz.addEventListener('drop', e => { e.preventDefault(); dz.classList.remove('drag-over');
      if (e.dataTransfer.files[0]) this._upload(e.dataTransfer.files[0]); });

    document.getElementById('btn-ocr-run').addEventListener('click', () => this._ocrPage(this.currentPage));
    document.getElementById('btn-ocr-all').addEventListener('click', () => this._ocrAll());
    document.getElementById('btn-ocr-reset').addEventListener('click', () => this._reset());
    document.getElementById('btn-ocr-stop').addEventListener('click', () => this._ocrStop());
    document.getElementById('btn-zoom-in').addEventListener('click',  () => this._setZoom(this.zoom + 0.2));
    document.getElementById('btn-zoom-out').addEventListener('click', () => this._setZoom(this.zoom - 0.2));
    document.getElementById('btn-zoom-fit').addEventListener('click', () => this._setZoom(1));
    document.getElementById('btn-rotate').addEventListener('click', () => { this.rotate=(this.rotate+90)%360; this._applyTransform(); });
    document.getElementById('btn-select-region').addEventListener('click', () => {
      this.ocrSelectionMode = !this.ocrSelectionMode;
      document.getElementById('btn-select-region').classList.toggle('active', this.ocrSelectionMode);
      this.canvas.setSelectionMode(this.ocrSelectionMode);
    });
    document.getElementById('btn-prev-page').addEventListener('click', () => this._goPage(this.currentPage - 1));
    document.getElementById('btn-next-page').addEventListener('click', () => this._goPage(this.currentPage + 1));
    document.getElementById('ocr-page-input').addEventListener('change', e => this._goPage(+e.target.value));
    document.getElementById('ocr-copy-btn').addEventListener('click', () => {
      const text = this.ocrView === 'json' ? this._jsonText : this._activeOcrText();
      copyWithToast(text, t('toast_text_copied'));
    });
    // Download Markdown (real markdown when present, else plain text rendered as .md).
    document.getElementById('ocr-dl-md').addEventListener('click', () =>
      dlBlob(this._markdown || this._plainText || '', 'ocr-result.md', 'text/markdown'));
    // Download JSON (structured OCR output across all pages).
    document.getElementById('ocr-dl-json').addEventListener('click', () =>
      dlBlob(this._buildJsonExport(), 'ocr-result.json', 'application/json'));
    document.getElementById('ocr-dl-txt').addEventListener('click', () =>
      dlTxt(this._plainText || State.ocrText || '', 'ocr-result.txt'));
    // Download DOCX — converts current markdown via pandoc on the server.
    document.getElementById('ocr-dl-docx').addEventListener('click', () => this._exportDocx());

    // ── Structured-output view tabs (Text / Markdown / HTML / Table) ──────────
    document.querySelectorAll('#ocr-view-tabs .ocr-vtab').forEach(btn => {
      btn.addEventListener('click', () => this._setOcrView(btn.dataset.vtab));
    });

    // ── OCR Engine & AI selector ──────────────────────────────────────────
    const engineSelect = document.getElementById('ocr-engine-select');
    if (engineSelect) {
      engineSelect.addEventListener('change', (e) => {
        // Respect & persist the user's manual choice for the rest of the session;
        // never auto-switch away from it (see _resetMode).
        this.ocrEngine = e.target.value;
        this._sessionEngine = e.target.value;
      });
      engineSelect.value = this.ocrEngine;
    }
    document.querySelectorAll('#ocr-layout-toggle .ocr-mode-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        this.ocrLayout = btn.dataset.layout;
        this._updateModeSelector();
        // Immediately re-render current page from cache
        const cacheKey = this.ocrEngine + '_' + this.ocrAi;
        const cached = this.pages[this.currentPage]?.[cacheKey];
        if (cached) {
          const results = this.ocrLayout === 'original' ? (cached.raw_results || cached.results) : cached.results;
          if (this.canvas) {
            this.canvas.load(results, cached.img_width, cached.img_height);
            this.canvas.draw();
          }
          this._renderResults(cached); this._renderStructured(cached); this._updateStats(cached);
          this._renderTextAll();
        }
      });
    });
    this._updateModeSelector();

    window.addEventListener('resize', () => { if (this.canvas) { this.canvas.resize(); this.canvas.draw(); } });
  },

  _updateModeSelector() {
    document.querySelectorAll('#ocr-layout-toggle .ocr-mode-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.layout === this.ocrLayout);
    });
  },

  _resetMode() {
    // Keep the user's session engine choice (default ⭐ Recommended) across nav.
    this.ocrEngine = this._sessionEngine || 'glmocr';
    this.ocrAi = false;
    this.ocrLayout = 'enhanced';
    const engineSelect = document.getElementById('ocr-engine-select');
    if (engineSelect) engineSelect.value = this.ocrEngine;
    this._updateModeSelector();
  },

  // Clear the viewer's visible state to a clean blank slate. Used when loading a
  // NEW file (upload or from the library) so the previous file's OCR text/boxes/
  // stats never linger in the DOM. (Fixes: opening a file showed the last file's
  // OCR when the selected file had no persisted OCR of its own.)
  _resetViewerState() {
    const detList = document.getElementById('det-list');
    if (detList) detList.innerHTML = '';
    const empty = document.getElementById('ocr-empty-results');
    if (empty) empty.style.display = 'flex';
    const sReg = document.getElementById('stat-regions'); if (sReg) sReg.textContent = '0';
    const sConf = document.getElementById('stat-conf'); if (sConf) sConf.textContent = '—';
    const sTime = document.getElementById('stat-time'); if (sTime) sTime.textContent = '0';
    const sPages = document.getElementById('stat-pages');
    if (sPages) sPages.textContent = `${this.currentPage || 1}/${this.pageCount || '?'}`;
    const raw = document.getElementById('ocr-md-raw'); if (raw) raw.value = '';
    const rend = document.getElementById('ocr-md-rendered'); if (rend) rend.innerHTML = '';
    const imgs = document.getElementById('ocr-images'); if (imgs) imgs.innerHTML = '';
    const jsn = document.getElementById('ocr-json'); if (jsn) { const c = jsn.querySelector('code'); if (c) c.textContent = ''; }
    this._plainText = ''; this._markdown = ''; this._hasRealMd = false; this._images = []; this._jsonText = '';
    this._curDocId = null;
    const badge = document.getElementById('ocr-status-badge');
    if (badge) badge.style.display = 'none';
    if (this.canvas) this.canvas.load([], 1, 1);
    if (typeof State !== 'undefined' && State.setOcrText) State.setOcrText('');
  },


  async _upload(file) {
    const allowed = ['.jpg','.jpeg','.png','.webp','.pdf'];
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!allowed.includes(ext)) { Toast.show(t('toast_unsupported'), 'error'); return; }
    
    // Reset file input so same file can be selected again
    const fi = document.getElementById('ocr-file-input');
    if (fi) fi.value = '';

    this.isPdf = ext === '.pdf';
    this.currentPage = 1;
    this.pageCount = 1;
    this.pages = {};
    this.fileId = null;

    // 1. Swap UI IMMEDIATELY
    document.getElementById('ocr-upload-zone').style.display = 'none';
    document.getElementById('ocr-workspace').style.display = 'grid';
    document.getElementById('ocr-file-name').textContent = file.name;

    // 2. Clear UI state (shared with library-open so neither leaks prior results)
    this._resetViewerState();

    // 3. Display Local Preview IMMEDIATELY
    const img = document.getElementById('preview-img');
    if (!this.isPdf) {
      if (this._previewUrl) URL.revokeObjectURL(this._previewUrl);
      this._previewUrl = URL.createObjectURL(file);
      
      img.onload = () => {
        if (this.canvas) {
          this.canvas.load([], img.naturalWidth, img.naturalHeight);
        }
        this._applyTransform();
      };
      img.src = this._previewUrl;
      img.style.display = 'block';
    } else {
      if (this.canvas) this.canvas.load([], 1, 1);
      // For PDFs, we'll request a preview from the backend after upload
      img.src = ''; 
      img.style.display = 'none';
    }

    // 4. Background Upload
    try {
      const data = await API.upload(file);
      if (!data.success) { Toast.show(data.error, 'error'); return; }
      
      this.fileId = data.file_id;
      this.pageCount = data.page_count;
      document.getElementById('stat-pages').textContent = `1/${this.pageCount}`;
      this._buildTabs();
      this._updateNav();
      
      // 5. If PDF, trigger immediate preview of Page 1
      if (this.isPdf) this._ocrPage(1, true); 
    } catch (e) {
      Toast.show(e.message, 'error');
    }
  },

  _buildTabs() {
    const bar = document.getElementById('page-tabs-bar');
    bar.style.display = this.isPdf && this.pageCount > 1 ? 'flex' : 'none';
    bar.innerHTML = '';
    for (let p = 1; p <= this.pageCount; p++) {
      const b = document.createElement('button'); b.className = 'pg-tab'; b.textContent = `Page ${p}`; b.dataset.page = p;
      b.addEventListener('click', () => this._goPage(p)); bar.appendChild(b);
    }
    this._updateTabs();
  },
  _updateTabs() {
    document.querySelectorAll('.pg-tab').forEach(t => {
      const p = +t.dataset.page;
      const pageModes = this.pages[p] || {};
      const hasAnyMode = !!(pageModes.standard || pageModes.smart);
      t.classList.toggle('active', p === this.currentPage);
      t.classList.toggle('done', hasAnyMode && p !== this.currentPage);
    });
  },
  _goPage(p) {
    p = Math.max(1, Math.min(this.pageCount, p));
    this.currentPage = p; this._updateNav(); this._updateTabs();
    const cacheKey = this.ocrEngine + '_' + this.ocrAi;
    const cached = this.pages[p]?.[cacheKey];
    if (cached) this._renderPage(cached);
    else this._ocrPage(p, true);
  },
  _updateNav() {
    document.getElementById('ocr-page-input').value = this.currentPage;
    document.getElementById('ocr-page-total').textContent = `/ ${this.pageCount}`;
    document.getElementById('btn-prev-page').disabled = this.currentPage <= 1;
    document.getElementById('btn-next-page').disabled = this.currentPage >= this.pageCount;
  },

  async _ocrPage(p, previewOnly = false) {
    if (!previewOnly) this._setLoading(true);
    this._abortCtrl = new AbortController();
    try {
      const data = await API.ocrPage(this.fileId, p, this.ocrEngine, this.ocrAi, previewOnly, this._abortCtrl.signal);
      if (!data.success) { Toast.show(data.error, 'error'); return; }
      this.pages[p] ||= {};
      const cacheKey = this.ocrEngine + '_' + this.ocrAi;
      this.pages[p][cacheKey] = data;
      this._renderPage(data); this._updateTabs();
      // A preview load (opening a file) returns no regions — the real count comes from
      // the restored artifact, so only announce a count for an actual OCR run.
      if (!previewOnly) {
        const modeLabel = this.ocrAi ? ' 🧠' : '';
        Toast.show(`${t('nav_ocr')}: ${data.results.length} ${t('regions_found')}${modeLabel}`, 'success');
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        Toast.show('OCR cancelled.', 'info');
      } else {
        Toast.show('OCR failed: ' + err.message, 'error');
      }
    } finally {
      this._abortCtrl = null;
      if (!previewOnly) this._setLoading(false);
    }
  },

  async _ocrAll() {
    this._setLoading(true, true);
    this._abortCtrl = new AbortController();
    try {
      const data = await API.ocrAll(this.fileId, this.ocrEngine, this.ocrAi, this._abortCtrl.signal);
      if (!data.success) { Toast.show(data.error, 'error'); return; }
      const cacheKey = this.ocrEngine + '_' + this.ocrAi;
      data.pages.forEach(p => {
        this.pages[p.page_num] ||= {};
        this.pages[p.page_num][cacheKey] = p;
      });
      this._renderPage(this.pages[this.currentPage][cacheKey]);
      this._updateTabs(); this._updateStats();
      const modeLabel = this.ocrAi ? ' 🧠' : '';
      Toast.show(`${data.pages.length} ${t('pages_done')}${modeLabel}`, 'success');
    } catch (err) {
      if (err.name === 'AbortError') {
        Toast.show('OCR cancelled.', 'info');
      } else {
        Toast.show('OCR all failed: ' + err.message, 'error');
      }
    } finally {
      this._abortCtrl = null;
      this._setLoading(false);
    }
  },

  _ocrStop() {
    if (this._abortCtrl) {
      this._abortCtrl.abort();
    }
  },

  _renderPage(data) {
    const img = document.getElementById('preview-img');
    img.style.display = 'block';
    img.onload = () => {
      document.getElementById('overlay-canvas').classList.add('interactive');
      const results = this.ocrLayout === 'original' ? (data.raw_results || data.results) : data.results;
      this.canvas.load(results, data.img_width, data.img_height);
      this._applyTransform();
    };
    img.src = `data:image/png;base64,${data.page_image_b64}`;
    this._renderResults(data); this._renderStructured(data); this._updateStats(data);
    this._renderTextAll();
  },

  _renderTextAll() {
    const cacheKey = this.ocrEngine + '_' + this.ocrAi;
    const allText = Object.values(this.pages)
      .map(pageModes => pageModes?.[cacheKey])
      .filter(Boolean)
      .flatMap(p => {
        const arr = this.ocrLayout === 'original' ? (p.raw_results || p.results) : p.results;
        return (arr || []).map(r => r.text);
      })
      .join('\n');
    State.setOcrText(allText);
  },

  _renderResults(data) {
    const list = document.getElementById('det-list');
    const empty = document.getElementById('ocr-empty-results');
    // Only remove detection items — keep #ocr-empty-results in the DOM
    list.querySelectorAll('.det-item').forEach(el => el.remove());
    const results = this.ocrLayout === 'original' ? (data?.raw_results || data?.results) : data?.results;
    if (!results?.length) { if (empty) empty.style.display='flex'; return; }
    if (empty) empty.style.display = 'none';
    results.forEach((item, i) => {
      const cc = item.confidence >= .9 ? 'conf-high' : item.confidence >= .7 ? 'conf-med' : 'conf-low';
      const div = document.createElement('div'); div.className='det-item'; div.id=`det-${i}`;
      div.innerHTML = `<span class="det-text">${esc(item.text)}</span>
        ${item.confidence!=null?`<span class="det-conf ${cc}">${(item.confidence*100).toFixed(1)}%</span>`:''}`;
      div.addEventListener('click', () => {
        document.querySelectorAll('.det-item').forEach(d=>d.classList.remove('selected'));
        div.classList.add('selected'); this.canvas.selectByIndex(i); this.canvas.draw();
      });
      list.appendChild(div);
    });
  },

  // Content sent to Correct/Translate/Summarize. On the Markdown tabs (rendered/raw)
  // send markdown when the engine produced real markdown, otherwise plain text. The
  // raw textarea is editable, so its (possibly edited) value wins on the raw tab.
  _activeOcrText() {
    const raw = document.getElementById('ocr-md-raw');
    if (this.ocrView === 'raw' && raw) return raw.value;
    if (this.ocrView === 'md')  return this._hasRealMd ? (this._markdown || '') : (this._plainText || '');
    return this._plainText || (raw ? raw.value : '');
  },

  _setOcrView(tab) {
    // Don't switch to a disabled tab (e.g. Images when there are none).
    const btn = document.querySelector(`#ocr-view-tabs .ocr-vtab[data-vtab="${tab}"]`);
    if (btn && btn.disabled) tab = 'md';
    this.ocrView = tab;
    document.querySelectorAll('#ocr-view-tabs .ocr-vtab').forEach(b =>
      b.classList.toggle('active', b.dataset.vtab === tab));
    const show = (id, on) => { const el = document.getElementById(id); if (el) el.style.display = on ? '' : 'none'; };
    show('ocr-md-rendered', tab === 'md');
    show('ocr-md-raw',      tab === 'raw');
    show('ocr-images',      tab === 'images');
    show('ocr-json',        tab === 'json');
    // Lazily fetch extracted images for a restored document the first time the tab opens.
    if (tab === 'images' && !this._images.length && this._curDocId != null) {
      this._loadImagesForDoc(this._curDocId);
    }
  },

  // Artifact-driven renderer: populates all four tabs from a page result (live OCR)
  // or a restore-synthesized object. Markdown is the default; the Images tab is
  // disabled when the engine produced no visual artifacts. No per-engine forks.
  _renderStructured(data) {
    const results = (data && (data.results)) || [];
    const plain = results.map(r => r.text).filter(s => (s || '').trim()).join('\n');
    const realMd = (data && typeof data.markdown === 'string' && data.markdown.trim()) ? data.markdown : '';
    const md = realMd || plain;
    this._plainText = plain;
    this._markdown  = realMd;
    this._hasRealMd = !!realMd;
    this._images    = (data && data.images) || [];

    const rend = document.getElementById('ocr-md-rendered');
    if (rend) rend.innerHTML = renderMarkdown(md, this._hasRealMd) ||
      '<div class="output-empty"><div class="oe-icon">📝</div><div>No text</div></div>';
    const raw = document.getElementById('ocr-md-raw');
    if (raw) raw.value = md;

    // JSON: prefer the engine's structured raw_json; else the results + layout blocks.
    // raw_json may be an array (GLM pages), an object (hybrid engine), or absent.
    const rawJ = data && data.raw_json;
    const jsonObj = rawJ != null ? rawJ : {
      results, layout_blocks: (data && data.layout_blocks) || undefined,
    };
    this._jsonText = JSON.stringify(jsonObj, null, 2);
    const jc = document.querySelector('#ocr-json code');
    if (jc) jc.textContent = this._jsonText;

    this._renderImages(this._images);
    this._setOcrView(this.ocrView || 'md');
  },

  // Document-viewer rendering: one large fit-to-container stage (wheel/click zoom + drag
  // pan) plus a horizontal thumbnail strip when there's more than one image.
  _renderImages(images) {
    const box = document.getElementById('ocr-images');
    const tabBtn = document.querySelector('#ocr-view-tabs .ocr-vtab[data-vtab="images"]');
    const has = !!(images && images.length);
    if (tabBtn) { tabBtn.disabled = !has; tabBtn.classList.toggle('disabled', !has); }
    if (!box) return;
    if (!has) {
      this._iv = null;
      box.innerHTML = '<div class="output-empty"><div class="oe-icon">🖼</div><div>No extracted images for this engine</div></div>';
      return;
    }
    const multi = images.length > 1;
    const cap = im => `${esc(im.kind || 'image')}${im.page ? (' · p' + im.page) : ''}`;
    box.innerHTML = `
      <div class="ocr-iv-stage" tabindex="0">
        <img class="ocr-iv-img" draggable="false" alt="">
        <div class="ocr-iv-bar">
          <button class="ocr-iv-btn" data-iv="out" title="Zoom out">−</button>
          <span class="ocr-iv-zoom">100%</span>
          <button class="ocr-iv-btn" data-iv="in" title="Zoom in">+</button>
          <button class="ocr-iv-btn" data-iv="fit" title="Fit to view">⤢</button>
          <span class="ocr-iv-count"></span>
        </div>
        <div class="ocr-iv-cap"></div>
      </div>
      ${multi ? `<div class="ocr-iv-strip">${images.map((im, i) => `
        <button class="ocr-iv-thumb" data-idx="${i}" title="${esc(im.label || cap(im))}">
          <img src="${im.src}" alt="" loading="lazy">
          <span>${cap(im)}</span>
        </button>`).join('')}</div>` : ''}`;
    this._initImageViewer(images);
  },

  // Wire zoom (wheel + buttons), click-to-zoom-toggle, drag-to-pan and thumbnail
  // navigation for the Extracted Images stage. State lives on this._iv.
  _initImageViewer(images) {
    const box = document.getElementById('ocr-images');
    const stage = box.querySelector('.ocr-iv-stage');
    const img = box.querySelector('.ocr-iv-img');
    const zoomLbl = box.querySelector('.ocr-iv-zoom');
    const countLbl = box.querySelector('.ocr-iv-count');
    const capLbl = box.querySelector('.ocr-iv-cap');
    const iv = this._iv = { images, idx: 0, scale: 1, tx: 0, ty: 0, drag: null, moved: false };

    const apply = () => {
      img.style.transform = `translate(${iv.tx}px, ${iv.ty}px) scale(${iv.scale})`;
      img.style.cursor = iv.scale > 1 ? (iv.drag ? 'grabbing' : 'grab') : 'zoom-in';
      if (zoomLbl) zoomLbl.textContent = Math.round(iv.scale * 100) + '%';
    };

    // Keep the (zoomed) image overlapping the stage so it can't be panned out of view.
    const clampPan = () => {
      const sr = stage.getBoundingClientRect();
      const maxX = Math.max(0, (img.offsetWidth * iv.scale - sr.width) / 2);
      const maxY = Math.max(0, (img.offsetHeight * iv.scale - sr.height) / 2);
      iv.tx = Math.max(-maxX, Math.min(maxX, iv.tx));
      iv.ty = Math.max(-maxY, Math.min(maxY, iv.ty));
    };

    // Zoom toward a screen point (cursor), keeping that point stationary.
    const zoomAt = (px, py, factor) => {
      const s0 = iv.scale, s1 = Math.max(1, Math.min(8, s0 * factor));
      if (s1 === s0) return;
      const sr = stage.getBoundingClientRect();
      const cx = sr.left + img.offsetLeft + img.offsetWidth / 2;   // untransformed center
      const cy = sr.top + img.offsetTop + img.offsetHeight / 2;
      iv.tx += (s0 - s1) / s0 * (px - cx - iv.tx);
      iv.ty += (s0 - s1) / s0 * (py - cy - iv.ty);
      iv.scale = s1;
      if (s1 === 1) { iv.tx = 0; iv.ty = 0; }
      clampPan(); apply();
    };

    const select = (i) => {
      iv.idx = (i + images.length) % images.length;
      const im = images[iv.idx];
      img.src = im.src;
      iv.scale = 1; iv.tx = 0; iv.ty = 0;
      box.querySelectorAll('.ocr-iv-thumb').forEach((t, k) => t.classList.toggle('active', k === iv.idx));
      if (countLbl) countLbl.textContent = images.length > 1 ? `${iv.idx + 1} / ${images.length}` : '';
      if (capLbl) capLbl.textContent = im.label || `${im.kind || 'image'}${im.page ? (' · p' + im.page) : ''}`;
      apply();
    };

    stage.addEventListener('wheel', (e) => {
      e.preventDefault();
      zoomAt(e.clientX, e.clientY, e.deltaY < 0 ? 1.15 : 1 / 1.15);
    }, { passive: false });

    img.addEventListener('pointerdown', (e) => {
      iv.moved = false;
      if (iv.scale <= 1) return;
      iv.drag = { x: e.clientX, y: e.clientY, tx: iv.tx, ty: iv.ty };
      try { img.setPointerCapture(e.pointerId); } catch (_) {}
      apply();
    });
    img.addEventListener('pointermove', (e) => {
      if (!iv.drag) return;
      iv.moved = true;
      iv.tx = iv.drag.tx + (e.clientX - iv.drag.x);
      iv.ty = iv.drag.ty + (e.clientY - iv.drag.y);
      clampPan(); apply();
    });
    const endDrag = (e) => {
      if (!iv.drag) return;
      iv.drag = null;
      try { img.releasePointerCapture(e.pointerId); } catch (_) {}
      apply();
    };
    img.addEventListener('pointerup', endDrag);
    img.addEventListener('pointercancel', endDrag);

    // Click toggles between fit and 2.2× at the click point (suppressed after a pan).
    img.addEventListener('click', (e) => {
      if (iv.moved) { iv.moved = false; return; }
      if (iv.scale > 1) { iv.scale = 1; iv.tx = 0; iv.ty = 0; apply(); }
      else zoomAt(e.clientX, e.clientY, 2.2);
    });

    box.querySelectorAll('.ocr-iv-btn').forEach(b => b.addEventListener('click', () => {
      const sr = stage.getBoundingClientRect();
      const cx = sr.left + sr.width / 2, cy = sr.top + sr.height / 2;
      if (b.dataset.iv === 'in') zoomAt(cx, cy, 1.3);
      else if (b.dataset.iv === 'out') zoomAt(cx, cy, 1 / 1.3);
      else { iv.scale = 1; iv.tx = 0; iv.ty = 0; apply(); }
    }));

    box.querySelectorAll('.ocr-iv-thumb').forEach(t =>
      t.addEventListener('click', () => select(parseInt(t.dataset.idx, 10))));

    stage.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { select(iv.idx + 1); e.preventDefault(); }
      else if (e.key === 'ArrowLeft') { select(iv.idx - 1); e.preventDefault(); }
    });

    select(0);
  },

  // Aggregate the structured JSON across all OCR'd pages for the JSON download.
  _buildJsonExport() {
    const cacheKey = this.ocrEngine + '_' + this.ocrAi;
    const out = [];
    Object.keys(this.pages).map(Number).sort((a, b) => a - b).forEach(pn => {
      const p = this.pages[pn]?.[cacheKey];
      if (!p) return;
      if (Array.isArray(p.raw_json)) out.push(...p.raw_json);
      else if (p.raw_json != null) out.push(p.raw_json);
      else out.push({ page: pn, results: p.results || [], layout_blocks: p.layout_blocks || [] });
    });
    return JSON.stringify(out.length ? out : (this._jsonText ? JSON.parse(this._jsonText) : []), null, 2);
  },

  // Export current OCR markdown as a Word DOCX file via the backend pandoc route.
  async _exportDocx() {
    const md = this._markdown || this._plainText || '';
    if (!md.trim()) {
      Toast.show('No OCR text to export.', 'info');
      return;
    }
    // Derive a clean filename stem from the document name shown in the toolbar.
    const nameEl = document.getElementById('ocr-file-name');
    const rawName = nameEl ? nameEl.textContent.trim() : '';
    const stem = rawName.replace(/\.[^.]+$/, '').replace(/[^\w\-]/g, '-').slice(0, 80) || 'ocr-result';

    const btn = document.getElementById('ocr-dl-docx');
    const origHtml = btn ? btn.innerHTML : '';
    if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spin"></span> DOCX'; }

    try {
      const resp = await fetch('/api/ocr/export-docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ markdown: md, filename: stem }),
      });

      if (!resp.ok) {
        // Server returned JSON error
        let msg = `DOCX export failed (${resp.status})`;
        try {
          const j = await resp.json();
          if (j && j.error) msg = j.error;
        } catch (_) {}
        Toast.show(msg, 'error');
        return;
      }

      // Stream the blob and trigger browser download
      const blob = await resp.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      a.download = `${stem}.docx`;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 2000);
      Toast.show('DOCX exported.', 'success');
    } catch (err) {
      Toast.show('DOCX export error: ' + err.message, 'error');
    } finally {
      if (btn) { btn.disabled = false; btn.innerHTML = origHtml; }
    }
  },

  async _loadImagesForDoc(docId) {
    try {
      const r = await API.getOcrImages(docId);
      if (r && r.success && r.images && r.images.length) {
        this._images = r.images;
        this._renderImages(r.images);
        if (this.ocrView === 'images') this._setOcrView('images');
      }
    } catch (_) { /* leave tab disabled */ }
  },

  _updateStats(data) {
    let all=[]; let ms=0; let pg=Object.keys(this.pages).length;
    const cacheKey = this.ocrEngine + '_' + this.ocrAi;
    Object.values(this.pages).forEach(pageModes=>{
      const p = pageModes?.[cacheKey];
      if (p) { all=[...all,...(p.results||[])]; ms+=p.elapsed_ms||0; }
    });
    if(data){all=data.results;ms=data.elapsed_ms;}
    const avg = all.length ? all.reduce((s,r)=>s+(r.confidence||0),0)/all.length : 0;
    document.getElementById('stat-regions').textContent = all.length;
    document.getElementById('stat-conf').textContent = avg?(avg*100).toFixed(1)+'%':'—';
    document.getElementById('stat-time').textContent = ms?ms+'ms':'—';
    document.getElementById('stat-pages').textContent = `${pg}/${this.pageCount}`;
  },

  _hover(i, e) {
    document.querySelectorAll('.det-item').forEach(d=>d.classList.remove('highlighted'));
    const tt = document.getElementById('box-tooltip');
    if (i===-1) { tt.classList.remove('show'); return; }
    const pageData = this.pages[this.currentPage]?.[cacheKey];
    const results = this.ocrLayout === 'original' ? (pageData?.raw_results || pageData?.results) : pageData?.results;
    const item = results?.[i];
    if (!item) return;
    document.getElementById(`det-${i}`)?.classList.add('highlighted');
    tt.innerHTML = `<strong>${esc(item.text)}</strong><br>Conf: ${item.confidence!=null?(item.confidence*100).toFixed(1)+'%':'n/a'}`;
    if (e) { tt.style.left=(e.clientX+14)+'px'; tt.style.top=(e.clientY-10)+'px'; }
    tt.classList.add('show');
  },
  _select(i) {
    document.querySelectorAll('.det-item').forEach(d=>d.classList.remove('selected'));
    const el = document.getElementById(`det-${i}`);
    if (el) { el.classList.add('selected'); el.scrollIntoView({behavior:'smooth',block:'nearest'}); }
  },

  _setZoom(z) {
    this.zoom = Math.max(.3, Math.min(4, z));
    document.getElementById('zoom-lbl').textContent = Math.round(this.zoom*100)+'%';
    this._applyTransform();
  },
  _applyTransform() {
    document.getElementById('preview-img').style.transform = `scale(${this.zoom}) rotate(${this.rotate}deg)`;
    setTimeout(()=>{this.canvas.resize();this.canvas.draw();},50);
  },
  _setLoading(on, all=false) {
    const btnRun  = document.getElementById('btn-ocr-run');
    const btnAll  = document.getElementById('btn-ocr-all');
    const btnStop = document.getElementById('btn-ocr-stop');
    btnRun.disabled = on;
    btnAll.disabled = on;
    btnRun.innerHTML = on && !all ? `<span class="spin"></span> ${t('run_ocr_running')}` : t('run_ocr');
    btnAll.innerHTML = on && all  ? `<span class="spin"></span> ${t('ocr_all_running')}` : t('ocr_all');
    // Show/hide stop button
    if (btnStop) btnStop.style.display = on ? 'inline-flex' : 'none';
    const pb = document.getElementById('progress-bar-wrap');
    pb.classList.toggle('show', on);
    document.getElementById('progress-bar').style.width = on ? '60%' : '100%';
    if (!on) setTimeout(() => pb.classList.remove('show'), 500);
  },
  _reset() {
    this._resetMode();
    this.fileId=null;this.pages={};this.zoom=1;this.rotate=0;
    document.getElementById('ocr-upload-zone').style.display = 'flex';
    document.getElementById('ocr-workspace').style.display='none';
    document.getElementById('overlay-canvas').classList.remove('interactive');
    document.getElementById('preview-img').src='';
    this._resetViewerState();
    document.getElementById('det-list').querySelectorAll('.det-item').forEach(el => el.remove());
    const empty = document.getElementById('ocr-empty-results');
    if (empty) empty.style.display='flex';
  },

  async _onRegionSelect(rect) {
    const cacheKey = this.ocrEngine + '_' + this.ocrAi;
    const pageData = this.pages[this.currentPage]?.[cacheKey];
    if (!pageData || !pageData.results) return;

    // Filter boxes whose bounding rectangle intersects the drawn selection.
    // Skip items with no geometry (box=null) — they can't be spatially hit-tested.
    const subset = pageData.results.filter(item => {
      const box = item.box;
      if (!box || !box.length) return false;  // no-geometry block — skip
      const xmin = Math.min(...box.map(pt => pt[0]));
      const ymin = Math.min(...box.map(pt => pt[1]));
      const xmax = Math.max(...box.map(pt => pt[0]));
      const ymax = Math.max(...box.map(pt => pt[1]));
      return !(xmax < rect.x1 || xmin > rect.x2 || ymax < rect.y1 || ymin > rect.y2);
    });

    if (subset.length === 0) {
      Toast.show('No text found in selected region.', 'info');
      return;
    }

    // Sort spatially: top-to-bottom, then left-to-right within the same row
    // Group into rows whose Y-centres are within ~20px of each other
    const ROW_GAP = 20;
    const withCentre = subset.map(item => {
      const box = item.box;
      const cx = (Math.min(...box.map(p => p[0])) + Math.max(...box.map(p => p[0]))) / 2;
      const cy = (Math.min(...box.map(p => p[1])) + Math.max(...box.map(p => p[1]))) / 2;
      return { ...item, cx, cy };
    }).sort((a, b) => a.cy - b.cy);

    const rows = [];
    for (const item of withCentre) {
      const lastRow = rows[rows.length - 1];
      if (lastRow && Math.abs(item.cy - lastRow[0].cy) <= ROW_GAP) {
        lastRow.push(item);
      } else {
        rows.push([item]);
      }
    }
    // Within each row sort left-to-right
    rows.forEach(row => row.sort((a, b) => a.cx - b.cx));

    const text = rows.map(row => row.map(r => r.text).join(' ')).join('\n');

    // Copy via the shared helper (secure-context Clipboard API + execCommand fallback,
    // with success/error feedback).
    await copyWithToast(text, `${subset.length} region(s) copied to clipboard`);
  },

  // Resolve a document by file_id and load it (deep-link loader; no navigation).
  async _openFromFileId(fileId) {
    if (!fileId) return;
    const find = () => (DocumentsView.docs || []).find(d => d.file_id === fileId);
    let doc = find();
    if (!doc) { try { await DocumentsView.load(); } catch (_) {} doc = find(); }
    if (!doc) { Toast.show(t('doc_not_found') || 'Document not found', 'error'); return; }
    this.loadByFileId(doc);
  },

  // Load a pre-existing file from the Documents library (skip upload). This is a
  // LOADER only — the view switch is owned by the hash router (Router._render).
  loadByFileId(doc) {
    this.fileId = doc.file_id; this.isPdf = doc.file_type === '.pdf';
    this.pageCount = doc.page_count || 1; this.currentPage = 1; this.pages = {};
    document.getElementById('ocr-upload-zone').style.display = 'none';
    document.getElementById('ocr-workspace').style.display = 'grid';
    document.getElementById('ocr-file-name').textContent = doc.filename;
    // Blank the viewer for THIS file before preview/restore, so a file with no
    // persisted OCR never shows the previously opened file's result. Also reset
    // the engine selector to default; _restoreStoredArtifact overrides it from
    // the file's own artifact when one exists.
    this._resetViewerState();
    this.ocrEngine = this._sessionEngine || 'glmocr';
    const _eng = document.getElementById('ocr-engine-select');
    if (_eng) _eng.value = this.ocrEngine;
    this._buildTabs(); this._updateNav();
    Toast.show(`${t('loaded_from_lib')} "${doc.filename}"`, 'info');
    // Preview is non-destructive (no re-OCR). After it renders, restore the
    // persisted OCR result + the engine that produced it, so the viewer shows the
    // real latest result (e.g. VietOCR) instead of a blank/re-run page.
    this._ocrPage(1, true).then(() => this._restoreStoredArtifact(doc));
  },

  // Restore persisted OCR state for a library document. Prefers the structured
  // 'ocr_layout' snapshot (overlay boxes + stats + status, no re-run); falls back
  // to text + engine only for older documents that predate the snapshot.
  async _restoreStoredArtifact(doc) {
    if (!doc || doc.id == null) return;
    const applyEngine = (eng) => {
      // Restore the engine a saved doc was processed with. paddleocr_modern is now
      // hidden from the selector but still valid internally — keep it as the active
      // engine, but only reflect it in the dropdown when a matching option exists
      // (so a restored Modern doc doesn't blank out the 3-option selector).
      if (['paddleocr', 'vietocr', 'paddleocr_modern', 'glmocr', 'glm_vietocr'].includes(eng)) {
        this.ocrEngine = eng;
        const sel = document.getElementById('ocr-engine-select');
        if (sel && [...sel.options].some(o => o.value === eng)) sel.value = eng;
      }
    };
    try {
      const a = await API.getDocText(doc.id);
      if (!a || !a.success || !a.artifacts) return;
      const arts = a.artifacts;

      // ── Full structured restore ─────────────────────────────────────────
      if (arts.ocr_layout && arts.ocr_layout.content) {
        let layout = null;
        try { layout = JSON.parse(arts.ocr_layout.content); } catch (_) {}
        if (layout && Array.isArray(layout.pages) && layout.pages.length) {
          this.ocrAi = false;
          if (layout.engine) applyEngine(String(layout.engine).toLowerCase());
          const cacheKey = this.ocrEngine + '_' + this.ocrAi;
          layout.pages.forEach(pg => {
            const data = {
              results:          pg.results || [],
              raw_results:      pg.results || [],   // keep Original/Enhanced toggle working
              img_width:        pg.img_width,
              img_height:       pg.img_height,
              elapsed_ms:       pg.elapsed_ms,
              inference_status: pg.inference_status,
              page_num:         pg.page_num,
            };
            this.pages[pg.page_num] ||= {};
            this.pages[pg.page_num][cacheKey] = data;
          });
          // Draw the current page's overlay onto the already-loaded preview image.
          const cur = this.pages[this.currentPage] && this.pages[this.currentPage][cacheKey];
          if (cur) {
            const results = this.ocrLayout === 'original' ? (cur.raw_results || cur.results) : cur.results;
            if (cur.img_width && cur.img_height) this.canvas.load(results, cur.img_width, cur.img_height);
            this._applyTransform();
            this._renderResults(cur);
            this._updateStats(cur);
            // Rehydrate the result tabs (markdown/json/images) from persisted artifacts.
            if (arts.ocr_markdown && arts.ocr_markdown.content) cur.markdown = arts.ocr_markdown.content;
            if (arts.ocr_json && arts.ocr_json.content) {
              try { cur.raw_json = JSON.parse(arts.ocr_json.content); } catch (_) {}
            }
            this._curDocId = doc.id;
            this._renderStructured(cur);
            this._loadImagesForDoc(doc.id);   // enable Images tab if artifacts exist
          }
          this._renderTextAll();
          this._setOcrStatusBadge(doc, layout);
          // Reflect the actual restored artifact (sum of regions across pages).
          const regions = layout.pages.reduce((n, pg) => n + ((pg.results || []).length), 0);
          Toast.show(`${t('nav_ocr')}: ${regions} ${t('regions_found')}`, 'success');
          return;
        }
      }

      // ── Fallback: text (+ optional markdown) only ───────────────────────
      const art = arts.ocr || arts.text;
      if (!art || !art.content) return;
      this._curDocId = doc.id;
      const data = { results: String(art.content).split('\n').map(text => ({ text })) };
      if (arts.ocr_markdown && arts.ocr_markdown.content) data.markdown = arts.ocr_markdown.content;
      if (arts.ocr_json && arts.ocr_json.content) {
        try { data.raw_json = JSON.parse(arts.ocr_json.content); } catch (_) {}
      }
      this._renderStructured(data);
      this._loadImagesForDoc(doc.id);   // enable Images tab if artifacts exist
      State.setOcrText(art.content);
      const m = /engine=([a-z0-9_]+)/i.exec(art.meta || '');
      if (m) applyEngine(m[1].toLowerCase());
      this._setOcrStatusBadge(doc, null);
    } catch (e) { /* leave preview as-is */ }
  },

  // Show an OCR-status badge next to the filename from Document.status / layout.
  _setOcrStatusBadge(doc, layout) {
    const el = document.getElementById('ocr-status-badge');
    if (!el) return;
    const status = (doc && doc.status) || '';
    let txt = '';
    if (status === 'ocr_done' || (layout && layout.pages)) {
      const eng = (layout && layout.engine) || this.ocrEngine || '';
      txt = '✓ OCR' + (eng ? ' · ' + eng : '');
      const inf = layout && layout.pages && layout.pages[0] && layout.pages[0].inference_status;
      if (inf && inf !== 'ok') txt += ' · ' + inf;
    }
    el.textContent = txt;
    el.style.display = txt ? '' : 'none';
  }
};

// ── Utilities ──────────────────────────────────────────
function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function fmtSize(b) {
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b/1024).toFixed(1) + ' KB';
  return (b/1048576).toFixed(1) + ' MB';
}
// Server timestamps are UTC (ISO now carries a +00:00/Z marker). Render them in a
// fixed Vietnam timezone so the display is correct regardless of the viewer's machine.
const DISPLAY_TZ = 'Asia/Ho_Chi_Minh';
function fmtDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d)) return '';
  return new Intl.DateTimeFormat('vi-VN', {
    timeZone: DISPLAY_TZ,
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', hour12: false,
  }).format(d);
}

// ══════════════════════════════════════════════════════
// Documents View
// ══════════════════════════════════════════════════════
const DocumentsView = {
  docs: [],
  isAdmin: false,
  filter: 'all',
  page: 1,
  pageSize: 20,
  totalPages: 1,
  totalItems: 0,
  stats: { total:0, images:0, pdfs:0, texts:0 },

  init() {
    document.getElementById('docs-refresh').addEventListener('click', () => { this.page = 1; this.load(); });
    document.querySelectorAll('.filter-pill').forEach(p =>
      p.addEventListener('click', () => {
        document.querySelectorAll('.filter-pill').forEach(x => x.classList.remove('active'));
        p.classList.add('active'); this.filter = p.dataset.filter;
        this.page = 1; this.load();
      }));
    
    let searchTimer;
    document.getElementById('docs-search').addEventListener('input', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => { this.page = 1; this.load(); }, 300);
    });

    document.getElementById('pagin-prev').addEventListener('click', () => {
      if (this.page > 1) { this.page--; this.load(); }
    });
    document.getElementById('pagin-next').addEventListener('click', () => {
      if (this.page < this.totalPages) { this.page++; this.load(); }
    });
    document.getElementById('pagin-size-select').addEventListener('change', (e) => {
      this.pageSize = parseInt(e.target.value);
      this.page = 1;
      this.load();
    });
  },

  show() { this.load(); },

  async load() {
    const tbl = document.getElementById('docs-table');
    const empty = document.getElementById('docs-empty');
    const loading = document.getElementById('docs-loading');
    const pagin = document.getElementById('docs-pagination');
    const q = (document.getElementById('docs-search')?.value||'').toLowerCase();
    
    loading.style.display='flex'; tbl.style.display='none'; empty.style.display='none'; pagin.style.display='none';
    
    try {
      const url = `/api/documents?page=${this.page}&page_size=${this.pageSize}&filter=${this.filter}&search=${encodeURIComponent(q)}`;
      const r = await fetch(url);
      const data = await r.json();
      if (!data.success) { Toast.show(t('toast_load_fail'), 'error'); return; }
      
      this.docs = data.documents; 
      this.isAdmin = data.is_admin;
      this.stats = data.stats || this.stats;
      
      if (data.pagination) {
          this.totalItems = data.pagination.total_items;
          this.totalPages = data.pagination.total_pages;
          this.page = data.pagination.current_page;
      }

      document.getElementById('docs-owner-col').style.display = this.isAdmin ? '' : 'none';
      this._renderStats(); 
      this._render();
      this._renderPagination();
    } finally { 
      loading.style.display='none'; 
    }
  },

  _renderStats() {
    document.getElementById('docs-stats').innerHTML =
      `<div class="ds-chip"><strong>${this.stats.total}</strong> ${t('docs_stat_total')}</div>
       <div class="ds-chip"><strong>${this.stats.images}</strong> ${t('docs_stat_images')}</div>
       <div class="ds-chip"><strong>${this.stats.pdfs}</strong> ${t('docs_stat_pdfs')}</div>
       <div class="ds-chip"><strong>${this.stats.texts}</strong> ${t('docs_stat_texts')}</div>`;
  },

  _render() {
    const tbody = document.getElementById('docs-tbody');
    const tbl   = document.getElementById('docs-table');
    const empty = document.getElementById('docs-empty');
    tbody.innerHTML = '';
    if (!this.docs.length) { tbl.style.display='none'; empty.style.display='flex'; return; }
    tbl.style.display=''; empty.style.display='none';
    
    const IMG = ['.jpg','.jpeg','.png','.webp'];
    const isOcr  = d => IMG.includes(d.file_type) || d.file_type==='.pdf';

    this.docs.forEach((doc, i) => {
      const ext = doc.file_type;
      const stt = (this.page - 1) * this.pageSize + i + 1;
      const iconCls = IMG.includes(ext)?'doc-icon-img':ext==='.pdf'?'doc-icon-pdf':'doc-icon-txt';
      const icon = IMG.includes(ext)?'🖼️':ext==='.pdf'?'📜':'📄';
      const sc = 'status-'+(doc.status||'uploaded');
      const ownerTd = this.isAdmin ? `<td class="owner-cell">${esc(doc.owner||'')}</td>` : '';
      const ocrBtn = isOcr(doc)
        ? `<button class="btn-icon" data-i18n-title="docs_tip_ocr" title="${t('docs_tip_ocr')}" onclick="DocumentsView._sendOCR(${doc.id})">🔍</button>` : '';
      // "Already processed" badge from persisted artifacts (OCR/extracted text present).
      const _kinds = doc.artifact_kinds || [];
      const _hasText = _kinds.includes('ocr') || _kinds.includes('text');
      const _pb = (on, label) => on
        ? `<span class="proc-badge" style="display:inline-block;margin-left:4px;padding:1px 6px;border-radius:8px;background:rgba(60,120,220,.12);color:#2c5fd4;font-size:10px;font-weight:700;vertical-align:middle">${label}</span>`
        : '';
      const procBadges = _pb(_hasText, t('badge_text'));
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="td-muted" style="text-align:center;font-size:12px">${stt}</td>
        <td><div class="doc-file-cell">
          <div class="doc-icon ${iconCls}">${icon}</div>
          <div><div class="doc-name" title="${esc(doc.filename)}">${esc(doc.filename)}</div>
               <div class="doc-size">${fmtSize(doc.file_size)}</div></div>
        </div></td>
        <td><span class="type-badge">${esc(ext)}</span></td>
        <td class="doc-size">${fmtSize(doc.file_size)}</td>
        ${ownerTd}
        <td class="date-cell">${fmtDate(doc.upload_date)}</td>
        <td><span class="doc-status ${sc}">${esc(doc.status)}</span>${procBadges}</td>
        <td><div class="doc-actions">
          ${ocrBtn}
          <a class="btn-icon" title="${t('docs_tip_download')}" href="/api/documents/${doc.id}/download">⬇️</a>
          <button class="btn-icon" title="${t('docs_tip_delete')}" style="color:var(--danger)" onclick="DocumentsView._delete(${doc.id}, this)">🗑️</button>
        </div></td>`;
      tbody.appendChild(tr);
    });
  },

  _renderPagination() {
    const pagin = document.getElementById('docs-pagination');
    if (this.totalItems === 0) { pagin.style.display = 'none'; return; }
    pagin.style.display = 'flex';
    
    document.getElementById('pagin-total').textContent = this.totalItems;
    const start = (this.page - 1) * this.pageSize + 1;
    const end = Math.min(this.page * this.pageSize, this.totalItems);
    document.getElementById('pagin-range').textContent = `${start}–${end}`;
    
    document.getElementById('pagin-prev').disabled = (this.page <= 1);
    document.getElementById('pagin-next').disabled = (this.page >= this.totalPages);
    
    const pagesDiv = document.getElementById('pagin-pages');
    pagesDiv.innerHTML = '';
    
    // Simple pagination: show current, first, last, and neighbors
    let range = [];
    for (let i = 1; i <= this.totalPages; i++) {
      if (i === 1 || i === this.totalPages || (i >= this.page - 1 && i <= this.page + 1)) {
        range.push(i);
      }
    }
    
    let last = 0;
    for (let i of range) {
      if (last && i - last > 1) {
        const dots = document.createElement('span');
        dots.className = 'pagin-dots';
        dots.textContent = '...';
        pagesDiv.appendChild(dots);
      }
      const btn = document.createElement('button');
      btn.className = 'pagin-btn' + (i === this.page ? ' active' : '');
      btn.textContent = i;
      btn.addEventListener('click', () => {
        this.page = i;
        this.load();
      });
      pagesDiv.appendChild(btn);
      last = i;
    }
  },

  _docById(id) { return this.docs.find(d => d.id === id); },

  _sendOCR(id) {
    const doc = this._docById(id); if (!doc) return;
    Router.goto('ocr', doc.file_id);   // deep link → Router loads + restores
  },

  async _delete(id, btn) {
    if (!confirm(t('docs_delete_confirm'))) return;
    btn.disabled = true;
    const r = await fetch(`/api/documents/${id}`, { method:'DELETE' });
    const data = await r.json();
    if (data.success) {
      Toast.show(t('toast_delete_success'), 'success');
      this.load();
    } else {
      Toast.show(t('toast_delete_fail') + data.error, 'error');
      btn.disabled = false;
    }
  }
};


// ── Boot ───────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  // Init i18n first
  I18n.init();

  // Router: also call show() when navigating to documents
  const _origGoto = Router.goto.bind(Router);
  Router.goto = function(name, ...rest) {
    _origGoto(name, ...rest);   // forward the deep-link arg (e.g. file_id) — dropping it
                                // here was breaking Documents → OCR restore
    if (name === 'documents') DocumentsView.show();
    if (name === 'ocr') OCRView._resetMode();
  };

  // Register views
  ['home','ocr','documents'].forEach(name =>
    Router.register(name, document.getElementById(`view-${name}`)));

  // Nav links
  document.querySelectorAll('.nav-link').forEach(l =>
    l.addEventListener('click', () => Router.goto(l.dataset.view)));

  // In-app back (OCR viewer → wherever the user came from)
  const ocrBackBtn = document.getElementById('ocr-back-btn');
  if (ocrBackBtn) ocrBackBtn.addEventListener('click', () => Router.back());

  // Home cards: SPA views navigate via the router…
  document.querySelectorAll('[data-goto]').forEach(el =>
    el.addEventListener('click', () => Router.goto(el.dataset.goto)));
  // …separate-page modules (Admin /admin/) navigate for real.
  document.querySelectorAll('[data-href]').forEach(el =>
    el.addEventListener('click', () => { window.location.href = el.dataset.href; }));

  // Init views
  OCRView.init();
  DocumentsView.init();

  // Render the initial view from the URL hash (defaults to home), and wire
  // browser Back/Forward via hashchange.
  Router.init();
});

