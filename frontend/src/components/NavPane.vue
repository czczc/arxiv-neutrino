<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { useFacets } from '../composables/useFacets.js';
import { useFilters } from '../composables/useFilters.js';
import { useLocalState } from '../composables/useLocalState.js';

const props = defineProps({ unreadCount: Number, showFolders: { type: Boolean, default: true } });
const emit = defineEmits(['navigate']);
const route = useRoute();
const { facets } = useFacets();
const { tags, collab, toggleTag, setCollab, active, clear } = useFilters();
const ls = useLocalState();
const showAllTags = ref(false);
const fileInput = ref(null);
const importMsg = ref('');

const folders = [
  { to: '/unread', label: 'Unread' },
  { to: '/starred', label: 'Starred' },
  { to: '/all', label: 'All papers' },
  { to: '/archive', label: 'Archive' },
];
const folderCount = (f) => f.to === '/unread' ? props.unreadCount : f.to === '/starred' ? ls.starredIds().length : f.to === '/all' ? facets.value.total : null;
const isOn = (f) => route.path === f.to || (f.to === '/all' && route.path.startsWith('/paper'));
const queryFor = () => ({ tags: route.query.tags, collab: route.query.collab, q: route.query.q });

function doExport() {
  const blob = new Blob([ls.exportJson()], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `arxiv-neutrino-marks-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
}
async function doImport(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  try {
    const n = ls.importJson(await file.text());
    importMsg.value = `Imported ${n.stars} stars, ${n.read} read marks`;
  } catch {
    importMsg.value = 'Could not read that file';
  }
  e.target.value = '';
  setTimeout(() => (importMsg.value = ''), 4000);
}
</script>

<template>
  <nav class="nav">
    <div v-if="showFolders" class="group">
      <router-link v-for="f in folders" :key="f.to" :to="{ path: f.to, query: queryFor() }" class="row" :class="{ on: isOn(f) }" @click="emit('navigate')">
        <span>{{ f.label }}</span><span v-if="folderCount(f) != null" class="c mono">{{ folderCount(f) }}</span>
      </router-link>
    </div>

    <div v-if="facets.collaborations.length" class="group">
      <h4>Collaboration</h4>
      <button v-for="c in facets.collaborations" :key="c.collaboration" class="row" :class="{ on: collab === c.collaboration }" @click="setCollab(c.collaboration)">
        <span>{{ c.collaboration }}</span><span class="c mono">{{ c.count }}</span>
      </button>
    </div>

    <div class="group">
      <h4>Tags</h4>
      <button v-for="t in (showAllTags ? facets.tags : facets.tags.slice(0, 12))" :key="t.tag" class="row" :class="{ on: tags.includes(t.tag) }" @click="toggleTag(t.tag)">
        <span>{{ t.tag }}</span><span class="c mono">{{ t.count }}</span>
      </button>
      <button v-if="facets.tags.length > 12" class="more" @click="showAllTags = !showAllTags">{{ showAllTags ? 'Fewer tags' : `All ${facets.tags.length} tags` }}</button>
    </div>

    <button v-if="active" class="more" @click="clear">Clear filters</button>

    <div class="foot">
      <div>Stars and read marks are kept in this browser only.</div>
      <div class="links">
        <button @click="doExport">Export</button>
        <span>·</span>
        <button @click="fileInput.click()">Import</button>
        <input ref="fileInput" type="file" accept="application/json" hidden @change="doImport" />
      </div>
      <div v-if="importMsg" class="msg">{{ importMsg }}</div>
    </div>
  </nav>
</template>

<style scoped>
.nav { width: var(--nav-w); flex-shrink: 0; padding: 12px 10px; display: flex; flex-direction: column; gap: 14px; border-right: 1px solid var(--rule); overflow-y: auto; background: var(--bg); }
.group { display: flex; flex-direction: column; }
h4 { margin: 0 0 4px 8px; font-size: 10.5px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--faint); }
.row { display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 5px 8px; border-radius: var(--r-md); color: var(--text-2); font-size: 12.5px; text-align: left; width: 100%; }
.row:hover { background: var(--rule-soft); }
.row.on { background: #e5e9f2; color: var(--ink); font-weight: 600; }
.row .c { font-size: 11px; color: var(--faint); }
.row.on .c { color: var(--accent); }
.more { align-self: flex-start; margin: 4px 8px 0; font-size: 12px; color: var(--accent); }
.foot { margin-top: auto; padding: 10px 8px 0; border-top: 1px solid var(--rule); font-size: 11.5px; color: var(--faint); display: flex; flex-direction: column; gap: 4px; }
.links { display: flex; gap: 6px; }
.links button { color: var(--text-3); font-weight: 500; }
.msg { color: var(--good); }
@media (max-width: 699px) {
  .nav { width: min(320px, 85vw); padding: 14px 12px; gap: 18px; }
  .row { min-height: 44px; font-size: 15px; padding: 0 12px; }
  .row .c { font-size: 12.5px; }
  .more { font-size: 14px; min-height: 44px; display: flex; align-items: center; }
  .foot { font-size: 13px; }
  .links button { min-height: 44px; padding: 0 6px; }
}
</style>
