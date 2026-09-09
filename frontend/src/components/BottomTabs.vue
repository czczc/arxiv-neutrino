<script setup>
import { useRoute } from 'vue-router';
import Icon from './Icon.vue';
const props = defineProps({ unreadCount: Number });
const route = useRoute();
const tabs = [
  { to: '/unread', label: 'Unread', icon: 'inbox' },
  { to: '/starred', label: 'Starred', icon: 'star' },
  { to: '/archive', label: 'Archive', icon: 'archive' },
];
</script>

<template>
  <nav class="tabs">
    <router-link v-for="t in tabs" :key="t.to" :to="t.to" class="tab" :class="{ on: route.path === t.to }">
      <span class="ic"><Icon :name="t.icon" :size="22" /><span v-if="t.to === '/unread' && unreadCount" class="badge mono">{{ unreadCount }}</span></span>
      {{ t.label }}
    </router-link>
  </nav>
</template>

<style scoped>
.tabs { display: flex; height: calc(58px + env(safe-area-inset-bottom)); padding-bottom: env(safe-area-inset-bottom); border-top: 1px solid var(--rule); background: var(--pane); flex-shrink: 0; }
.tab { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px; font-size: 11px; font-weight: 500; color: var(--faint); }
.tab.on { color: var(--accent); }
.ic { position: relative; display: flex; }
.badge { position: absolute; top: -5px; right: -16px; font-size: 10px; font-weight: 600; padding: 1px 5px; border-radius: 999px; background: var(--accent); color: #fff; }
</style>
