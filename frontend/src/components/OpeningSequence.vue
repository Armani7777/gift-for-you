<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import PasswordGate from '@/components/PasswordGate.vue'

const props = withDefaults(
  defineProps<{
    recipient: string
    greeting?: string
    hint?: string
    password?: string
    showLock?: boolean
  }>(),
  {
    greeting: '',
    hint: 'Пароль это дата нашего первого свидания',
    password: '',
    showLock: false,
  },
)

const emit = defineEmits<{
  done: []
  opened: []
  bloom: []
  unlocking: []
}>()

const phase = ref<'envelope' | 'lock'>('envelope')
const opened = ref(false)
const leaving = ref(false)
const timers: number[] = []

watch(
  () => props.showLock,
  (show) => {
    if (!show) return
    leaving.value = true
    later(() => {
      phase.value = 'lock'
    }, 720)
  },
)

onMounted(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    emit('opened')
    emit('bloom')
  }
})

onUnmounted(() => {
  timers.forEach((id) => window.clearTimeout(id))
})

function later(fn: () => void, ms: number) {
  timers.push(window.setTimeout(fn, ms))
}

function openEnvelope() {
  if (opened.value) return
  opened.value = true
  emit('opened')
  later(() => emit('bloom'), 820)
}

function onUnlocked() {
  emit('unlocking')
}
</script>

<template>
  <div class="opening">
    <section v-if="phase === 'envelope'" class="stage" :class="{ leave: leaving }">
      <div class="float">
        <button type="button" class="envelope" :class="{ open: opened }" aria-label="Tap to open" @click="openEnvelope">
          <span class="shadow" />
          <span class="back" />
          <span class="paper" />
          <span class="pocket" />
          <span class="flap" />
          <span class="seal">♥</span>
        </button>
      </div>
      <p class="tap">tap to open</p>
    </section>

    <div class="reveal" :class="{ show: leaving || phase === 'lock' }">
      <div class="gate-layer">
        <PasswordGate
          v-if="password && (leaving || phase === 'lock')"
          :recipient="recipient"
          :greeting="greeting"
          :hint="hint"
          :password="password"
          @unlocked="onUnlocked"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.opening {
  min-height: 100dvh;
  width: 100%;
  display: grid;
  place-items: center;
  position: relative;
  z-index: 2;
  padding:
    max(24px, env(safe-area-inset-top))
    20px
    max(24px, env(safe-area-inset-bottom));
}

.stage {
  display: grid;
  place-items: center;
  gap: 28px;
  transition: opacity 720ms ease, transform 720ms ease;
}

.stage.leave {
  opacity: 0;
  transform: translateY(-8px);
  pointer-events: none;
}

.float {
  animation: float 4.8s ease-in-out infinite;
}

.envelope {
  width: min(78vw, 268px);
  height: 168px;
  border: 0;
  background: transparent;
  position: relative;
  perspective: 900px;
}

.shadow,
.back,
.paper,
.pocket,
.flap,
.seal {
  position: absolute;
}

.shadow {
  inset: 36px 10px -14px;
  border-radius: 20px;
  background: rgba(92, 48, 62, 0.16);
  filter: blur(14px);
}

.back {
  inset: 38px 0 0;
  border-radius: 0 0 20px 20px;
  background: #f4e6dc;
}

.paper {
  left: 22px;
  right: 22px;
  top: 48px;
  height: 92px;
  border-radius: 6px;
  background: #fffaf4;
  box-shadow: 0 8px 18px rgba(92, 48, 62, 0.08);
}

.pocket {
  inset: 70px 0 0;
  border-radius: 0 0 20px 20px;
  background: linear-gradient(180deg, #f7ebe3 0%, #eddcd0 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.flap {
  inset: 0 0 auto;
  height: 86px;
  clip-path: polygon(0 0, 100% 0, 50% 100%);
  background: linear-gradient(180deg, #fff6ef, #ecd8cc);
  transform-origin: top center;
  z-index: 3;
}

.seal {
  left: 50%;
  top: 72px;
  z-index: 4;
  width: 36px;
  height: 36px;
  margin-left: -18px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #f8e6ea;
  font-size: 0.78rem;
  background: radial-gradient(circle at 32% 28%, #d37a88, #8a3d4d);
  box-shadow: 0 6px 12px rgba(80, 24, 36, 0.2);
}

.envelope.open .flap {
  transform: rotateX(180deg);
  transition: transform 700ms cubic-bezier(0.22, 1, 0.32, 1);
}

.envelope.open .paper {
  transform: translateY(-38px);
  transition: transform 720ms cubic-bezier(0.22, 1, 0.32, 1) 140ms;
}

.envelope.open .seal {
  opacity: 0;
  transform: scale(0.8);
  transition: opacity 240ms ease, transform 240ms ease;
}

.tap {
  font-family: var(--font-script);
  font-size: 1.7rem;
  color: var(--muted);
  margin: 0;
}

.reveal {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  opacity: 0;
  pointer-events: none;
  transition: opacity 720ms ease;
}

.reveal.show {
  opacity: 1;
  pointer-events: auto;
}

.gate-layer {
  z-index: 1;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-11px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .float {
    animation: none;
  }
  .envelope.open .flap,
  .envelope.open .paper {
    transition: none;
  }
}
</style>
