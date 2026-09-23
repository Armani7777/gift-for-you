<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

withDefaults(
  defineProps<{
    recipient: string
    sender: string
    caption?: string
    spotifyId?: string
  }>(),
  { caption: 'This is for you', spotifyId: '' },
)

const emit = defineEmits<{
  started: []
}>()

const grown = ref(false)
const leavesOn = ref(false)
const blooming = ref(false)
const spinning = ref(false)
const showCopy = ref(false)

const petalLayers = [
  { count: 4, w: 24, h: 46, curl: 78, delayBase: 0, tz: 2, cls: 'petal-bud' },
  { count: 5, w: 34, h: 58, curl: 65, delayBase: 0.25, tz: 9, cls: 'petal-core' },
  { count: 6, w: 46, h: 72, curl: 48, delayBase: 0.55, tz: 18, cls: 'petal-inner' },
  { count: 7, w: 58, h: 88, curl: 22, delayBase: 0.9, tz: 30, cls: 'petal-mid-inner' },
  { count: 8, w: 72, h: 104, curl: -5, delayBase: 1.3, tz: 44, cls: 'petal-mid' },
  { count: 9, w: 86, h: 118, curl: -25, delayBase: 1.75, tz: 60, cls: 'petal-outer' },
  { count: 10, w: 98, h: 130, curl: -48, delayBase: 2.25, tz: 76, cls: 'petal-blush' },
]

const petals = petalLayers.flatMap((layer, layerIndex) => {
  const angleStep = 360 / layer.count
  const layerOffset = layerIndex * 24
  return Array.from({ length: layer.count }, (_, index) => ({
    key: `${layerIndex}-${index}`,
    cls: layer.cls,
    w: layer.w,
    h: layer.h,
    angle: layerOffset + index * angleStep,
    curl: layer.curl,
    scale: 0.97 + ((layerIndex + index) % 5) * 0.012,
    delay: layer.delayBase + index * 0.05,
    tz: layer.tz,
    bloomDur: 2.2,
  }))
})

const sepals = Array.from({ length: 5 }, (_, index) => ({
  key: `sepal-${index}`,
  angle: index * 72,
  curl: 20 + (index % 3) * 2,
  delay: 0.3 + index * 0.06,
}))

type FallingPetal = {
  key: number
  left: number
  top: number
  w: number
  h: number
  c1: string
  c2: string
  dur: number
  delay: number
  s1: number
  s2: number
  s3: number
  s4: number
}

const falling = ref<FallingPetal[]>([])
const timers: number[] = []
let petalTick: number | null = null
let petalKey = 0

const colors: Array<[string, string]> = [
  ['#9a001d', '#3d0008'],
  ['#850018', '#2b0005'],
  ['#ad0022', '#480008'],
  ['#bf0028', '#52000c'],
]

function later(fn: () => void, ms: number) {
  timers.push(window.setTimeout(fn, ms))
}

function spawnPetal() {
  if (falling.value.length > 10) return
  const w = 10 + Math.random() * 12
  const pair = colors[Math.floor(Math.random() * colors.length)]
  const sign = () => (Math.random() > 0.5 ? 1 : -1)
  const key = ++petalKey
  const dur = 5.5 + Math.random() * 3.5
  const delay = Math.random() * 0.6
  falling.value.push({
    key,
    left: 20 + Math.random() * 60,
    top: 3 + Math.random() * 10,
    w,
    h: w * 1.3,
    c1: pair[0],
    c2: pair[1],
    dur,
    delay,
    s1: sign() * (15 + Math.random() * 25),
    s2: sign() * (10 + Math.random() * 20),
    s3: sign() * (20 + Math.random() * 30),
    s4: sign() * (10 + Math.random() * 15),
  })
  later(() => {
    falling.value = falling.value.filter((item) => item.key !== key)
  }, (dur + delay) * 1000 + 300)
}

onMounted(() => {
  emit('started')
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduced) {
    grown.value = true
    leavesOn.value = true
    blooming.value = true
    spinning.value = true
    showCopy.value = true
    return
  }

  later(() => {
    grown.value = true
  }, 80)
  later(() => {
    leavesOn.value = true
  }, 900)
  later(() => {
    blooming.value = true
  }, 2300)
  later(() => {
    spinning.value = true
  }, 4900)
  later(() => {
    showCopy.value = true
    spawnPetal()
    spawnPetal()
    petalTick = window.setInterval(spawnPetal, 2200)
  }, 5600)
})

