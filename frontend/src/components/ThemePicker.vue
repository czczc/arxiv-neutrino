<script setup>
import { LIGHT_THEMES, useTheme } from '../composables/useTheme.js';
const { prefs, setAppearance, setLight } = useTheme();
const modes = [{ id: 'light', label: 'Light' }, { id: 'dark', label: 'Dark' }, { id: 'system', label: 'Auto' }];
</script>

<template>
  <div class="theme">
    <div class="seg">
      <button v-for="m in modes" :key="m.id" :class="{ on: prefs.appearance === m.id }" @click="setAppearance(m.id)">{{ m.label }}</button>
    </div>
    <div class="swatches" :class="{ dim: prefs.appearance === 'dark' }" title="Light palette">
      <button v-for="t in LIGHT_THEMES" :key="t.id" class="sw" :class="{ on: prefs.light === t.id }" :style="{ background: t.swatch, '--sw': t.accent }"
              :aria-label="t.name" :title="t.name" @click="setLight(t.id); prefs.appearance === 'dark' && setAppearance('light')"></button>
    </div>
  </div>
</template>

<style scoped>
.theme { display: flex; flex-direction: column; gap: 8px; }
.seg { display: flex; border: 1px solid var(--rule-hard); border-radius: var(--r-md); overflow: hidden; }
.seg button { flex: 1; height: 26px; font-size: 11.5px; font-weight: 500; color: var(--dim); background: var(--pane); }
.seg button + button { border-left: 1px solid var(--rule-hard); }
.seg button.on { background: var(--nav-on); color: var(--ink); font-weight: 600; }
.swatches { display: flex; gap: 8px; }
.swatches.dim { opacity: 0.5; }
.sw { width: 22px; height: 22px; border-radius: 50%; border: 1px solid var(--rule-hard); position: relative; }
.sw::after { content: ""; position: absolute; inset: 6px; border-radius: 50%; background: var(--sw); }
.sw.on { box-shadow: 0 0 0 2px var(--pane), 0 0 0 4px var(--ink); }
@media (max-width: 699px) {
  .seg button { height: 40px; font-size: 14px; }
  .sw { width: 36px; height: 36px; }
  .sw::after { inset: 10px; }
}
</style>
