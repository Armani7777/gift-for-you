<script setup lang="ts">
defineProps<{
  src?: string | null
  caption?: string
  alt?: string
}>()

function onError(event: Event) {
  const image = event.target as HTMLImageElement
  image.style.display = 'none'
}
</script>

<template>
  <figure class="photo-card">
    <img v-if="src" :src="src" :alt="alt || caption || 'Invitation photo'" loading="eager" fetchpriority="high" @error="onError" />
    <div v-else class="fallback" aria-hidden="true" />
    <figcaption v-if="caption">{{ caption }}</figcaption>
  </figure>
</template>

<style scoped>
.photo-card {
  margin: 0;
  overflow: hidden;
  border-radius: 22px;
  background: var(--accent-soft);
}

img,
.fallback {
  width: 100%;
  aspect-ratio: 4 / 5;
  object-fit: cover;
}

.fallback {
  background: linear-gradient(160deg, var(--accent-soft), var(--bg-accent));
}

figcaption {
  padding: 10px 4px 0;
  color: var(--muted);
  font-size: 0.9rem;
}
</style>
