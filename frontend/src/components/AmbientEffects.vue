<script setup lang="ts">
function rand(seed: number) {
  const value = Math.sin(seed * 127.1 + 311.7) * 43758.5453
  return value - Math.floor(value)
}

const petals = Array.from({ length: 22 }, (_, index) => ({
  id: index,
  left: 3 + rand(index + 1) * 94,
  delay: -rand(index + 5) * 14,
  duration: 9 + rand(index + 7) * 11,
  width: 8 + rand(index + 9) * 7,
  height: 12 + rand(index + 10) * 10,
  drift: Math.round((rand(index + 3) * 2 - 1) * 120),
  sway: Math.round((rand(index + 11) * 2 - 1) * 48),
  spin: 120 + rand(index + 13) * 260,
  hue: rand(index + 17),
}))
</script>

<template>
  <div class="ambient" aria-hidden="true">
    <span
      v-for="petal in petals"
      :key="petal.id"
      class="petal"
      :style="{
        left: petal.left + '%',
        width: petal.width + 'px',
        height: petal.height + 'px',
        animationDelay: petal.delay + 's',
        animationDuration: petal.duration + 's',
        '--drift': petal.drift + 'px',
        '--sway': petal.sway + 'px',
        '--spin': petal.spin + 'deg',
        '--hue': petal.hue,
      }"
    />
  </div>
</template>

<style scoped>
.ambient {
  pointer-events: none;
  position: fixed;
  inset: 0;
  overflow: hidden;
  z-index: 0;
}

.petal {
  position: absolute;
  top: -10%;
  border-radius: 80% 0 70% 80%;
  background:
    radial-gradient(circle at 30% 25%, rgba(255, 255, 255, 0.55), transparent 42%),
    linear-gradient(
      160deg,
      color-mix(in srgb, #efe4f7 calc(70% + var(--hue) * 30%), #fff),
      color-mix(in srgb, #c9b0dc calc(45% + var(--hue) * 35%), #b89bcf)
    );
  animation-name: fall;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
  transform-origin: 50% 50%;
}

@keyframes fall {
  0% {
    transform: translate3d(0, -6vh, 0) rotate(12deg);
    opacity: 0;
  }
  10% {
    opacity: 0.85;
  }
  45% {
    transform: translate3d(var(--sway), 48vh, 0) rotate(calc(var(--spin) * 0.5));
  }
  100% {
    transform: translate3d(var(--drift), 110vh, 0) rotate(var(--spin));
    opacity: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .petal {
    animation: none;
    opacity: 0;
  }
}
</style>
