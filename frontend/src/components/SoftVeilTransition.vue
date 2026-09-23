<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps<{
  active: boolean
}>()

const emit = defineEmits<{
  covered: []
  finished: []
}>()

const step = ref<'idle' | 'in' | 'out'>('idle')
const timers: number[] = []

function clearTimers() {
  timers.forEach((id) => window.clearTimeout(id))
  timers.length = 0
}

function later(fn: () => void, ms: number) {
  timers.push(window.setTimeout(fn, ms))
}

function play() {
  clearTimers()
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    emit('covered')
    later(() => emit('finished'), 80)
    return
  }

  step.value = 'in'
  later(() => emit('covered'), 700)
  later(() => {
    step.value = 'out'
  }, 860)
  later(() => {
    step.value = 'idle'
    emit('finished')
  }, 1680)
}

watch(
  () => props.active,
  (on) => {
    if (on) play()
    else {
      clearTimers()
      step.value = 'idle'
    }
  },
)

onBeforeUnmount(clearTimers)
</script>

<template>
  <div v-if="step !== 'idle'" class="veil" :class="step" aria-hidden="true" />
</template>

<style scoped>
.veil {
  position: fixed;
  inset: 0;
  z-index: 9999;
  pointer-events: none;
  background: var(--bg, #f4efe8);
  opacity: 0;
}

.in {
  animation: ease-in 780ms ease forwards;
}

.out {
  animation: ease-out 780ms ease forwards;
}

@keyframes ease-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes ease-out {
  from { opacity: 1; }
  to { opacity: 0; }
}

@media (prefers-reduced-motion: reduce) {
  .veil {
    display: none;
  }
}
</style>
