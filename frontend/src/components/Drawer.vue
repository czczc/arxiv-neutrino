<script setup>
const props = defineProps({ open: Boolean });
const emit = defineEmits(['close']);
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="scrim" @click="emit('close')">
      <div class="panel" @click.stop><slot /></div>
    </div>
  </Teleport>
</template>

<style scoped>
.scrim { position: fixed; inset: 0; z-index: 20; background: rgba(17, 20, 26, 0.35); display: flex; }
.panel { height: 100%; display: flex; background: var(--bg); box-shadow: 4px 0 24px rgba(0,0,0,0.15); }
.panel > :deep(*) { height: 100%; border-right: 0; }
</style>
