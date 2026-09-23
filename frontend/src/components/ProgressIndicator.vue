<script setup lang="ts">
defineProps<{
  current: number
  total: number
}>()
</script>

<template>
  <div class="progress" role="status" :aria-label="`Step ${current} of ${total}`">
    <span
      v-for="index in total"
      :key="index"
      class="dot"
      :class="{ active: index === current, done: index < current }"
    />
  </div>
</template>

<style scoped>
.progress {
  display: flex;
  gap: 7px;
  justify-content: center;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--line);
}

.dot.active,
.dot.done {
  background: linear-gradient(90deg, #e36a7a, #f0c27a);
}

.dot.active {
  width: 18px;
}
</style>
