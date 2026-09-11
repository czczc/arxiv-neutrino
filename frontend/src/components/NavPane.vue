<script setup>
import { computed, reactive, ref, watch } from 'vue';
import Icon from './Icon.vue';
import { useRoute, useRouter } from 'vue-router';
import { useFacets } from '../composables/useFacets.js';
import { useFilters } from '../composables/useFilters.js';
import { useLocalState } from '../composables/useLocalState.js';

const props = defineProps({ unreadCount: Number, showFolders: { type: Boolean, default: true } });
const emit = defineEmits(['navigate']);
const route = useRoute();
const router = useRouter();
const { facets } = useFacets();
const { tags, collab, toggleTag, setCollab, active, clear } = useFilters();
const ls = useLocalState();
const showAllTags = ref(false);
const showAllCollabs = ref(false);

const UI_KEY = 'arxivnu:nav:v1';
let saved = {};
try { saved = JSON.parse(localStorage.getItem(UI_KEY)) || {}; } catch { /* ignore */ }
const collapsed = reactive({ collabs: !!saved.collabs, tags: !!saved.tags });
watch(collapsed, (v) => { try { localStorage.setItem(UI_KEY, JSON.stringify(v)); } catch { /* ignore */ } });

const builtin = [
  { to: '/all', label: 'All papers' },
  { to: '/unread', label: 'Unread' },
  { to: '/starred', label: 'Starred' },
];
const trash = { to: '/deleted', label: 'Deleted' };
const userFolders = computed(() => ls.state.folders.map((f) => ({ to: `/folder/${f.id}`, label: f.name, id: f.id, n: Object.keys(f.ids).length })));

function newFolder() { const name = window.prompt('Folder name'); if (name?.trim()) ls.addFolder(name); }
function rename(f) { const name = window.prompt('Rename folder', f.label); if (name?.trim()) ls.renameFolder(f.id, name); }
function remove(f) {
  if (!window.confirm(`Delete folder "${f.label}"? The papers themselves are kept.`)) return;
  ls.removeFolder(f.id);
  if (route.path === f.to) router.replace('/all');
}
// Mouse drag to reorder user folders (HTML5 DnD; not available on touch).
const dragging = ref(null);
const over = ref(null);
function drop(i) { if (dragging.value != null && dragging.value !== i) ls.moveFolder(dragging.value, i); dragging.value = over.value = null; }
const folderCount = (f) => f.n != null ? f.n : f.to === '/unread' ? props.unreadCount : f.to === '/starred' ? ls.starredIds().length : f.to === '/deleted' ? ls.deletedIds().length : f.to === '/all' ? Math.max(0, facets.value.total - ls.deletedIds().length) : null;
const isOn = (f) => route.path === f.to || (f.to === '/all' && route.path.startsWith('/paper'));
const queryFor = () => ({ tags: route.query.tags, collab: route.query.collab, q: route.query.q });
</script>

