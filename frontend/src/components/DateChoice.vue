<script setup lang="ts">
import { computed, ref } from 'vue'
import { todayIso } from '@/services/dates'

const props = defineProps<{
  selected: string[]
  available: string[]
}>()

const emit = defineEmits<{
  change: [value: string[]]
}>()

const chips = computed(() => props.available.slice(0, 3))
const suggested = computed(() => new Set(chips.value))
const pickingOther = ref(false)
const otherSelected = computed(() => Boolean(props.selected[0] && !suggested.value.has(props.selected[0])))
const showPicker = computed(() => pickingOther.value || otherSelected.value)
const minDate = computed(() => todayIso())

function label(iso: string) {
  const date = new Date(`${iso}T12:00:00`)
  return {
    title: new Intl.DateTimeFormat('en-US', { weekday: 'long' }).format(date),
    sub: String(date.getDate()),
  }
}

function pickSuggested(iso: string) {
  pickingOther.value = false
  emit('change', [iso])
}

function pickOther() {
  pickingOther.value = true
  if (!otherSelected.value) emit('change', [])
}

function onCustom(event: Event) {
  const value = (event.target as HTMLInputElement).value
  emit('change', value ? [value] : [''])
}
</script>

<template>
  <div class="choices">
    <button
      v-for="iso in chips"
      :key="iso"
      type="button"
      class="chip"
      :class="{ selected: selected[0] === iso }"
      @click="pickSuggested(iso)"
    >
      <strong>{{ label(iso).title }}</strong>
      <span>{{ label(iso).sub }}</span>
    </button>
    <button type="button" class="chip other" :class="{ selected: showPicker }" @click="pickOther">
      <strong>Another day</strong>
      <span>Pick your own</span>
    </button>
    <label v-if="showPicker" class="picker">
      <span>Choose a day</span>
      <input type="date" :min="minDate" :value="selected[0] || ''" @input="onCustom" />
    </label>
  </div>
</template>

<style scoped>
.choices {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  width: 100%;
}

.chip {
  min-height: 72px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background: color-mix(in srgb, var(--surface) 80%, transparent);
  display: grid;
  align-content: center;
  gap: 2px;
  padding: 10px 8px;
  color: var(--text);
}

.chip span {
  color: var(--muted);
  font-size: 0.82rem;
}

.chip.selected {
  border-color: var(--accent);
  background: var(--accent-soft);
  color: var(--accent);
}

.chip.selected span {
  color: inherit;
  opacity: 0.8;
}

.other {
  grid-column: 1 / -1;
  min-height: 58px;
}

.picker {
  grid-column: 1 / -1;
  display: grid;
  gap: 8px;
  text-align: left;
  color: var(--muted);
  font-size: 0.82rem;
}

.picker input {
  width: 100%;
  min-height: 48px;
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 0 14px;
  background: color-mix(in srgb, var(--surface) 88%, transparent);
  color: var(--text);
  font: inherit;
}
</style>
