<script setup>
defineProps({ name: { type: String, required: true }, size: { type: [Number, String], default: 16 } });
const paths = {
  star: 'M12 3.5l2.7 5.6 6.1.8-4.5 4.3 1.1 6.1L12 17.4l-5.4 2.9 1.1-6.1L3.2 9.9l6.1-.8z',
  check: 'M4 12.5l5 5L20 6.5',
  'check-all': 'M3 12.5l5 5L18 7.5M12 17.5l2 2L22 11',
  search: 'M18 18a7 7 0 1 0-14 0 7 7 0 0 0 14 0zM20 20l-3.5-3.5',
  menu: 'M4 6h16M7 12h10M10 18h4',
  back: 'M15 5l-7 7 7 7',
  up: 'M6 15l6-6 6 6',
  down: 'M6 9l6 6 6-6',
  external: 'M7 17L17 7M9 7h8v8',
  close: 'M6 6l12 12M18 6L6 18',
  calendar: 'M4 6h16v14H4zM4 10h16M8 3v4M16 3v4',
  info: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM12 11v5M12 8v.5',
  trash: 'M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v5M14 11v5',
  inbox: 'M4 5h16v11H4zM4 16l3-4h10l3 4',
  filter: 'M3 5h18l-7 8v6l-4-2v-4z',
  moon: 'M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z',
  sun: 'M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10zM12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4',
};
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
       stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <template v-if="name === 'search'">
      <circle cx="11" cy="11" r="7" /><path d="M20 20l-3.5-3.5" />
    </template>
    <path v-else :d="paths[name]" />
  </svg>
</template>
