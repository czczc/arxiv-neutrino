<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import TopBar from '../components/TopBar.vue';
import NavPane from '../components/NavPane.vue';
import BottomTabs from '../components/BottomTabs.vue';
import Drawer from '../components/Drawer.vue';
import { fetchDates } from '../api.js';
import { monthName, shortDay } from '../lib/dates.js';
import { useMedia } from '../composables/useMedia.js';

const router = useRouter();
const { isPhone, isWide } = useMedia();
const dates = ref([]);
const drawer = ref(false);
const open = ref({});
fetchDates().then((d) => { dates.value = d; if (d.length) open.value[d[0].date.slice(0, 7)] = true; });

const tree = computed(() => {
  const years = new Map();
  for (const d of dates.value) {
    const [y, m] = d.date.split('-');
    if (!years.has(y)) years.set(y, { year: y, count: 0, months: new Map() });
    const Y = years.get(y); Y.count += d.count;
    const key = `${y}-${m}`;
    if (!Y.months.has(key)) Y.months.set(key, { key, name: monthName(m), count: 0, days: [] });
    const M = Y.months.get(key); M.count += d.count; M.days.push(d);
  }
  return [...years.values()].map((Y) => ({ ...Y, months: [...Y.months.values()] }));
});
const total = computed(() => dates.value.reduce((n, d) => n + d.count, 0));
const openDay = (d) => router.push({ path: '/all', query: { date: d } });
</script>

<template>
  <div class="shell">
    <TopBar title="Archive" :count="total" :is-phone="isPhone" :menu="!isWide" @menu="drawer = true" />
    <div class="panes">
      <NavPane v-if="isWide" />
      <div class="content">
        <div v-for="Y in tree" :key="Y.year" class="year">
          <h2>{{ Y.year }} <span class="mono c">{{ Y.count }}</span></h2>
          <div v-for="M in Y.months" :key="M.key" class="month">
            <button class="mh" @click="open[M.key] = !open[M.key]">
              <span class="tri" :class="{ on: open[M.key] }">▸</span>{{ M.name }} <span class="mono c">{{ M.count }}</span>
            </button>
            <div v-if="open[M.key]" class="days">
              <button v-for="d in M.days" :key="d.date" class="day" @click="openDay(d.date)">
                <span>{{ shortDay(d.date) }}</span><span class="mono c">{{ d.count }}</span>
              </button>
            </div>
          </div>
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
.content { flex: 1; overflow-y: auto; padding: 18px 24px 40px; max-width: 720px; }
h2 { font-size: 16px; font-weight: 700; color: var(--ink); margin: 14px 0 6px; padding-bottom: 6px; border-bottom: 2px solid var(--ink); }
.c { font-size: 11.5px; color: var(--faint); font-weight: 400; margin-left: 6px; }
.mh { display: flex; align-items: center; gap: 6px; height: 34px; font-size: 13.5px; font-weight: 600; color: var(--text-2); }
.tri { display: inline-block; color: var(--faint); transition: transform 0.12s; }
.tri.on { transform: rotate(90deg); }
.days { display: flex; flex-direction: column; padding-left: 18px; margin-bottom: 8px; }
.day { display: flex; justify-content: space-between; align-items: center; height: 32px; padding: 0 10px; border-radius: var(--r-md); font-size: 13px; color: var(--text-2); text-align: left; }
.day:hover { background: var(--pane); }
.empty { color: var(--faint); padding: 40px; text-align: center; }
@media (max-width: 699px) {
  .content { padding: 12px 16px 24px; }
  .mh { height: 44px; font-size: 15px; }
  .day { height: 44px; font-size: 15px; }
}
</style>
