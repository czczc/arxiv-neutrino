<script setup>
import { computed, ref } from 'vue';
import Icon from './Icon.vue';
import { renderMath } from '../lib/math.js';

const props = defineProps({ paper: Object, selected: Boolean, read: Boolean, starred: Boolean, swipe: Boolean });
const emit = defineEmits(['select', 'toggle-star', 'toggle-read']);

const authors = computed(() => {
  const p = props.paper;
  if (p.collaboration) return null;
  const names = p.authors.map((a) => a.split(' ').slice(-1)[0]);
  if (p.author_count > 3) return `${names[0]} et al.`;
  return names.join(', ');
});
const title = computed(() => renderMath(props.paper.title));

// Touch swipe: right = toggle read, left = toggle star. Visual reveal while
// dragging; committed past 80px. Mouse users get the buttons in the reader.
const dx = ref(0);
let startX = 0, startY = 0, tracking = false;
function ts(e) { if (!props.swipe) return; startX = e.touches[0].clientX; startY = e.touches[0].clientY; tracking = true; }
function tm(e) {
  if (!tracking) return;
  const mx = e.touches[0].clientX - startX, my = e.touches[0].clientY - startY;
  if (Math.abs(my) > Math.abs(mx) && Math.abs(dx.value) < 10) { tracking = false; dx.value = 0; return; }
  dx.value = Math.max(-140, Math.min(140, mx));
}
function te() {
  if (!tracking) return;
  tracking = false;
  if (dx.value > 80) emit('toggle-read');
  else if (dx.value < -80) emit('toggle-star');
  dx.value = 0;
}
</script>

<template>
  <div class="swipe" @touchstart.passive="ts" @touchmove.passive="tm" @touchend="te" @touchcancel="te">
    <div class="reveal left" :class="{ arm: dx > 80 }"><Icon name="check" :size="20" />{{ read ? 'Unread' : 'Read' }}</div>
    <div class="reveal right" :class="{ arm: dx < -80 }"><Icon name="star" :size="20" />{{ starred ? 'Unstar' : 'Star' }}</div>
    <div class="row" :class="{ sel: selected, read }" :style="dx ? { transform: `translateX(${dx}px)` } : null" @click="emit('select')">
      <span class="dot"></span>
      <button class="st" :class="{ on: starred }" :aria-label="starred ? 'Unstar' : 'Star'" @click.stop="emit('toggle-star')">
        <svg width="13" height="13" viewBox="0 0 24 24" :fill="starred ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><path d="M12 3.5l2.7 5.6 6.1.8-4.5 4.3 1.1 6.1L12 17.4l-5.4 2.9 1.1-6.1L3.2 9.9l6.1-.8z" /></svg>
      </button>
      <div class="body">
        <div class="t" v-html="title"></div>
        <div class="m">
          <b v-if="paper.collaboration">{{ paper.collaboration }}</b>
          <span v-else-if="authors">{{ authors }}</span>
          <span class="mono">{{ paper.arxiv_id }}</span>
          <span v-if="paper.tags.length" class="tg">{{ paper.tags.slice(0, 2).join(', ') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.swipe { position: relative; overflow: hidden; border-bottom: 1px solid var(--rule-soft); }
.reveal { position: absolute; top: 0; bottom: 0; width: 140px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; font-size: 12px; font-weight: 600; color: #fff; opacity: 0.6; }
.reveal.arm { opacity: 1; }
.reveal.left { left: 0; background: var(--good); }
.reveal.right { right: 0; background: var(--star); }
.row { position: relative; display: flex; gap: 10px; padding: 9px 12px 9px 10px; align-items: flex-start; background: var(--pane); cursor: pointer; transition: transform 0.08s linear; }
.row:hover { background: var(--pane-2); }
.row.sel { background: var(--sel); box-shadow: inset 3px 0 0 var(--accent); }
.dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); margin-top: 6px; flex-shrink: 0; }
.row.read .dot { background: transparent; }
.st { color: var(--ghost); margin-top: 1px; flex-shrink: 0; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; }
.st.on { color: var(--star); }
.body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.t { font-weight: 600; font-size: 13px; color: var(--ink); line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.row.read .t { font-weight: 400; color: #5a6170; }
.m { font-size: 11.5px; color: var(--faint); display: flex; gap: 6px; white-space: nowrap; overflow: hidden; }
.m b { color: var(--text-3); font-weight: 600; }
.m .tg { overflow: hidden; text-overflow: ellipsis; }
@media (max-width: 699px) {
  .row { padding: 12px 14px 12px 12px; min-height: 44px; }
  .dot { width: 8px; height: 8px; margin-top: 7px; }
  .st { width: 32px; height: 32px; margin: -6px -6px 0 -8px; }
  .t { font-size: 15px; }
  .m { font-size: 12.5px; }
}
</style>