onBeforeUnmount(() => {
  timers.forEach((id) => window.clearTimeout(id))
  if (petalTick) window.clearInterval(petalTick)
})
</script>

<template>
  <section class="finale" aria-label="A rose for you">
    <div class="vignette" />
    <div class="spotlight" />
    <div class="ambient" :class="{ visible: blooming }" />

    <div class="scene">
      <div class="rose-wrapper" :class="{ rotating: spinning }">
        <div class="stem-group">
          <div class="stem" :class="{ grow: grown }">
            <div class="stem-highlight" />
          </div>
          <div class="thorn thorn-1" />
          <div class="thorn thorn-2" />
          <div class="leaf leaf-left" :class="{ visible: leavesOn }">
            <div class="leaf-vein" />
          </div>
          <div class="leaf leaf-right" :class="{ visible: leavesOn }">
            <div class="leaf-vein" />
          </div>
        </div>

        <div class="calyx" :class="{ visible: blooming }">
          <div
            v-for="sepal in sepals"
            :key="sepal.key"
            class="sepal"
            :style="{
              '--sepal-angle': sepal.angle + 'deg',
              '--sepal-curl': sepal.curl + 'deg',
              '--sepal-delay': sepal.delay + 's',
            }"
          />
        </div>

        <div class="rose-head" :class="{ blooming }">
          <div class="rose-glow" />
          <div class="rose-glow-inner" />
          <div
            v-for="petal in petals"
            :key="petal.key"
            class="petal"
            :class="petal.cls"
            :style="{
              width: petal.w + 'px',
              height: petal.h + 'px',
              '--angle': petal.angle + 'deg',
              '--curl': petal.curl + 'deg',
              '--scale': petal.scale,
              '--delay': petal.delay + 's',
              '--tz': petal.tz + 'px',
              '--bloom-dur': petal.bloomDur + 's',
            }"
          />
        </div>
      </div>
    </div>

    <div class="copy" :class="{ visible: showCopy }">
      <h2 class="caption">{{ caption }}</h2>
      <div class="names-space" aria-hidden="true" />
      <div class="extra">
        <slot />
      </div>
    </div>

    <iframe
      v-if="spotifyId"
      class="spotify"
      :src="`https://open.spotify.com/embed/track/${spotifyId}?utm_source=generator&theme=0`"
      allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
      loading="eager"
      title="Background song"
    />

    <div
      v-for="petal in falling"
      :key="petal.key"
      class="falling-petal"
      :style="{
        left: petal.left + 'vw',
        top: petal.top + 'vh',
        '--fp-w': petal.w + 'px',
        '--fp-h': petal.h + 'px',
        '--fp-c1': petal.c1,
        '--fp-c2': petal.c2,
        '--f-dur': petal.dur + 's',
        '--f-delay': petal.delay + 's',
        '--s1': petal.s1 + 'px',
        '--s2': petal.s2 + 'px',
        '--s3': petal.s3 + 'px',
        '--s4': petal.s4 + 'px',
      }"
    />
  </section>
</template>

<style scoped>
.finale {
  min-height: 100dvh;
  width: 100%;
  display: grid;
  place-items: center;
  align-content: center;
  gap: 8px;
  background: radial-gradient(ellipse at 50% 75%, #120105 0%, #050002 55%, #000 100%);
  color: #f7e7ea;
  text-align: center;
  overflow: hidden;
  position: relative;
  padding:
    max(24px, env(safe-area-inset-top))
    20px
    max(28px, env(safe-area-inset-bottom));
}

.vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center, transparent 35%, rgba(0, 0, 0, 0.72) 100%);
  pointer-events: none;
  z-index: 2;
}

.spotlight,
.ambient {
  position: absolute;
  left: 50%;
  top: 34%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  pointer-events: none;
}

.spotlight {
  width: 85vw;
  height: 70vh;
  background: radial-gradient(circle, rgba(255, 30, 80, 0.06) 0%, transparent 70%);
  filter: blur(50px);
}

.ambient {
  width: 420px;
  height: 420px;
  background: radial-gradient(circle, rgba(255, 30, 60, 0.1) 0%, transparent 65%);
  opacity: 0;
  transition: opacity 3s ease;
  z-index: 1;
}

.ambient.visible {
  opacity: 1;
}

.scene {
  perspective: 1200px;
  perspective-origin: 50% 35%;
  width: min(100%, 340px);
  height: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3;
}

