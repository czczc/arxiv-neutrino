<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import Icon from '../components/Icon.vue';
import ReaderPane from '../components/ReaderPane.vue';
import { useLocalState } from '../composables/useLocalState.js';
import { useMedia } from '../composables/useMedia.js';
import { useQueue } from '../composables/useQueue.js';

const props = defineProps({ id: String });
const router = useRouter();
const ls = useLocalState();
const { isPhone } = useMedia();
const queue = useQueue();

const idx = computed(() => queue.ids.value.indexOf(props.id));
const total = computed(() => queue.ids.value.length);
const prevId = computed(() => (idx.value > 0 ? queue.ids.value[idx.value - 1] : null));
const nextId = computed(() => (idx.value >= 0 && idx.value < total.value - 1 ? queue.ids.value[idx.value + 1] : null));

function back() { if (window.history.length > 1) router.back(); else router.push('/unread'); }
function go(id) { router.replace(`/paper/${id}`); }
function readNext(paper) {
  ls.markRead([paper.arxiv_id]);
  if (nextId.value) go(nextId.value); else back();
}
</script>

<template>
  <div class="shell">
    <header class="bar">
      <button class="icon-btn" aria-label="Back" @click="back"><Icon name="back" :size="22" /></button>
      <div class="pos"><template v-if="idx >= 0"><b>{{ idx + 1 }}</b> of {{ total }}</template><template v-else>Paper</template></div>
      <button class="icon-btn" :class="{ dim: !prevId }" :disabled="!prevId" aria-label="Previous" @click="go(prevId)"><Icon name="up" :size="20" /></button>
      <button class="icon-btn" :class="{ dim: !nextId }" :disabled="!nextId" aria-label="Next" @click="go(nextId)"><Icon name="down" :size="20" /></button>
    </header>
    <ReaderPane :paper-id="id" :compact="isPhone" @read-next="readNext" />
  </div>
</template>

<style scoped>
.shell { height: 100%; display: flex; flex-direction: column; background: var(--pane); }
.bar { height: 56px; display: flex; align-items: center; gap: 4px; padding: 0 8px 0 4px; border-bottom: 1px solid var(--rule); flex-shrink: 0; }
.icon-btn { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: var(--r-lg); color: var(--text-2); }
.icon-btn.dim { color: var(--ghost); }
.pos { flex: 1; text-align: center; font-size: 13px; color: var(--dim); }
.pos b { color: var(--ink); font-weight: 600; }
@media (min-width: 700px) { .shell { max-width: 860px; margin: 0 auto; border-left: 1px solid var(--rule); border-right: 1px solid var(--rule); } }
</style>
