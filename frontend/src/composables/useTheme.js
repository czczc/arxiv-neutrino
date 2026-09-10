import { reactive, watch } from 'vue';

// Appearance preference, per browser. `appearance` picks light/dark/system;
// `light` picks which light palette is used whenever light applies.
// index.html applies the same rule inline before first paint to avoid a flash.
export const KEY = 'arxivnu:theme:v1';
export const LIGHT_THEMES = [
  { id: 'cool', name: 'Cool', swatch: '#f4f5f7', accent: 'oklch(0.48 0.13 250)' },
  { id: 'paper', name: 'Paper', swatch: '#fbf8f1', accent: 'oklch(0.55 0.13 55)' },
  { id: 'forest', name: 'Forest', swatch: '#f2f6f3', accent: 'oklch(0.50 0.12 155)' },
  { id: 'lavender', name: 'Lavender', swatch: '#f5f4f9', accent: 'oklch(0.52 0.16 295)' },
];
const DEFAULT = { appearance: 'system', light: 'cool' };

function load() {
  try { return { ...DEFAULT, ...JSON.parse(localStorage.getItem(KEY) || '{}') }; } catch { return { ...DEFAULT }; }
}

const prefs = reactive(load());
const darkQ = window.matchMedia('(prefers-color-scheme: dark)');

function resolved() {
  const dark = prefs.appearance === 'dark' || (prefs.appearance === 'system' && darkQ.matches);
  return dark ? 'dark' : prefs.light;
}
function apply() { document.documentElement.dataset.theme = resolved(); }

watch(prefs, () => {
  try { localStorage.setItem(KEY, JSON.stringify(prefs)); } catch { /* ignore */ }
  apply();
}, { deep: true });
darkQ.addEventListener('change', apply);
apply();

export function useTheme() {
  return {
    prefs,
    setAppearance: (a) => (prefs.appearance = a),
    setLight: (id) => (prefs.light = id),
    isDark: () => resolved() === 'dark',
  };
}
