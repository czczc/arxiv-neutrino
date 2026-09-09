<script setup>
import { useLocalState } from '../composables/useLocalState.js';
import { todayIso } from '../lib/dates.js';
const props = defineProps({ total: Number });
const ls = useLocalState();
function markOld() { ls.setReadBefore(todayIso()); ls.dismissBanner(); }
</script>

<template>
  <div v-if="!ls.state.bannerDismissed && !ls.state.readBefore && total > 30" class="banner">
    <div class="txt"><b>New here?</b> All {{ total }} papers show as unread. You can start fresh from today.</div>
    <div class="acts">
      <button class="btn primary" @click="markOld">Mark everything before today read</button>
      <button class="btn" @click="ls.dismissBanner()">Keep them</button>
    </div>
  </div>
</template>

<style scoped>
.banner { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: #fff8e6; border-bottom: 1px solid oklch(0.88 0.08 80); font-size: 12.5px; color: var(--text-2); }
.txt { flex: 1; }
.acts { display: flex; gap: 8px; }
@media (max-width: 699px) {
  .banner { flex-direction: column; align-items: stretch; font-size: 14px; }
  .acts .btn { flex: 1; justify-content: center; }
}
</style>
