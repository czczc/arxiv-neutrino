<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import TopBar from '../components/TopBar.vue';
import NavPane from '../components/NavPane.vue';
import BottomTabs from '../components/BottomTabs.vue';
import Drawer from '../components/Drawer.vue';
import { fetchDates } from '../api.js';
import { monthName, todayIso } from '../lib/dates.js';
import { useMedia } from '../composables/useMedia.js';

const router = useRouter();
const { isPhone, isWide } = useMedia();
const dates = ref([]);
const drawer = ref(false);
fetchDates().then((d) => (dates.value = d));

const WEEK = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
const today = todayIso();
const pad = (n) => String(n).padStart(2, '0');

// One grid per month that has papers, newest first. Cells are null for the
// leading blanks before the 1st, otherwise { iso, day, count, future }.
const months = computed(() => {
  const byDate = new Map(dates.value.map((d) => [d.date, d.count]));
  const keys = [...new Set(dates.value.map((d) => d.date.slice(0, 7)))].sort().reverse();
  return keys.map((key) => {
    const [y, m] = key.split('-').map(Number);
    const first = new Date(y, m - 1, 1).getDay();
    const days = new Date(y, m, 0).getDate();
    const cells = Array(first).fill(null);
    let total = 0;
    for (let d = 1; d <= days; d++) {
      const iso = `${y}-${pad(m)}-${pad(d)}`;
      const count = byDate.get(iso) || 0;
      total += count;
      cells.push({ iso, day: d, count, future: iso > today });
    }
    return { key, title: `${monthName(m)} ${y}`, total, cells };
  });
});
const total = computed(() => dates.value.reduce((n, d) => n + d.count, 0));
const openDay = (iso) => router.push({ path: '/all', query: { date: iso } });
</script>

<template>
  <div class="shell">
    <TopBar title="Archive" :count="total" :is-phone="isPhone" :menu="!isWide" @menu="drawer = true" />
    <div class="panes">
      <NavPane v-if="isWide" />
      <div class="content">
        <div class="months">
          <section v-for="M in months" :key="M.key" class="month">
            <h2>{{ M.title }} <span class="mono c">{{ M.total }}</span></h2>
            <div class="grid">
              <div v-for="(w, i) in WEEK" :key="i" class="wd">{{ w }}</div>
              <template v-for="(cell, i) in M.cells" :key="i">
                <div v-if="!cell" class="blank"></div>
                <button v-else class="day" :class="{ has: cell.count, today: cell.iso === today, future: cell.future }"
                        :disabled="!cell.count" :title="cell.count ? `${cell.count} papers` : ''" @click="openDay(cell.iso)">
                  <span class="n">{{ cell.day }}</span>
                  <span v-if="cell.count" class="mono k">{{ cell.count }}</span>
                </button>
              </template>
            </div>
          </section>
        </div>
        <div v-if="!dates.length" class="empty">Loading…</div>
      </div>
    </div>
    <BottomTabs v-if="isPhone" />
    <Drawer :open="drawer" @close="drawer = false"><NavPane :show-folders="isPhone" @navigate="drawer = false" /></Drawer>
  </div>
</template>

<style scoped>
.shell { height: 100%; display: flex; flex-direction: column; }
.panes { flex: 1; min-height: 0; display: flex; }
.content { flex: 1; overflow-y: auto; padding: 18px 24px 40px; }
.months { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 22px 32px; max-width: 1000px; }
h2 { font-size: 15px; font-weight: 700; color: var(--ink); margin: 0 0 8px; padding-bottom: 6px; border-bottom: 2px solid var(--ink); }
.c { font-size: 11.5px; color: var(--faint); font-weight: 400; margin-left: 6px; }
.grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }
.wd { text-align: center; font-size: 10.5px; font-weight: 600; color: var(--faint); padding-bottom: 2px; }
.day { position: relative; aspect-ratio: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1px; border-radius: var(--r-md); border: 1px solid transparent; color: var(--faint); font-size: 12px; }
.day .n { line-height: 1; }
.day .k { font-size: 10px; line-height: 1; color: var(--accent); font-weight: 600; }
.day:disabled { cursor: default; }
.day.future { color: var(--ghost); }
.day.today { border-color: var(--accent); }
.day.has { color: var(--ink); background: var(--pane); border-color: var(--rule); }
.day.has:hover { border-color: var(--accent); background: var(--sel); }
.empty { color: var(--faint); padding: 40px; text-align: center; }
@media (max-width: 699px) {
  .content { padding: 12px 16px 24px; }
  .months { grid-template-columns: 1fr; }
  .day { font-size: 14px; }
  .day .k { font-size: 11px; }
}
</style>
