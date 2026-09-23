<script setup lang="ts">
import { assetUrl } from '@/services/assets'

withDefaults(
  defineProps<{
    scene?: 'hug' | 'yay' | 'heart' | 'pass'
  }>(),
  { scene: 'hug' },
)

const sources: Record<string, string> = {
  hug: assetUrl('art/bears-hug.png'),
  yay: assetUrl('art/bear-yay.png'),
  heart: assetUrl('art/bear-heart.png'),
  pass: assetUrl('art/bear-heart.png'),
}
</script>

<template>
  <div class="bears" :class="scene" aria-hidden="true">
    <img :src="sources[scene]" alt="" decoding="async" fetchpriority="high" />
  </div>
</template>

<style scoped>
.bears {
  width: min(100%, 280px);
  min-height: 168px;
  margin: 0 auto;
}

.bears img {
  width: 100%;
  height: auto;
  display: block;
  mix-blend-mode: multiply;
}

.yay {
  width: min(100%, 220px);
}

.pass {
  width: 76px;
  height: 76px;
  overflow: hidden;
  border-radius: 16px;
}

.pass img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 50% 40%;
  transform: scale(1.45);
  transform-origin: 50% 42%;
  mix-blend-mode: multiply;
}
</style>