.rose-wrapper,
.stem-group,
.calyx,
.rose-head,
.sepal,
.petal {
  transform-style: preserve-3d;
}

.rose-wrapper {
  position: relative;
  width: 300px;
  height: 480px;
  transform: rotateX(-22deg) rotateY(0deg);
}

.rose-wrapper.rotating {
  animation: rotateRose 28s linear infinite;
}

.stem-group {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 10px;
  height: 250px;
  margin-left: -5px;
}

.stem {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 0;
  background: linear-gradient(to top, #092e12 0%, #114c23 30%, #1a6f35 70%, #114c23 100%);
  border-radius: 5px;
  overflow: hidden;
  transition: height 2.2s cubic-bezier(0.22, 1, 0.36, 1);
}

.stem.grow {
  height: 100%;
}

.stem-highlight {
  position: absolute;
  top: 0;
  left: 1px;
  width: 2.5px;
  height: 100%;
  background: linear-gradient(to bottom, transparent, rgba(150, 255, 180, 0.15), transparent);
}

.thorn {
  position: absolute;
  width: 11px;
  height: 6px;
  opacity: 0;
  transition: opacity 0.5s ease 0.4s;
}

.thorn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #1a6f35, #092e12);
  clip-path: polygon(0% 85%, 100% 50%, 30% 0%);
}

.thorn-1 {
  right: -9px;
  bottom: 65%;
  transform: scaleX(-1);
}

.thorn-2 {
  left: -9px;
  bottom: 42%;
}

.stem.grow ~ .thorn {
  opacity: 0.75;
}

.leaf {
  position: absolute;
  width: 52px;
  height: 25px;
  opacity: 0;
  transition: opacity 0.6s ease, transform 1.1s cubic-bezier(0.34, 1.45, 0.64, 1);
}

.leaf::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(160deg, #2a944e 0%, #1a6f35 40%, #092e12 100%);
  border-radius: 2px 65% 2px 65%;
}

.leaf-vein {
  position: absolute;
  width: 60%;
  height: 1px;
  background: rgba(150, 255, 180, 0.12);
  top: 48%;
  left: 20%;
}

.leaf-left {
  left: -52px;
  bottom: 56%;
  transform-origin: right center;
  transform: rotate(35deg) scale(0);
}

.leaf-left::before {
  border-radius: 65% 2px 65% 2px;
}

.leaf-right {
  left: 10px;
  bottom: 38%;
  transform-origin: left center;
  transform: rotate(-35deg) scale(0);
}

.leaf.visible {
  opacity: 1;
}

.leaf-left.visible {
  transform: rotate(15deg) scale(1);
}

.leaf-right.visible {
  transform: rotate(-15deg) scale(1);
}

.calyx {
  position: absolute;
  bottom: 242px;
  left: 50%;
  width: 0;
  height: 0;
}

.sepal {
  position: absolute;
  bottom: -4px;
  left: 50%;
  width: 14px;
  height: 32px;
  transform-origin: 50% 100%;
  background: linear-gradient(to top, #092e12 0%, #15582b 40%, #299c4c 100%);
  border-radius: 50% 50% 10% 10% / 80% 80% 20% 20%;
  clip-path: polygon(10% 100%, 0% 30%, 50% 0%, 100% 30%, 90% 100%);
  opacity: 0;
  transform: translateX(-50%) rotateY(var(--sepal-angle, 0deg)) rotateX(60deg) scale(0.5);
  transition:
    transform 1.3s cubic-bezier(0.25, 1, 0.5, 1) var(--sepal-delay, 0s),
    opacity 0.5s ease var(--sepal-delay, 0s);
}

.calyx.visible .sepal {
  opacity: 0.95;
  transform: translateX(-50%) rotateY(var(--sepal-angle, 0deg)) rotateX(var(--sepal-curl, 22deg)) scale(1);
}

.rose-head {
  position: absolute;
  bottom: 245px;
  left: 50%;
  width: 0;
  height: 0;
  z-index: 10;
}

.rose-glow,
.rose-glow-inner {
  position: absolute;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  pointer-events: none;
  z-index: -1;
}

.rose-glow {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(160, 5, 30, 0.18) 0%, transparent 65%);
  transition: opacity 3.5s ease;
}

.rose-glow-inner {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(180, 40, 60, 0.15) 0%, transparent 65%);
  transition: opacity 2s ease 0.8s;
}

.rose-head.blooming .rose-glow,
.rose-head.blooming .rose-glow-inner {
  opacity: 1;
}

