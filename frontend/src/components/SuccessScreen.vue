<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <section class="success">
    <div class="mark" aria-hidden="true">♥</div>
    <h2 class="display">{{ title }}</h2>
    <p v-if="subtitle" class="muted">{{ subtitle }}</p>
    <slot />
  </section>
</template>

<style scoped>
.success {
  text-align: center;
  display: grid;
  gap: 12px;
  justify-items: center;
}

.mark {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 1.6rem;
  animation: rise 700ms ease;
}

.display {
  font-size: clamp(2rem, 7vw, 3rem);
}

@keyframes rise {
  from {
    transform: scale(0.86);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
