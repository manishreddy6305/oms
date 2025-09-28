// Content script: Extract visible logs from OpenSearch Dashboards Discover/log views.
// This relies on typical DOM structure where each log line / document row appears within a table or list.
// Because OpenSearch UI can change, we provide multiple selectors & a fallback text capture.

function extractVisibleLogs() {
  const candidates = [];

  // Common selectors for Discover table rows
  const rowSelectors = [
    'tr.osdDocTable__row', // older versions
    'tr.discoverTableRow',
    'div.discover-table-row',
    'div.euiDataGridRow',
    'div.euiDataGridRow .euiText',
    'div.euiDataGridRow div[role="row"]'
  ];

  const seen = new Set();
  rowSelectors.forEach(sel => {
    document.querySelectorAll(sel).forEach(el => {
      const text = el.innerText.trim();
      if (text && !seen.has(text)) {
        candidates.push(text);
        seen.add(text);
      }
    });
  });

  // Fallback: capture any monospaced blocks (often log messages)
  if (candidates.length === 0) {
    document.querySelectorAll('code, pre').forEach(el => {
      const text = el.innerText.trim();
      if (text && !seen.has(text)) {
        candidates.push(text);
        seen.add(text);
      }
    });
  }

  return candidates;
}

function parseValue(raw) {
  const t = raw.trim();
  if (!t) return '';
  // Try JSON
  if ((t.startsWith('{') && t.endsWith('}')) || (t.startsWith('[') && t.endsWith(']'))) {
    try { return JSON.parse(t); } catch (_) {}
  }
  // Try primitive types
  if (t === 'true') return true;
  if (t === 'false') return false;
  if (t === 'null') return null;
  if (!isNaN(Number(t)) && isFinite(Number(t))) return Number(t);
  return t;
}

function ensureStringValues(doc) {
  const out = {};
  Object.keys(doc).forEach(k => {
    const v = doc[k];
    if (v === undefined) return;
    if (v === null) {
      out[k] = 'null';
    } else if (typeof v === 'object') {
      try { out[k] = JSON.stringify(v); } catch (_) { out[k] = String(v); }
    } else {
      out[k] = String(v);
    }
  });
  return out;
}

function extractDocsFromTables() {
  const tables = document.querySelectorAll('.osdDocViewerTable');
  const docs = [];
  tables.forEach(table => {
    const doc = {};
    const rows = table.querySelectorAll('tr[data-test-subj^="tableDocViewRow-"]');
    rows.forEach(tr => {
      const dataAttr = tr.getAttribute('data-test-subj');
      let fieldName = dataAttr ? dataAttr.replace('tableDocViewRow-', '') : undefined;
      // Field name may also be inside the field cell.
      if (!fieldName) {
        const nameSpan = tr.querySelector('.osdDocViewer__field span.eui-textTruncate span');
        if (nameSpan) fieldName = nameSpan.textContent.trim();
      }
      if (!fieldName) return;
      const valEl = tr.querySelector('.osdDocViewer__value');
      if (!valEl) return;
      const rawVal = valEl.innerText || valEl.textContent || '';
      doc[fieldName] = parseValue(rawVal);
    });
    // Only push non-empty docs
    if (Object.keys(doc).length) {
      if (doc._source && typeof doc._source === 'object') {
        docs.push(ensureStringValues(doc._source));
      } else {
        docs.push(ensureStringValues(doc));
      }
    }
  });
  return docs;
}

function extractJsonDocs() {
  const docs = [];
  const blocks = document.querySelectorAll('.osdDocViewer code.json, .osdDocViewer pre code');
  blocks.forEach(code => {
    const txt = code.innerText.trim();
    if (!txt.startsWith('{')) return;
    try {
      const obj = JSON.parse(txt);
      if (obj && typeof obj === 'object' && obj._source && typeof obj._source === 'object') {
        docs.push(ensureStringValues(obj._source));
      } else {
        docs.push(ensureStringValues(obj));
      }
    } catch (_) { /* ignore parse errors */ }
  });
  return docs;
}

function buildDocumentsFromLogs(logLines) {
  return logLines.map(line => {
    let parsed;
    try { parsed = JSON.parse(line); } catch (_) {}
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      if (!parsed.timestamp) parsed.timestamp = new Date().toISOString();
      parsed.source = parsed.source || 'opensearch-ui-visible';
      parsed.url = parsed.url || location.href;
      return ensureStringValues(parsed);
    }
    return ensureStringValues({
      timestamp: new Date().toISOString(),
      message: line,
      source: 'opensearch-ui-visible',
      url: location.href
    });
  });
}

function collectDocuments() {
  const tableDocs = extractDocsFromTables();
  if (tableDocs.length) return tableDocs;
  const jsonDocs = extractJsonDocs();
  if (jsonDocs.length) return jsonDocs;
  const lines = extractVisibleLogs();
  return buildDocumentsFromLogs(lines);
}

function clickRowDetailToggles() {
  let count = 0;
  document.querySelectorAll('button[aria-label="Toggle row details"][aria-expanded="false"]').forEach(btn => {
    try { btn.click(); count++; } catch (_) {}
  });
  return count;
}

// Listen for requests from popup/background
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg && msg.type === 'COLLECT_VISIBLE_LOGS') {
    try {
      const clicked = clickRowDetailToggles();
      if (clicked > 0) {
        // Allow DOM to render expanded rows
        setTimeout(() => {
          try {
            const docs = collectDocuments();
            sendResponse({ ok: true, docs, count: docs.length, expanded: true });
          } catch (e) {
            sendResponse({ ok: false, error: e.message });
          }
        }, 300);
        return true; // keep channel open for async response
      }
      const docs = collectDocuments();
      sendResponse({ ok: true, docs, count: docs.length, expanded: false });
    } catch (e) {
      sendResponse({ ok: false, error: e.message });
    }
    return true; // async response
  }
});
