<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Button from '@/components/Button.vue'
</script>

<template>
  <main class="page-shell missing">
    <h1 class="display">This page drifted away.</h1>
    <p class="muted">The invitation you’re looking for may have been moved or never existed.</p>
    <RouterLink to="/">
      <Button>Back home</Button>
    </RouterLink>
  </main>
</template>

<style scoped>
.missing {
  min-height: 100dvh;
  display: grid;
  place-content: center;
  text-align: center;
  gap: 16px;
  justify-items: center;
}

.display {
  font-size: 2.4rem;
  max-width: 12ch;
}
</style>
