import { ref } from 'vue';
import { fetchFacets } from '../api.js';

const facets = ref({ tags: [], collaborations: [], total: 0 });
let loaded = false;

export function useFacets() {
  if (!loaded) {
    loaded = true;
    fetchFacets().then((f) => (facets.value = f)).catch(() => (loaded = false));
  }
  return { facets };
}
