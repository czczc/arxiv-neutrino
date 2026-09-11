<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import Icon from './Icon.vue';
import { useLocalState } from '../composables/useLocalState.js';

// Top-bar button: export / import the browser-local marks as JSON.
const props = defineProps({ phone: Boolean });
const ls = useLocalState();
const open = ref(false);
const el = ref(null);
const fileInput = ref(null);
const msg = ref('');
function onDocClick(e) { if (open.value && el.value && !el.value.contains(e.target)) open.value = false; }
onMounted(() => document.addEventListener('click', onDocClick));
onUnmounted(() => document.removeEventListener('click', onDocClick));

function doExport() {
  const blob = new Blob([ls.exportJson()], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `neutrino-daily-marks-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
  open.value = false;
}
async function doImport(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  try {
    const n = ls.importJson(await file.text());
    msg.value = `Imported ${n.stars} stars, ${n.read} read marks`;
  } catch {
    msg.value = 'Could not read that file';
  }
  e.target.value = '';
  setTimeout(() => (msg.value = ''), 4000);
}
</script>

<template>
  <div ref="el" class="wrap">
    <button :class="phone ? 'icon-btn' : 'btn theme-btn'" aria-label="Export or import" title="Export / import" @click="open = !open"><Icon name="sync" :size="phone ? 20 : 14" /></button>
    <div v-if="open" class="pop">
      <div class="note">Stars, read marks, deletions and folders are kept in this browser only. Move them to another browser with a JSON file.</div>
      <button class="item" @click="doExport"><Icon name="download" :size="14" />Export…</button>
      <button class="item" @click="fileInput.click()"><Icon name="upload" :size="14" />Import…</button>
      <input ref="fileInput" type="file" accept="application/json" hidden @change="doImport" />
      <div v-if="msg" class="msg">{{ msg }}</div>
    </div>
  </div>
</template>

<style scoped>
.wrap { position: relative; }
.icon-btn { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: var(--r-lg); color: var(--text-2); flex-shrink: 0; }
.theme-btn { width: 28px; padding: 0; justify-content: center; }
.pop { position: absolute; right: 0; top: calc(100% + 6px); z-index: 30; width: 260px; padding: 8px; background: var(--pane); border: 1px solid var(--rule-hard); border-radius: var(--r-lg); box-shadow: 0 8px 24px var(--scrim); display: flex; flex-direction: column; }
.note { padding: 4px 8px 8px; font-size: 12px; line-height: 1.45; color: var(--faint); border-bottom: 1px solid var(--rule); margin-bottom: 4px; }
.item { display: flex; align-items: center; gap: 8px; padding: 7px 8px; border-radius: var(--r-md); font-size: 13px; color: var(--text-2); text-align: left; }
.item:hover { background: var(--rule-soft); }
.msg { padding: 6px 8px 2px; font-size: 12px; color: var(--good); }
@media (max-width: 699px) { .item { min-height: 44px; font-size: 15px; } .note { font-size: 13px; } }
</style>
