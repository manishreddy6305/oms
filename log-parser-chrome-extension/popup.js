const statusEl = document.getElementById('status');
const previewEl = document.getElementById('preview');
const btn = document.getElementById('captureBtn');
const indexInput = document.getElementById('indexInput');

const bulkBtn = document.createElement('button');
bulkBtn.textContent = 'Capture & Download Bulk';
btn.insertAdjacentElement('afterend', bulkBtn);

async function ensureContentScript(tabId) {
  try {
    await chrome.scripting.executeScript({
      target: { tabId },
      files: ['contentScript.js']
    });
  } catch (e) {
    console.warn('Injection failed', e);
  }
}

async function captureAndSave() {
  statusEl.textContent = 'Collecting visible logs...';
  previewEl.textContent = '';

  try {
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.id) {
      statusEl.textContent = 'No active tab';
      return;
    }

    let response;
    try {
      // Ask content script to collect logs
      response = await chrome.tabs.sendMessage(tab.id, { type: 'COLLECT_VISIBLE_LOGS' });
    } catch (e) {
      // Likely no content script; try injecting then retry once
      await ensureContentScript(tab.id);
      try {
        response = await chrome.tabs.sendMessage(tab.id, { type: 'COLLECT_VISIBLE_LOGS' });
      } catch (inner) {
        statusEl.textContent = 'Content script not available on this page.';
        return;
      }
    }

    if (!response || !response.ok) {
      statusEl.textContent = 'Failed to collect logs: ' + (response && response.error);
      return;
    }

    const { docs, count } = response;
    if (count === 0) {
      statusEl.textContent = 'No visible logs found.';
      return;
    }

    const targetIndex = (indexInput && indexInput.value.trim()) || 'logs-service';
    statusEl.textContent = `Indexing ${count} documents into ${targetIndex}...`;
    previewEl.textContent = JSON.stringify(docs.slice(0, 5), null, 2) + (count > 5 ? `\n... (${count - 5} more)` : '');

    const indexResp = await chrome.runtime.sendMessage({ type: 'INDEX_LOG_DOCUMENTS', docs, index: targetIndex });
    if (!indexResp.ok) {
      statusEl.textContent = 'Index error: ' + indexResp.error;
      return;
    }

    const successCount = indexResp.results.filter(r => r.ok).length;
    statusEl.textContent = `Done. Success: ${successCount}/${count}`;
  } catch (e) {
    statusEl.textContent = 'Error: ' + e.message;
  }
}

function buildBulkNDJSON(docs, indexName) {
  indexName = indexName || (indexInput && indexInput.value.trim()) || 'logs-service';

  const stripUnderscoreKeys = (obj) => {
    return Object.fromEntries(
      Object.entries(obj).filter(([key]) => !key.startsWith('_'))
    );
  };

  const normalizeDoc = (doc) => {
    let filtered = stripUnderscoreKeys(doc);

    if (filtered.timestamp) {
      // Parse "Sep 11, 2025 @ 15:26:30.528"
      const parsedDate = new Date(filtered.timestamp.replace('@', '').trim());
      if (!isNaN(parsedDate)) {
        filtered.timestamp = parsedDate.toISOString();
      }
    }

    return filtered;
  };

  return docs
    .map(d => {
      const normalizedDoc = normalizeDoc(d);
      return (
        JSON.stringify({ index: { _index: indexName } }) +
        '\n' +
        JSON.stringify(normalizedDoc)
      );
    })
    .join('\n') + '\n';
}

async function captureAndDownloadBulk() {
  statusEl.textContent = 'Collecting visible logs...';
  previewEl.textContent = '';
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.id) { statusEl.textContent = 'No active tab'; return; }

    let response;
    try { response = await chrome.tabs.sendMessage(tab.id, { type: 'COLLECT_VISIBLE_LOGS' }); }
    catch { await ensureContentScript(tab.id); response = await chrome.tabs.sendMessage(tab.id, { type: 'COLLECT_VISIBLE_LOGS' }); }

    if (!response || !response.ok) { statusEl.textContent = 'Collect failed'; return; }
    const { docs, count } = response;
    if (!count) { statusEl.textContent = 'No logs'; return; }

    const targetIndex = (indexInput && indexInput.value.trim()) || 'logs-service';
    const ndjson = buildBulkNDJSON(docs, targetIndex);
    const blob = new Blob([ndjson], { type: 'application/x-ndjson' });
    const url = URL.createObjectURL(blob);
    const filename = 'bulk_logs_' + Date.now() + '.ndjson';
    chrome.downloads.download({ url, filename, saveAs: true });
    previewEl.textContent = ndjson.split('\n').slice(0, 10).join('\n');
    statusEl.textContent = `Bulk file ready (${count} docs).`;
  } catch (e) {
    statusEl.textContent = 'Error: ' + e.message;
  }
}

btn.addEventListener('click', captureAndSave);
bulkBtn.addEventListener('click', captureAndDownloadBulk);
