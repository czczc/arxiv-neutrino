<script setup>
import Icon from './Icon.vue';
import { useFilters } from '../composables/useFilters.js';
import { longDay } from '../lib/dates.js';
const emit = defineEmits(['add']);
const { tags, collab, q, date, toggleTag, setCollab, setQuery, setDate, active } = useFilters();
</script>

<template>
  <div v-if="active" class="chips">
    <button v-if="collab" class="chip on" @click="setCollab(collab)">{{ collab }}<Icon name="close" :size="11" /></button>
    <button v-for="t in tags" :key="t" class="chip on" @click="toggleTag(t)">{{ t }}<Icon name="close" :size="11" /></button>
    <button v-if="q" class="chip on" @click="setQuery('')">“{{ q }}”<Icon name="close" :size="11" /></button>
    <button v-if="date" class="chip on" @click="setDate('')">{{ longDay(date) }}<Icon name="close" :size="11" /></button>
    <button class="chip add" @click="emit('add')">+ filter</button>
  </div>
</template>

<style scoped>
.chips { display: flex; gap: 8px; padding: 8px 12px; overflow-x: auto; border-bottom: 1px solid var(--rule-soft); background: var(--pane); scrollbar-width: none; }
.chips::-webkit-scrollbar { display: none; }
.chip { display: inline-flex; align-items: center; gap: 6px; height: 28px; padding: 0 10px; border-radius: 999px; border: 1px solid var(--rule-hard); background: var(--pane); font-size: 12.5px; font-weight: 500; color: var(--text-2); white-space: nowrap; }
.chip.on { background: var(--ink); color: #fff; border-color: var(--ink); }
.chip.add { color: var(--accent); border-style: dashed; }
@media (max-width: 699px) {
  .chips { padding: 10px 12px; }
  .chip { height: 34px; padding: 0 12px; font-size: 13.5px; }
}
</style>
