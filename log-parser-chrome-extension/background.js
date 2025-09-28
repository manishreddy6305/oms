// Background service worker: receives docs and sends them to local OpenSearch/Elasticsearch.

async function postDocument(doc, index) {
  const idx = index || 'service-logs';
  const url = `https://localhost:9200/${idx}/_doc`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Basic ZWxhc3RpYzpVT0dad0p0bUMxaWthKl9keFYrMw=='
    },
    body: JSON.stringify(doc)
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error('Failed to index doc: ' + res.status + ' ' + text);
  }
  return res.json();
}

async function bulkIndex(docs, index) {
  const results = [];
  for (const d of docs) {
    try {
      const r = await postDocument(d, index);
      results.push({ ok: true, id: r._id });
    } catch (e) {
      results.push({ ok: false, error: e.message });
    }
  }
  return results;
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg && msg.type === 'INDEX_LOG_DOCUMENTS') {
    bulkIndex(msg.docs, msg.index).then(results => {
      sendResponse({ ok: true, results });
    }).catch(err => {
      sendResponse({ ok: false, error: err.message });
    });
    return true; // keep message channel open
  } else if (msg && msg.type === 'RAW_LOG_DOCUMENTS') {
    sendResponse({ ok: true, results: msg.docs });
    return true; // keep message channel open
  }
});
