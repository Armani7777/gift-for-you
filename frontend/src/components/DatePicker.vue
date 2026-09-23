<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  selected: string[]
  available?: string[]
  minDate?: string
  multiple?: boolean
}>()

const emit = defineEmits<{
  change: [value: string[]]
}>()

const today = new Date()
const monthCursor = defineModel<string>('month', { default: '' })

const viewDate = computed(() => {
  if (monthCursor.value) return new Date(`${monthCursor.value}-01T12:00:00`)
  const first = props.available?.[0] || props.selected[0]
  return first ? new Date(`${first}T12:00:00`) : today
})

const monthLabel = computed(() =>
  new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(viewDate.value),
)

const cells = computed(() => {
  const year = viewDate.value.getFullYear()
  const month = viewDate.value.getMonth()
  const first = new Date(year, month, 1)
  const start = first.getDay()
  const days = new Date(year, month + 1, 0).getDate()
  const items: Array<{ iso: string; day: number; enabled: boolean; selected: boolean } | null> = []
  for (let i = 0; i < start; i += 1) items.push(null)
  for (let day = 1; day <= days; day += 1) {
    const iso = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    const enabled =
      (!props.minDate || iso >= props.minDate) &&
      (!props.available || props.available.includes(iso))
    items.push({
      iso,
      day,
      enabled,
      selected: props.selected.includes(iso),
    })
  }
  return items
})

function shiftMonth(delta: number) {
  const next = new Date(viewDate.value)
  next.setMonth(next.getMonth() + delta)
  monthCursor.value = `${next.getFullYear()}-${String(next.getMonth() + 1).padStart(2, '0')}`
}

function toggle(iso: string, enabled: boolean) {
  if (!enabled) return
  if (props.multiple) {
    const next = props.selected.includes(iso)
      ? props.selected.filter((item) => item !== iso)
      : [...props.selected, iso].sort()
    emit('change', next)
    return
  }
  emit('change', [iso])
}
</script>

<template>
  <div class="calendar">
    <div class="nav">
      <button type="button" class="shift" aria-label="Previous month" @click="shiftMonth(-1)">‹</button>
      <p>{{ monthLabel }}</p>
      <button type="button" class="shift" aria-label="Next month" @click="shiftMonth(1)">›</button>
    </div>
    <div class="weekdays">
      <span v-for="(day, index) in ['S', 'M', 'T', 'W', 'T', 'F', 'S']" :key="index">{{ day }}</span>
    </div>
    <div class="grid">
      <template v-for="(cell, index) in cells" :key="index">
        <span v-if="!cell" />
        <button
          v-else
          type="button"
          class="day"
          :class="{ selected: cell.selected, disabled: !cell.enabled }"
          :disabled="!cell.enabled"
          :aria-pressed="cell.selected"
          @click="toggle(cell.iso, cell.enabled)"
        >
          {{ cell.day }}
        </button>
      </template>
    </div>
  </div>
</template>

<style scoped>
.calendar {
  display: grid;
  gap: 12px;
}

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav p {
  margin: 0;
  font-weight: 600;
}

.shift,
.day {
  border: 0;
  background: transparent;
  min-height: 44px;
  min-width: 44px;
  border-radius: 14px;
}

.weekdays,
.grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  text-align: center;
}

.weekdays {
  color: var(--muted);
  font-size: 0.75rem;
}

.day {
  color: var(--text);
}

.day.selected {
  background: var(--accent);
  color: #fff;
}

.day.disabled {
  opacity: 0.28;
  cursor: not-allowed;
}
</style>
