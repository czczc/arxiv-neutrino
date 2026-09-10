<script setup>
import { computed, ref, watch } from 'vue';
import Icon from './Icon.vue';
import { arxivUrl, fetchPaper, inspireUrl } from '../api.js';
import { renderMath } from '../lib/math.js';
import { longDay } from '../lib/dates.js';
import { useLocalState } from '../composables/useLocalState.js';

const props = defineProps({ paperId: String, compact: Boolean });
const emit = defineEmits(['read-next']);
const ls = useLocalState();
const paper = ref(null);
const error = ref('');

watch(() => props.paperId, async (id) => {
  paper.value = null; error.value = '';
  if (!id) return;
  try { paper.value = await fetchPaper(id); } catch (e) { error.value = e.message; }
}, { immediate: true });

const title = computed(() => renderMath(paper.value?.title));
const abstract = computed(() => renderMath(paper.value?.abstract));
const read = computed(() => paper.value && ls.isRead(paper.value));
const starred = computed(() => paper.value && ls.isStarred(paper.value.arxiv_id));
function openArxiv() { ls.markRead([paper.value.arxiv_id]); }
</script>

<template>
  <div class="reader" :class="{ compact }">
    <div v-if="!paperId" class="empty">Select a paper to read its summary.</div>
    <div v-else-if="error" class="empty">{{ error }}</div>
    <template v-else-if="paper">
      <div class="scroll">
        <div v-if="!compact" class="acts">
          <button class="btn" :class="{ 'star-on': starred }" @click="ls.toggleStar(paper.arxiv_id)">
            <svg width="13" height="13" viewBox="0 0 24 24" :fill="starred ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><path d="M12 3.5l2.7 5.6 6.1.8-4.5 4.3 1.1 6.1L12 17.4l-5.4 2.9 1.1-6.1L3.2 9.9l6.1-.8z" /></svg>{{ starred ? 'Starred' : 'Star' }}
          </button>
          <button class="btn" :class="{ 'read-on': read }" @click="ls.toggleRead(paper)"><Icon name="check" :size="13" />{{ read ? 'Read' : 'Mark read' }}</button>
          <span class="sp"></span>
          <a class="btn" :href="arxivUrl(paper.arxiv_id)" target="_blank" rel="noopener" @click="openArxiv">arXiv<Icon name="external" :size="12" /></a>
          <a class="btn" :href="inspireUrl(paper.arxiv_id)" target="_blank" rel="noopener">InspireHEP<Icon name="external" :size="12" /></a>
        </div>
        <div class="tags">
          <span v-if="paper.collaboration" class="tag collab">{{ paper.collaboration }}</span>
          <span v-for="t in paper.tags" :key="t" class="tag">{{ t }}</span>
        </div>
        <h1 class="title" v-html="title"></h1>
        <div class="meta">
          <b v-if="paper.collaboration">{{ paper.collaboration }} Collaboration</b>
          <span class="mono">arXiv:{{ paper.arxiv_id }}</span>
          <span>{{ longDay(paper.submitted_date) }}</span>
          <span v-if="paper.journal_ref">{{ paper.journal_ref }}</span>
        </div>
        <div v-if="paper.authors.length" class="authors">
          {{ paper.authors.slice(0, 12).join(', ') }}<span v-if="paper.author_count > 12"> and {{ paper.author_count - 12 }} more</span>
        </div>
        <section v-if="paper.summary">
          <div class="sec-h">Summary</div>
          <p class="sum">{{ paper.summary }}</p>
        </section>
        <section v-else><div class="sec-h">Summary</div><p class="sum pending">Summary pending.</p></section>
        <section>
          <div class="sec-h">Abstract</div>
          <p class="abs" v-html="abstract"></p>
        </section>
        <div v-if="!compact" class="foot">Stars and read marks are kept in this browser only.</div>
      </div>
      <div v-if="compact" class="actionbar">
        <button class="abtn" :class="{ 'star-on': starred }" @click="ls.toggleStar(paper.arxiv_id)">
          <svg width="18" height="18" viewBox="0 0 24 24" :fill="starred ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><path d="M12 3.5l2.7 5.6 6.1.8-4.5 4.3 1.1 6.1L12 17.4l-5.4 2.9 1.1-6.1L3.2 9.9l6.1-.8z" /></svg>{{ starred ? 'Starred' : 'Star' }}
        </button>
        <button class="abtn primary" @click="emit('read-next', paper)"><Icon name="check" :size="18" />{{ read ? 'Next' : 'Read · next' }}</button>
        <a class="abtn" :href="arxivUrl(paper.arxiv_id)" target="_blank" rel="noopener" @click="openArxiv"><Icon name="external" :size="18" />arXiv</a>
        <a class="abtn" :href="inspireUrl(paper.arxiv_id)" target="_blank" rel="noopener"><Icon name="external" :size="18" />Inspire</a>
      </div>
    </template>
    <div v-else class="empty">Loading…</div>
  </div>
</template>

<style scoped>
.reader { flex: 1; min-width: 0; min-height: 0; display: flex; flex-direction: column; background: var(--bg); }
.scroll { flex: 1; min-height: 0; overflow-y: auto; padding: 22px 28px 28px; display: flex; flex-direction: column; gap: 14px; }
.empty { flex: 1; display: flex; align-items: center; justify-content: center; color: var(--faint); padding: 40px; text-align: center; }
.acts { display: flex; gap: 8px; align-items: center; }
.sp { flex: 1; }
.title { margin: 0; font-size: 20px; font-weight: 700; line-height: 1.3; letter-spacing: -0.01em; color: var(--ink); }
.meta { font-size: 12.5px; color: var(--dim); display: flex; gap: 8px; flex-wrap: wrap; }
.meta b { color: var(--text-2); font-weight: 600; }
.authors { font-size: 12.5px; color: var(--text-3); line-height: 1.5; }
section p { margin: 0; }
.sum { font-size: 14px; line-height: 1.55; color: var(--body); }
.sum.pending { color: var(--faint); font-style: italic; }
.abs { font-size: 13px; line-height: 1.55; color: var(--text-3); }
.foot { margin-top: auto; padding-top: 14px; font-size: 11.5px; color: var(--faint); }
.actionbar { display: flex; gap: 8px; padding: 10px 12px calc(14px + env(safe-area-inset-bottom)); border-top: 1px solid var(--rule); background: var(--pane); }
.abtn { flex: 1; height: 48px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; border: 1px solid var(--rule-hard); border-radius: var(--r-lg); background: var(--pane); color: var(--text-2); font-size: 11.5px; font-weight: 600; }
.abtn.star-on { color: var(--star-ink); border-color: var(--star-rule); background: var(--star-bg); }
.abtn.primary { background: var(--ink); color: var(--on-ink); border-color: var(--ink); }
.compact { background: var(--pane); }
.compact .scroll { padding: 18px 18px 24px; }
.compact .title { font-size: 21px; }
.compact .meta, .compact .authors { font-size: 13px; }
.compact .sum { font-size: 15.5px; line-height: 1.5; }
.compact .abs { font-size: 14px; line-height: 1.5; }
</style>
