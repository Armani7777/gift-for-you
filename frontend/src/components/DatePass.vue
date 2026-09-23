<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import CuteBears from '@/components/CuteBears.vue'
import { formatPrettyDate, formatTime } from '@/services/share'

const props = defineProps<{
  recipient: string
  sender: string
  date?: string
  time?: string | null
  place?: string
  extras?: string
}>()

const now = ref(Date.now())
let tick: number | null = null

onMounted(() => {
  tick = window.setInterval(() => {
    now.value = Date.now()
  }, 1000)
})

onUnmounted(() => {
  if (tick) window.clearInterval(tick)
})

const countdown = computed(() => {
  if (!props.date) return ''
  const clock = (props.time || '19:00').slice(0, 5)
  const target = new Date(`${props.date}T${clock}:00`).getTime()
  const diff = target - now.value
  if (diff <= 0) return 'It’s today'
  const days = Math.floor(diff / 86_400_000)
  const hours = Math.floor((diff % 86_400_000) / 3_600_000)
  const minutes = Math.floor((diff % 3_600_000) / 60_000)
  const seconds = Math.floor((diff % 60_000) / 1000)
  const pad = (value: number) => String(value).padStart(2, '0')
  const dayLabel = days === 1 ? 'Day' : 'Days'
  return `${days} ${dayLabel} ${pad(hours)}:${pad(minutes)}:${pad(seconds)}`
})
</script>

<template>
  <article class="pass">
    <div class="stub">
      <CuteBears scene="pass" />
      <p>For two</p>
    </div>
    <div class="details">
      <p class="eyebrow">Date pass</p>
      <dl>
        <div>
          <dt>When</dt>
          <dd>{{ date ? formatPrettyDate(date) : 'A little later' }}</dd>
        </div>
        <div>
          <dt>Time</dt>
          <dd>{{ time ? formatTime(time) : 'We’ll see' }}</dd>
        </div>
        <div v-if="place">
          <dt>Where</dt>
          <dd>{{ place }}</dd>
        </div>
        <div v-if="extras">
          <dt>Then</dt>
          <dd>{{ extras }}</dd>
        </div>
        <div>
          <dt>With</dt>
          <dd>{{ recipient }} & {{ sender }}</dd>
        </div>
      </dl>
    </div>
  </article>
  <p v-if="countdown" class="count">Starts in <strong>{{ countdown }}</strong></p>
</template>

<style scoped>
.pass {
  width: 100%;
  display: grid;
  grid-template-columns: 108px 1fr;
  border-radius: 22px;
  overflow: hidden;
  background: color-mix(in srgb, var(--surface) 92%, white);
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
  text-align: left;
}

.stub {
  display: grid;
  place-items: center;
  align-content: center;
  gap: 6px;
  padding: 16px 10px;
  background: color-mix(in srgb, var(--accent-soft) 80%, white);
  color: var(--accent);
  text-align: center;
}

.stub p,
.stub small,
.eyebrow,
dt {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.62rem;
}

.details {
  padding: 16px 16px 16px 18px;
  border-left: 1px dashed var(--line);
}

.details dl {
  display: grid;
  gap: 8px;
  margin: 8px 0 0;
}

.details div {
  display: grid;
  grid-template-columns: 54px 1fr;
  gap: 8px;
  align-items: baseline;
}

dt {
  color: var(--muted);
}

dd {
  margin: 0;
  font-weight: 600;
}

.count {
  margin: 0;
  color: var(--muted);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 0.78rem;
}

.count strong {
  color: var(--accent);
  letter-spacing: 0.08em;
}
</style>
