<script setup lang="ts">
defineProps<{
  padded?: boolean
}>()
</script>

<template>
  <section class="card" :class="{ padded }">
    <slot />
  </section>
</template>

<style scoped>
.card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  backdrop-filter: blur(16px);
}

.padded {
  padding: 28px 24px;
}
</style>
