// Vite injects BASE_URL from `base` in vite.config.js: '/' locally,
// '/<prefix>/' when built with VITE_BASE. Strip the trailing slash so it
// concatenates with paths that start with '/'.
const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');

async function getJson(path, params = {}) {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') qs.set(k, v);
  }
  const url = BASE + path + (qs.size ? `?${qs}` : '');
  const resp = await fetch(url);
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    const err = new Error(body.detail || `HTTP ${resp.status}`);
    err.status = resp.status;
    throw err;
  }
  return resp.json();
}

export const fetchPapers = (params) => getJson('/api/papers', params);
export const fetchPaper = (id) => getJson(`/api/papers/${encodeURIComponent(id)}`);
export const fetchFacets = () => getJson('/api/facets');
export const fetchDates = () => getJson('/api/dates');

export const arxivUrl = (id) => `https://arxiv.org/abs/${id}`;
export const inspireUrl = (id) => `https://inspirehep.net/search?p=arxiv:${id}`;
