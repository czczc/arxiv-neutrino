<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import TopBar from '../components/TopBar.vue';
import NavPane from '../components/NavPane.vue';
import FilterChips from '../components/FilterChips.vue';
import PaperList from '../components/PaperList.vue';
import ReaderPane from '../components/ReaderPane.vue';
import BottomTabs from '../components/BottomTabs.vue';
import FirstVisitBanner from '../components/FirstVisitBanner.vue';
import Drawer from '../components/Drawer.vue';
import { arxivUrl, fetchPapers } from '../api.js';
import { useFilters } from '../composables/useFilters.js';
import { useLocalState } from '../composables/useLocalState.js';
import { useMedia } from '../composables/useMedia.js';
import { useFacets } from '../composables/useFacets.js';
import { useQueue } from '../composables/useQueue.js';

const props = defineProps({ mode: { type: String, default: 'unread' } });
const route = useRoute();
const router = useRouter();
const { apiParams, active } = useFilters();
const ls = useLocalState();
const { isPhone, isWide } = useMedia();
const { facets } = useFacets();
const queue = useQueue();

const PAGE = 100;
const papers = ref([]);
const nextBefore = ref(null);
const exhausted = ref(false);
const loading = ref(false);
const drawer = ref(false);
const topbar = ref(null);
const selectedId = computed(() => String(route.query.paper || ''));

const titles = { unread: 'Unread', starred: 'Starred', all: 'All papers' };
const visible = computed(() => props.mode === 'unread'
  ? papers.value.filter((p) => !ls.isRead(p) || p.arxiv_id === selectedId.value)
  : papers.value);
const unreadLoaded = computed(() => papers.value.filter((p) => !ls.isRead(p)).length);
const hasMore = computed(() => !exhausted.value);

async function loadPage(reset = false) {
  if (loading.value) return;
  loading.value = true;
  try {
    if (reset) { papers.value = []; nextBefore.value = null; exhausted.value = false; }
    if (props.mode === 'starred') {
      const ids = ls.starredIds();
      const out = [];
      for (let i = 0; i < ids.length; i += 150) {
        const r = await fetchPapers({ ...apiParams.value, ids: ids.slice(i, i + 150).join(',') });
        out.push(...r.papers);
      }
      out.sort((a, b) => (b.submitted_date || '').localeCompare(a.submitted_date || ''));
      papers.value = out;
      exhausted.value = true;
    } else {
      const r = await fetchPapers({ ...apiParams.value, before: nextBefore.value, limit: PAGE });
      papers.value = reset ? r.papers : [...papers.value, ...r.papers];
      nextBefore.value = r.next_before;
      exhausted.value = !r.next_before;
    }
  } finally {
    loading.value = false;
  }
}

// In Unread mode keep pulling older pages until enough unread rows are on screen.
watch([visible, loading, exhausted], () => {
  if (props.mode === 'unread' && !loading.value && !exhausted.value && visible.value.length < 15) loadPage();
});
watch([() => props.mode, apiParams], () => loadPage(true), { immediate: true, deep: true });

function select(p) {
  if (isPhone.value) {
    queue.set(visible.value.map((x) => x.arxiv_id));
    router.push({ path: `/paper/${p.arxiv_id}` });
  } else {
    router.replace({ path: route.path, query: { ...route.query, paper: p.arxiv_id } });
  }
}
function markAll() { ls.markRead(visible.value.map((p) => p.arxiv_id)); }
function markDay(ps) { ls.markRead(ps.map((p) => p.arxiv_id)); }

// Keyboard (desktop): j/k move, s star, e read, o open arXiv, / search.
function onKey(e) {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const tag = e.target?.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA') { if (e.key === 'Escape') e.target.blur(); return; }
  const list = visible.value;
  const idx = list.findIndex((p) => p.arxiv_id === selectedId.value);
  const cur = idx >= 0 ? list[idx] : null;
  switch (e.key) {
    case 'j': case 'ArrowDown': if (list.length) select(list[Math.min(idx + 1, list.length - 1)]); e.preventDefault(); break;
    case 'k': case 'ArrowUp': if (list.length) select(list[Math.max(idx - 1, 0)]); e.preventDefault(); break;
    case 's': if (cur) ls.toggleStar(cur.arxiv_id); break;
    case 'e': if (cur) { if (props.mode === 'unread') { ls.markRead([cur.arxiv_id]); if (list[idx + 1]) select(list[idx + 1]); } else ls.toggleRead(cur); } break;
    case 'o': if (cur) { ls.markRead([cur.arxiv_id]); window.open(arxivUrl(cur.arxiv_id), '_blank', 'noopener'); } break;
    case '/': topbar.value?.focusSearch(); e.preventDefault(); break;
  }
}
onMounted(() => window.addEventListener('keydown', onKey));
onUnmounted(() => window.removeEventListener('keydown', onKey));

const emptyText = computed(() =>
  props.mode === 'unread' ? (active.value ? 'No unread papers match these filters.' : 'All caught up.')
  : props.mode === 'starred' ? 'No starred papers yet. Tap the star on a row (or press s).'
  : 'No papers match.');
</script>

<template>
  <div class="shell">
    <TopBar ref="topbar" :title="titles[mode]" :count="visible.length" :is-phone="isPhone" :menu="!isWide" @menu="drawer = true" @mark-all="markAll" />
    <FirstVisitBanner v-if="mode === 'unread'" :total="facets.total" />
    <FilterChips @add="drawer = true" />
    <div class="panes">
      <NavPane v-if="isWide" :unread-count="unreadLoaded" />
      <div class="listcol" :class="{ solo: isPhone }">
        <PaperList :papers="visible" :selected-id="selectedId" :loading="loading" :has-more="hasMore" :swipe="isPhone"
                   :empty-text="emptyText" @select="select" @load-more="loadPage()" @mark-day="markDay" />
      </div>
      <ReaderPane v-if="!isPhone" :paper-id="selectedId" />
    </div>
    <BottomTabs v-if="isPhone" :unread-count="unreadLoaded" />
    <Drawer :open="drawer" @close="drawer = false">
      <NavPane :unread-count="unreadLoaded" :show-folders="isPhone" @navigate="drawer = false" />
    </Drawer>
  </div>
</template>

<style scoped>
.shell { height: 100%; display: flex; flex-direction: column; }
.panes { flex: 1; min-height: 0; display: flex; }
.listcol { width: var(--list-w); flex-shrink: 0; overflow-y: auto; background: var(--pane); border-right: 1px solid var(--rule); }
.listcol.solo { width: auto; flex: 1; border-right: 0; }
@media (min-width: 700px) and (max-width: 1099px) { .listcol { width: 380px; } }
</style>
