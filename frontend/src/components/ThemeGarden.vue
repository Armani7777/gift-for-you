<script setup lang="ts">
export interface GardenFlower {
  id: number
  x: number
  y: number
  size: number
  delay: number
  rot: number
  spin: number
  src: string
}

defineProps<{
  flowers: GardenFlower[]
}>()
</script>

<template>
  <div class="garden" aria-hidden="true">
    <img
      v-for="flower in flowers"
      :key="flower.id"
      class="bloom"
      :src="flower.src"
      alt=""
      :style="{
        '--x': flower.x,
        '--y': flower.y,
        '--s': flower.size + 'px',
        '--d': flower.delay + 's',
        '--rot': flower.rot + 'deg',
        '--spin': flower.spin + 'deg',
      }"
    />
  </div>
</template>

<style scoped>
.garden {
  position: absolute;
  inset: 0;
  overflow: hidden;
  background: #f4ecf8;
}

.bloom {
  position: absolute;
  left: 50%;
  top: 50%;
  width: var(--s);
  height: var(--s);
  object-fit: contain;
  mix-blend-mode: multiply;
  transform: translate(-50%, -50%) rotate(0deg) scale(0.08);
  opacity: 0;
  animation: swirl-out 1.15s cubic-bezier(0.14, 0.82, 0.18, 1) forwards;
  animation-delay: var(--d);
  pointer-events: none;
}

@keyframes swirl-out {
  0% {
    left: 50%;
    top: 50%;
    opacity: 0;
    transform: translate(-50%, -50%) rotate(0deg) scale(0.06);
  }
  18% {
    opacity: 1;
  }
  100% {
    left: calc(var(--x) * 1%);
    top: calc(var(--y) * 1%);
    opacity: 1;
    transform: translate(-50%, -50%) rotate(calc(var(--rot) + var(--spin))) scale(1);
  }
}

@media (prefers-reduced-motion: reduce) {
  .bloom {
    animation: none;
    left: calc(var(--x) * 1%);
    top: calc(var(--y) * 1%);
    opacity: 1;
    transform: translate(-50%, -50%) rotate(var(--rot)) scale(1);
  }
}
</style>
