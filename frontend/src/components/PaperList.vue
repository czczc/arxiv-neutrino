<script setup>
import { computed, reactive } from 'vue';
import Icon from './Icon.vue';
import PaperRow from './PaperRow.vue';
import { shortDay } from '../lib/dates.js';
import { useLocalState } from '../composables/useLocalState.js';

const props = defineProps({
  papers: Array, selectedId: String, loading: Boolean, hasMore: Boolean, swipe: Boolean, emptyText: String,
});
const emit = defineEmits(['select', 'load-more', 'mark-day']);
const ls = useLocalState();

const days = computed(() => {
  const out = [];
  let cur = null;
  for (const p of props.papers) {
    if (!cur || cur.date !== p.submitted_date) { cur = { date: p.submitted_date, papers: [] }; out.push(cur); }
    cur.papers.push(p);
  }
  return out;
});
const unreadIn = (d) => d.papers.filter((p) => !ls.isRead(p)).length;
const collapsed = reactive({});
</script>

<template>
  <div class="list">
    <template v-for="d in days" :key="d.date">
      <div class="lhead" role="button" :aria-expanded="!collapsed[d.date]" @click="collapsed[d.date] = !collapsed[d.date]">
        <Icon name="down" :size="12" class="chev" :class="{ closed: collapsed[d.date] }" />
        <span>{{ shortDay(d.date) }}</span>
        <span class="mono cnt">{{ d.papers.length }}<template v-if="unreadIn(d) && unreadIn(d) !== d.papers.length"> · {{ unreadIn(d) }} unread</template></span>
        <button v-if="unreadIn(d)" class="mk" @click.stop="emit('mark-day', d.papers)">Mark day read</button>
      </div>
      <PaperRow v-for="p in (collapsed[d.date] ? [] : d.papers)" :key="p.arxiv_id" :paper="p" :selected="p.arxiv_id === selectedId"
                :read="ls.isRead(p)" :starred="ls.isStarred(p.arxiv_id)" :swipe="swipe"
                @select="emit('select', p)" @toggle-star="ls.toggleStar(p.arxiv_id)" @toggle-read="ls.toggleRead(p)" />
    </template>
    <div v-if="!loading && !papers.length" class="empty">{{ emptyText || 'Nothing here.' }}</div>
    <div v-if="loading" class="empty">Loading…</div>
    <button v-else-if="hasMore" class="more" @click="emit('load-more')">Load older papers</button>
  </div>
</template>

<style scoped>
.list { display: flex; flex-direction: column; background: var(--pane); }
.lhead { position: sticky; top: 0; z-index: 1; display: flex; align-items: center; gap: 8px; height: 34px; padding: 0 12px; background: var(--pane-2); border-bottom: 1px solid var(--rule); font-size: 11px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--faint); }
.lhead { cursor: pointer; user-select: none; }
.chev { flex-shrink: 0; transition: transform 0.15s; }
.chev.closed { transform: rotate(-90deg); }
.cnt { font-weight: 400; letter-spacing: 0; }
.mk { margin-left: auto; font-weight: 500; font-size: 11.5px; color: var(--accent); height: 34px; }
.empty { padding: 40px 16px; text-align: center; color: var(--faint); }
.more { margin: 14px auto 24px; padding: 8px 16px; border: 1px solid var(--rule-hard); border-radius: var(--r-md); color: var(--text-2); font-size: 12.5px; font-weight: 500; background: var(--pane); }
@media (max-width: 699px) {
  .lhead { height: 36px; padding: 0 14px; font-size: 11.5px; background: var(--bg); }
  .mk { font-size: 13px; font-weight: 600; height: 36px; }
  .more { min-height: 44px; font-size: 14px; }
}
</style>
