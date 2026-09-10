<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import Icon from './Icon.vue';
import ThemePicker from './ThemePicker.vue';
import { useTheme } from '../composables/useTheme.js';
import { useFilters } from '../composables/useFilters.js';

const props = defineProps({ title: String, count: Number, isPhone: Boolean, menu: Boolean });
const emit = defineEmits(['menu', 'mark-all']);
const { q, setQuery } = useFilters();
const draft = ref(q.value);
const showSearch = ref(false);
const input = ref(null);
watch(q, (v) => { if (v !== draft.value.trim()) draft.value = v; });
// Search as you type, after a short pause.
let timer;
watch(draft, (v) => { clearTimeout(timer); timer = setTimeout(() => { if (v.trim() !== q.value) submit(); }, 250); });

const { isDark } = useTheme();
const themeOpen = ref(location.hash === '#theme');
const themeEl = ref(null);
function onDocClick(e) { if (themeOpen.value && themeEl.value && !themeEl.value.contains(e.target)) themeOpen.value = false; }
onMounted(() => document.addEventListener('click', onDocClick));
onUnmounted(() => document.removeEventListener('click', onDocClick));

function submit() { clearTimeout(timer); setQuery(draft.value.trim()); }
function focusSearch() {
  showSearch.value = true;
  requestAnimationFrame(() => input.value?.focus());
}
defineExpose({ focusSearch });
</script>

<template>
  <header class="bar">
    <button v-if="menu" class="icon-btn" aria-label="Filters" @click="emit('menu')"><Icon name="menu" :size="22" /></button>
    <span v-if="!isPhone" class="brand">Neutrino Daily</span>

    <div v-if="isPhone && !showSearch" class="title">{{ title }} <span class="mono n">{{ count }}</span></div>

    <form v-if="!isPhone || showSearch" class="search" :class="{ phone: isPhone }" @submit.prevent="submit">
      <Icon name="search" :size="13" />
      <input ref="input" v-model="draft" type="search" :placeholder="isPhone ? 'Search' : 'Search · press /'" @blur="isPhone && !draft && (showSearch = false)" />
      <button v-if="draft" type="button" class="clear" aria-label="Clear search" @click="draft = ''; submit()"><Icon name="close" :size="12" /></button>
    </form>

    <template v-if="isPhone">
      <button v-if="!showSearch" class="icon-btn" aria-label="Search" @click="focusSearch"><Icon name="search" :size="20" /></button>
      <button class="icon-btn" aria-label="Mark all read" title="Mark all loaded as read" @click="emit('mark-all')"><Icon name="check-all" :size="20" /></button>
      <div ref="themeEl" class="theme-wrap">
        <button class="icon-btn" aria-label="Theme" @click="themeOpen = !themeOpen"><Icon :name="isDark() ? 'moon' : 'sun'" :size="20" /></button>
        <div v-if="themeOpen" class="pop"><ThemePicker /></div>
      </div>
    </template>
    <template v-else>
      <button class="btn" @click="emit('mark-all')"><Icon name="check-all" :size="13" />Mark all read</button>
      <div class="kbd"><span><b>j</b><b>k</b> move</span><span><b>s</b> star</span><span><b>e</b> read · next</span><span><b>o</b> arXiv</span></div>
      <div class="local" title="Stars and read marks are stored in this browser only"><i></i>Local</div>
      <div ref="themeEl" class="theme-wrap">
        <button class="btn theme-btn" aria-label="Theme" title="Theme" @click="themeOpen = !themeOpen"><Icon :name="isDark() ? 'moon' : 'sun'" :size="14" /></button>
        <div v-if="themeOpen" class="pop"><ThemePicker /></div>
      </div>
    </template>
  </header>
</template>

<style scoped>
.bar { height: var(--bar-h); display: flex; align-items: center; gap: 12px; padding: 0 16px; background: var(--pane); border-bottom: 1px solid var(--rule); flex-shrink: 0; }
.brand { font-weight: 700; font-size: 14px; color: var(--ink); white-space: nowrap; }
.search { display: flex; align-items: center; gap: 8px; flex: 1; max-width: 420px; height: 28px; padding: 0 10px; border: 1px solid var(--rule); border-radius: var(--r-md); background: var(--pane-2); color: var(--faint); }
.search input { flex: 1; min-width: 0; border: 0; background: none; outline: none; font: inherit; font-size: 12.5px; color: var(--body); }
.search input::-webkit-search-cancel-button { display: none; }
.search:focus-within { border-color: var(--accent); }
.clear { color: var(--faint); display: flex; }
.kbd { display: flex; gap: 10px; margin-left: auto; font-size: 11.5px; color: var(--faint); white-space: nowrap; }
.kbd b { font-family: var(--font-mono); font-weight: 500; padding: 1px 5px; margin-right: 2px; border: 1px solid var(--rule-hard); border-bottom-width: 2px; border-radius: 4px; color: var(--text-3); background: var(--pane); }
.local { display: flex; align-items: center; gap: 6px; font-size: 11.5px; color: var(--dim); }
.local i { width: 7px; height: 7px; border-radius: 50%; background: var(--good); }
.icon-btn { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: var(--r-lg); color: var(--text-2); flex-shrink: 0; }
.theme-wrap { position: relative; }
.theme-btn { width: 28px; padding: 0; justify-content: center; }
.pop { position: absolute; right: 0; top: calc(100% + 6px); z-index: 30; width: 220px; padding: 12px; background: var(--pane); border: 1px solid var(--rule-hard); border-radius: var(--r-lg); box-shadow: 0 8px 24px var(--scrim); }
.title { flex: 1; font-weight: 700; font-size: 17px; color: var(--ink); display: flex; align-items: baseline; gap: 8px; white-space: nowrap; overflow: hidden; }
.title .n { font-size: 13px; font-weight: 500; color: var(--accent); }
@media (max-width: 699px) {
  .bar { height: 56px; gap: 4px; padding: 0 8px 0 4px; }
  .search.phone { max-width: none; height: 40px; border-radius: var(--r-lg); }
  .search input { font-size: 15px; }
}
@media (max-width: 1099px) { .kbd { display: none; } }
@media (max-width: 699px) { .pop { width: 260px; padding: 14px; } }
</style>
