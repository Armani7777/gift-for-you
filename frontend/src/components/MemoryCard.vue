<script setup lang="ts">
defineProps<{
  title: string
  description?: string
  imageUrl?: string | null
}>()

function onError(event: Event) {
  const image = event.target as HTMLImageElement
  image.style.opacity = '0'
}
</script>

<template>
  <article class="memory">
    <div class="image">
      <img v-if="imageUrl" :src="imageUrl" :alt="title" loading="eager" decoding="sync" fetchpriority="high" @error="onError" />
    </div>
    <div class="copy">
      <h3>{{ title }}</h3>
      <p v-if="description">{{ description }}</p>
    </div>
  </article>
</template>

<style scoped>
.memory {
  min-width: 100%;
  scroll-snap-align: center;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 24px;
  overflow: hidden;
}

.image {
  aspect-ratio: 5 / 4;
  background: linear-gradient(160deg, var(--accent-soft), var(--bg-accent));
}

img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.copy {
  padding: 18px 18px 20px;
}

h3 {
  margin: 0 0 6px;
  font-family: var(--font-serif);
  font-size: 1.35rem;
  font-weight: 500;
}

p {
  margin: 0;
  color: var(--muted);
}
</style>
