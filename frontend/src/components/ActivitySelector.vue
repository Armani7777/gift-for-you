<script setup lang="ts">
import type { Activity } from '@/types/invitation'

const props = defineProps<{
  options: Activity[]
  selected: Array<number | string>
  multiple?: boolean
}>()

const emit = defineEmits<{
  change: [value: Array<number | string>]
}>()

function toggle(id: number | string) {
  if (props.multiple) {
    const exists = props.selected.includes(id)
    emit('change', exists ? props.selected.filter((item) => item !== id) : [...props.selected, id])
    return
  }
  emit('change', [id])
}
</script>

<template>
  <div class="activities">
    <button
      v-for="option in options"
      :key="option.id"
      type="button"
      class="option"
      :class="{ selected: selected.includes(option.id) }"
      :aria-pressed="selected.includes(option.id)"
      @click="toggle(option.id)"
    >
      <span class="icon" aria-hidden="true">{{ option.icon }}</span>
      <span>{{ option.name }}</span>
    </button>
  </div>
</template>

<style scoped>
.activities {
  display: grid;
  gap: 10px;
}

.option {
  min-height: 56px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background: var(--surface);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  text-align: left;
}

.option.selected {
  border-color: var(--accent);
  background: var(--accent-soft);
}

.icon {
  width: 28px;
  text-align: center;
}
</style>
