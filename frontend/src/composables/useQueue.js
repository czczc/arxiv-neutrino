import { ref } from 'vue';

// The ordered list of ids the phone reader walks through with "Read · next".
// Set by the inbox when a row is tapped; empty on a direct link.
const ids = ref([]);
export function useQueue() {
  return { ids, set: (list) => (ids.value = list) };
}
