import { ref, onUnmounted } from 'vue';

// Breakpoints shared with the CSS: <700 one pane, 700–1099 two panes, ≥1100 three.
export function useMedia() {
  const mkq = (q) => window.matchMedia(q);
  const phoneQ = mkq('(max-width: 699px)');
  const wideQ = mkq('(min-width: 1100px)');
  const isPhone = ref(phoneQ.matches);
  const isWide = ref(wideQ.matches);
  const onP = (e) => (isPhone.value = e.matches);
  const onW = (e) => (isWide.value = e.matches);
  phoneQ.addEventListener('change', onP);
  wideQ.addEventListener('change', onW);
  onUnmounted(() => { phoneQ.removeEventListener('change', onP); wideQ.removeEventListener('change', onW); });
  return { isPhone, isWide };
}
