import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

// Filters live in the URL query so views are shareable: ?tags=a,b&collab=X&q=..&date=YYYY-MM-DD
export function useFilters() {
  const route = useRoute();
  const router = useRouter();

  const tags = computed(() => String(route.query.tags || '').split(',').filter(Boolean));
  const collab = computed(() => String(route.query.collab || ''));
  const q = computed(() => String(route.query.q || ''));
  const date = computed(() => String(route.query.date || ''));
  const active = computed(() => tags.value.length > 0 || !!collab.value || !!q.value || !!date.value);

  function push(patch, method = 'push') {
    const query = { ...route.query, ...patch };
    for (const k of Object.keys(query)) if (!query[k]) delete query[k];
    delete query.paper; // selection resets when filters change
    router[method]({ path: route.path, query });
  }
  const toggleTag = (t) => {
    const next = tags.value.includes(t) ? tags.value.filter((x) => x !== t) : [...tags.value, t];
    push({ tags: next.join(',') });
  };
  const setCollab = (c) => push({ collab: collab.value === c ? '' : c });
  const setQuery = (s) => push({ q: s }, 'replace'); // typed live; don't spam history
  const setDate = (d) => push({ date: d });
  const clear = () => push({ tags: '', collab: '', q: '', date: '' });

  // Params for /api/papers
  const apiParams = computed(() => ({
    tags: tags.value.join(','), collab: collab.value, q: q.value, date: date.value,
  }));

  return { tags, collab, q, date, active, toggleTag, setCollab, setQuery, setDate, clear, apiParams };
}
