<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import Icon from './Icon.vue';
import { useLocalState } from '../composables/useLocalState.js';

// "Add to" button + checklist of the user's folders for one paper.
const props = defineProps({ paperId: String, compact: Boolean });
const ls = useLocalState();
const open = ref(false);
const el = ref(null);
function onDocClick(e) { if (open.value && el.value && !el.value.contains(e.target)) open.value = false; }
onMounted(() => document.addEventListener('click', onDocClick));
onUnmounted(() => document.removeEventListener('click', onDocClick));

function create() {
  const name = window.prompt('Folder name');
  if (!name?.trim()) return;
  ls.toggleInFolder(ls.addFolder(name).id, props.paperId);
}
const count = () => ls.state.folders.filter((f) => f.ids[props.paperId]).length;
</script>

<template>
  <div ref="el" class="wrap">
    <button :class="compact ? 'abtn' : 'btn'" :aria-expanded="open" @click="open = !open">
      <Icon name="folder" :size="compact ? 18 : 13" />{{ count() ? `In ${count()}` : 'Add to' }}
    </button>
    <div v-if="open" class="pop">
      <label v-for="f in ls.state.folders" :key="f.id" class="item">
        <input type="checkbox" :checked="!!f.ids[paperId]" @change="ls.toggleInFolder(f.id, paperId)" />
        <span>{{ f.name }}</span>
      </label>
      <div v-if="!ls.state.folders.length" class="none">No folders yet.</div>
      <button class="new" @click="create"><Icon name="plus" :size="12" />New folder…</button>
    </div>
  </div>
</template>

<style scoped>
.wrap { position: relative; display: flex; }
.wrap:has(.abtn) { flex: 1; }
.pop { position: absolute; left: 0; bottom: auto; top: calc(100% + 6px); z-index: 30; min-width: 200px; padding: 6px; background: var(--pane); border: 1px solid var(--rule-hard); border-radius: var(--r-lg); box-shadow: 0 8px 24px var(--scrim); display: flex; flex-direction: column; }
.wrap:has(.abtn) .pop { top: auto; bottom: calc(100% + 6px); }
.item { display: flex; align-items: center; gap: 8px; padding: 6px 8px; border-radius: var(--r-md); font-size: 13px; color: var(--text-2); cursor: pointer; }
.item:hover { background: var(--rule-soft); }
.item input { accent-color: var(--accent); }
.none { padding: 6px 8px; font-size: 12.5px; color: var(--faint); }
.new { display: flex; align-items: center; gap: 6px; padding: 6px 8px; margin-top: 4px; border-top: 1px solid var(--rule); font-size: 12.5px; color: var(--accent); }
@media (max-width: 699px) { .item { min-height: 44px; font-size: 15px; } .new { min-height: 44px; font-size: 14px; } }
</style>
