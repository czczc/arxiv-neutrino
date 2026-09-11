import { reactive, readonly, watch } from 'vue';

// Per-visitor state. There is no login: stars and read marks live in this
// browser only. One versioned key so the shape can evolve.
const KEY = 'arxivnu:v1';
const EMPTY = () => ({ version: 1, stars: {}, read: {}, deleted: {}, readBefore: null, bannerDismissed: false });

function load() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return { state: EMPTY(), fresh: true };
    const parsed = JSON.parse(raw);
    return { state: { ...EMPTY(), ...parsed }, fresh: false };
  } catch {
    return { state: EMPTY(), fresh: true };
  }
}

function save(state) {
  try { localStorage.setItem(KEY, JSON.stringify(state)); } catch { /* private mode etc. */ }
}

const { state: initial, fresh } = load();
const state = reactive(initial);
const meta = reactive({ firstVisit: fresh });

watch(state, () => save(state), { deep: true });

// Another tab changed it: adopt without re-saving.
window.addEventListener('storage', (e) => {
  if (e.key !== KEY || !e.newValue) return;
  try { Object.assign(state, { ...EMPTY(), ...JSON.parse(e.newValue) }); } catch { /* ignore */ }
});

const now = () => new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');

export function useLocalState() {
  const isStarred = (id) => !!state.stars[id];
  const isDeleted = (id) => !!state.deleted[id];
  const isRead = (p) =>
    !!state.read[p.arxiv_id] || (!!state.readBefore && !!p.submitted_date && p.submitted_date < state.readBefore);

  function toggleStar(id) {
    if (state.stars[id]) delete state.stars[id];
    else state.stars[id] = now();
  }
  function toggleDelete(id) {
    if (state.deleted[id]) delete state.deleted[id];
    else state.deleted[id] = now();
  }
  function markRead(ids) {
    const t = now();
    for (const id of ids) state.read[id] = t;
  }
  function toggleRead(p) {
    if (isRead(p)) {
      delete state.read[p.arxiv_id];
      // Papers hidden by the baseline can't be "un-read" individually
      // without moving the baseline; record an explicit unread marker.
      if (state.readBefore && p.submitted_date < state.readBefore) state.read[p.arxiv_id] = false;
    } else {
      state.read[p.arxiv_id] = now();
    }
  }
  function setReadBefore(iso) { state.readBefore = iso; }
  function dismissBanner() { state.bannerDismissed = true; }

  function exportJson() {
    const { bannerDismissed, ...rest } = state;
    return JSON.stringify(rest, null, 2);
  }
  // Merge: imported marks are added to (not replacing) what this browser has.
  function importJson(text) {
    const incoming = JSON.parse(text);
    if (!incoming || typeof incoming !== 'object') throw new Error('not an object');
    Object.assign(state.stars, incoming.stars || {});
    Object.assign(state.read, incoming.read || {});
    Object.assign(state.deleted, incoming.deleted || {});
    if (incoming.readBefore && (!state.readBefore || incoming.readBefore > state.readBefore)) {
      state.readBefore = incoming.readBefore;
    }
    return { stars: Object.keys(incoming.stars || {}).length, read: Object.keys(incoming.read || {}).length };
  }

  return {
    state: readonly(state), meta, isStarred, isRead, isDeleted, toggleStar, toggleRead, toggleDelete, markRead,
    setReadBefore, dismissBanner, exportJson, importJson,
    starredIds: () => Object.keys(state.stars),
    deletedIds: () => Object.keys(state.deleted),
  };
}
