<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { normalizeClock } from '@/services/dates'
import { formatTime } from '@/services/share'

const props = defineProps<{
  times: string[]
  selected?: string | null
}>()

const emit = defineEmits<{
  change: [value: string]
}>()

const hour = ref((props.selected || '19:00').slice(0, 2))
const minute = ref((props.selected || '19:00').slice(3, 5))

const hours = Array.from({ length: 24 }, (_, index) => String(index).padStart(2, '0'))
const minutes = computed(() => {
  const base = ['00', '15', '30', '45']
  if (minute.value && !base.includes(minute.value)) return [...base, minute.value].sort()
  return base
})

watch(
  () => props.selected,
  (value) => {
    if (!value) return
    hour.value = value.slice(0, 2)
    minute.value = value.slice(3, 5)
  },
)

function applyCustom() {
  const next = normalizeClock(`${hour.value}:${minute.value}`)
  if (next) emit('change', next)
}
</script>

<template>
  <div class="times">
    <button
      v-for="time in times"
      :key="time"
      type="button"
      class="chip"
      :class="{ selected: selected === time }"
      :aria-pressed="selected === time"
      @click="emit('change', time)"
    >
      {{ formatTime(time) }}
    </button>
    <label class="custom">
      <span>If none of these work</span>
      <div class="clock">
        <select v-model="hour" aria-label="Hour" @change="applyCustom">
          <option v-for="item in hours" :key="item" :value="item">{{ item }}</option>
        </select>
        <span>:</span>
        <select v-model="minute" aria-label="Minutes" @change="applyCustom">
          <option v-for="item in minutes" :key="item" :value="item">{{ item }}</option>
        </select>
      </div>
    </label>
  </div>
</template>

<style scoped>
.times {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.chip {
  min-height: 48px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: var(--surface);
  font-variant-numeric: tabular-nums;
}

.chip.selected {
  border-color: var(--accent);
  background: var(--accent-soft);
  color: var(--accent);
}

.custom {
  grid-column: 1 / -1;
  display: grid;
  gap: 8px;
  color: var(--muted);
  font-size: 0.92rem;
}

.clock {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 8px;
  align-items: center;
}

.clock select {
  min-height: 48px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--text);
  padding: 0 12px;
  font-variant-numeric: tabular-nums;
}
</style>