.petal {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform-origin: 50% 100%;
  opacity: 0.002;
  border-radius: 50% 50% 35% 35% / 45% 45% 55% 55%;
  transform: translateX(-50%) rotateY(var(--angle, 0deg)) translateZ(0) rotateX(90deg) scale(0.1);
  transition:
    transform var(--bloom-dur, 2.4s) ease-in-out var(--delay, 0s),
    opacity 0.7s ease var(--delay, 0s);
}

.rose-head.blooming .petal {
  opacity: 1;
  transform:
    translateX(-50%)
    rotateY(var(--angle, 0deg))
    translateZ(var(--tz, 0px))
    rotateX(var(--curl, 30deg))
    scale(var(--scale, 1));
}

.petal-bud {
  background: linear-gradient(to bottom, #3d0008 0%, #220003 40%, #100001 75%, #040000 100%);
}

.petal-core {
  background: linear-gradient(to bottom, #52000c 0%, #350005 40%, #1a0002 75%, #080000 100%);
}

.petal-inner {
  background: linear-gradient(to bottom, #6d0012 0%, #480008 40%, #250003 75%, #0c0000 100%);
}

.petal-mid-inner {
  background: linear-gradient(to bottom, #850018 0%, #5c000d 40%, #310004 75%, #120000 100%);
}

.petal-mid {
  background: linear-gradient(to bottom, #9a001d 0%, #6e0011 40%, #3b0005 75%, #160000 100%);
}

.petal-outer {
  background: linear-gradient(to bottom, #ad0022 0%, #7e0014 40%, #440007 75%, #1a0001 100%);
}

.petal-blush {
  background: linear-gradient(to bottom, #bf0028 0%, #8e0018 40%, #4e0008 75%, #1e0001 100%);
}

.falling-petal {
  position: absolute;
  width: var(--fp-w, 13px);
  height: var(--fp-h, 17px);
  background: radial-gradient(ellipse at 40% 30%, var(--fp-c1, #9a001d), var(--fp-c2, #3d0008) 75%);
  border-radius: 50% 50% 45% 55% / 60% 60% 40% 40%;
  opacity: 0;
  pointer-events: none;
  z-index: 5;
  animation: fallSway var(--f-dur, 7s) linear forwards;
  animation-delay: var(--f-delay, 0s);
}

.copy {
  z-index: 6;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 1.2s ease, transform 1.2s ease;
}

.copy.visible {
  opacity: 1;
  transform: none;
}

.caption {
  margin: 0;
  font-family: var(--font-serif);
  font-weight: 500;
  font-style: italic;
  font-size: clamp(1.7rem, 6vw, 2.3rem);
}

.names-space {
  height: clamp(2.4rem, 7vw, 3.2rem);
  margin: 8px 0 0;
}

.extra {
  margin-top: 10px;
}

.spotify {
  width: min(100%, 360px);
  height: 80px;
  border: 0;
  border-radius: 16px;
  z-index: 6;
}

@keyframes rotateRose {
  from {
    transform: rotateX(-22deg) rotateY(0deg);
  }
  to {
    transform: rotateX(-22deg) rotateY(360deg);
  }
}

@keyframes fallSway {
  0% {
    opacity: 0;
    transform: translateX(0) translateY(0) rotate(0deg) scale(1);
  }
  8% {
    opacity: 0.85;
  }
  50% {
    transform: translateX(var(--s2, -25px)) translateY(48vh) rotate(160deg) scale(0.88);
  }
  100% {
    opacity: 0;
    transform: translateX(var(--s4, 10px)) translateY(108vh) rotate(390deg) scale(0.55);
  }
}

@media (max-width: 480px) {
  .scene {
    height: 400px;
  }

  .rose-wrapper {
    transform: rotateX(-22deg) scale(0.82);
  }

  .rose-wrapper.rotating {
    animation-name: rotateRoseSmall;
  }
}

@keyframes rotateRoseSmall {
  from {
    transform: rotateX(-22deg) rotateY(0deg) scale(0.82);
  }
  to {
    transform: rotateX(-22deg) rotateY(360deg) scale(0.82);
  }
}

@media (prefers-reduced-motion: reduce) {
  .rose-wrapper.rotating,
  .falling-petal,
  .stem,
  .leaf,
  .sepal,
  .petal {
    animation: none;
    transition: none;
  }

  .stem {
    height: 100%;
  }

  .leaf,
  .sepal,
  .petal,
  .copy {
    opacity: 1;
  }
}
</style>