<template>
  <nav class="nav">
    <div v-if="showFolders" class="group">
      <router-link v-for="f in builtin" :key="f.to" :to="{ path: f.to, query: queryFor() }" class="row" :class="{ on: isOn(f) }" @click="emit('navigate')">
        <span>{{ f.label }}</span><span v-if="folderCount(f) != null" class="c mono">{{ folderCount(f) }}</span>
      </router-link>
      <router-link v-for="(f, i) in userFolders" :key="f.id" :to="{ path: f.to, query: queryFor() }" class="row user" :class="{ on: isOn(f), over: over === i }"
                   draggable="true" @dragstart="dragging = i" @dragover.prevent="over = i" @dragleave="over = null" @drop.prevent="drop(i)" @dragend="dragging = over = null"
                   @click="emit('navigate')" @dblclick.prevent="rename(f)" :title="f.label">
        <span class="lbl">{{ f.label }}</span>
        <button class="x" :aria-label="`Rename folder ${f.label}`" title="Rename folder" @click.prevent.stop="rename(f)"><Icon name="edit" :size="11" /></button>
        <button class="x" :aria-label="`Delete folder ${f.label}`" title="Delete folder" @click.prevent.stop="remove(f)"><Icon name="close" :size="11" /></button>
        <span class="c mono">{{ f.n }}</span>
      </router-link>
      <router-link :to="{ path: trash.to, query: queryFor() }" class="row" :class="{ on: isOn(trash) }" @click="emit('navigate')">
        <span>{{ trash.label }}</span><span class="c mono">{{ folderCount(trash) }}</span>
      </router-link>
      <button class="more" @click="newFolder"><Icon name="plus" :size="12" /> New folder</button>
    </div>

    <div v-if="facets.collaborations.length" class="group">
      <button class="h4" :aria-expanded="!collapsed.collabs" @click="collapsed.collabs = !collapsed.collabs"><Icon name="down" :size="12" class="chev" :class="{ closed: collapsed.collabs }" />Collaboration</button>
      <template v-if="!collapsed.collabs">
      <button v-for="c in (showAllCollabs ? facets.collaborations : facets.collaborations.slice(0, 10))" :key="c.collaboration" class="row" :class="{ on: collab === c.collaboration }" @click="setCollab(c.collaboration)">
        <span>{{ c.collaboration }}</span><span class="c mono">{{ c.count }}</span>
      </button>
      <button v-if="facets.collaborations.length > 10" class="more" @click="showAllCollabs = !showAllCollabs">{{ showAllCollabs ? 'Fewer' : `All ${facets.collaborations.length} collaborations` }}</button>
      </template>
    </div>

    <div class="group">
      <button class="h4" :aria-expanded="!collapsed.tags" @click="collapsed.tags = !collapsed.tags"><Icon name="down" :size="12" class="chev" :class="{ closed: collapsed.tags }" />Tags</button>
      <template v-if="!collapsed.tags">
      <button v-for="t in (showAllTags ? facets.tags : facets.tags.slice(0, 12))" :key="t.tag" class="row" :class="{ on: tags.includes(t.tag) }" @click="toggleTag(t.tag)">
        <span>{{ t.tag }}</span><span class="c mono">{{ t.count }}</span>
      </button>
      <button v-if="facets.tags.length > 12" class="more" @click="showAllTags = !showAllTags">{{ showAllTags ? 'Fewer tags' : `All ${facets.tags.length} tags` }}</button>
      </template>
    </div>

    <button v-if="active" class="more" @click="clear">Clear filters</button>

  </nav>
</template>

<style scoped>
.nav { width: var(--nav-w); flex-shrink: 0; padding: 12px 10px; display: flex; flex-direction: column; gap: 14px; border-right: 1px solid var(--rule); overflow-y: auto; background: var(--bg); }
.group { display: flex; flex-direction: column; }
.h4 { display: flex; align-items: center; gap: 4px; margin: 0 0 4px 4px; padding: 2px 4px; font-size: 10.5px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--faint); }
.h4:hover { color: var(--text-3); }
.chev { transition: transform 0.15s; }
.chev.closed { transform: rotate(-90deg); }
.row { display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 5px 8px; border-radius: var(--r-md); color: var(--text-2); font-size: 12.5px; text-align: left; width: 100%; }
.row:hover { background: var(--rule-soft); }
.row.on { background: var(--nav-on); color: var(--ink); font-weight: 600; }
.row .c { font-size: 11px; color: var(--faint); }
.row.user .lbl { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row.user .x { display: none; color: var(--faint); width: 16px; height: 16px; align-items: center; justify-content: center; border-radius: 4px; }
.row.user:hover .x { display: flex; }
.row.user .x:hover { color: var(--ink); background: var(--rule); }
.row.user .x:last-of-type:hover { color: var(--bad); }
.row.user.over { box-shadow: inset 0 2px 0 var(--accent); }
.row.on .c { color: var(--accent); }
.more { align-self: flex-start; margin: 4px 8px 0; font-size: 12px; color: var(--accent); display: flex; align-items: center; gap: 4px; }
@media (max-width: 699px) {
  .nav { width: min(320px, 85vw); padding: 14px 12px; gap: 18px; }
  .row { min-height: 44px; font-size: 15px; padding: 0 12px; }
  .h4 { min-height: 36px; font-size: 12px; }
  .row .c { font-size: 12.5px; }
  .more { font-size: 14px; min-height: 44px; display: flex; align-items: center; }
}
</style>
