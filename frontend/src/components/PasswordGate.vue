<script setup lang="ts">
import { computed, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    recipient: string
    greeting?: string
    hint?: string
    password: string
  }>(),
  {
    greeting: '',
    hint: 'Пароль это дата нашего первого свидания',
  },
)

const emit = defineEmits<{
  unlocked: []
}>()

const digits = ref('')
const shake = ref(false)
const error = ref('')

const dayDisplay = computed(() => digits.value.slice(0, 2) || 'DD')
const monthDisplay = computed(() => digits.value.slice(2, 4) || 'MM')
const yearDisplay = computed(() => digits.value.slice(4, 8) || 'YYYY')

const isDefaultGreeting = computed(() => {
  const custom = (props.greeting || '').trim()
  return !custom || /^hi,?\s*beautiful!?$/i.test(custom)
})

const displayGreeting = computed(() => {
  if (isDefaultGreeting.value) return `Hi, ${props.recipient}`
  return (props.greeting || '').trim().replace(/^hi\b/, 'Hi')
})

function press(value: string) {
  error.value = ''
  if (digits.value.length >= 8) return
  digits.value += value
  if (digits.value.length === 8) {
    if (digits.value === props.password) {
      emit('unlocked')
      return
    }
    shake.value = true
    error.value = 'Not that day. Try the first date.'
    window.setTimeout(() => {
      shake.value = false
      digits.value = ''
    }, 700)
  }
}

function backspace() {
  digits.value = digits.value.slice(0, -1)
  error.value = ''
}
</script>

<template>
  <section class="gate">
    <p class="greeting">
      <template v-if="isDefaultGreeting">
        <span class="hi">Hi, </span>
        <span class="who">{{ recipient }}</span>
      </template>
      <span v-else class="who">{{ displayGreeting }}</span>
    </p>
    <p class="hint">{{ hint }}</p>
    <div class="display" :class="{ shake }" aria-label="Password DD MM YYYY">
      <span :class="{ placeholder: digits.length < 1 }">{{ dayDisplay }}</span>
      <small>/</small>
      <span :class="{ placeholder: digits.length < 3 }">{{ monthDisplay }}</span>
      <small>/</small>
      <span class="year" :class="{ placeholder: digits.length < 5 }">{{ yearDisplay }}</span>
    </div>
    <div class="pad">
      <button v-for="n in ['1', '2', '3', '4', '5', '6', '7', '8', '9']" :key="n" type="button" @click="press(n)">
        {{ n }}
      </button>
      <button type="button" class="ghost" aria-label="Delete" @click="backspace">⌫</button>
      <button type="button" @click="press('0')">0</button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </section>
</template>

<style scoped>
.gate {
  width: min(100%, 360px);
  display: grid;
  justify-items: center;
  gap: 12px;
  text-align: center;
  z-index: 1;
  padding: 0 12px;
}

.greeting {
  margin: 0;
  font-size: clamp(2.4rem, 9vw, 3.4rem);
  color: var(--accent);
}

.hi {
  font-family: var(--font-script);
}

.who {
  font-family: var(--font-names);
  font-weight: 700;
}

.hint {
  margin: 0;
  max-width: 16em;
  line-height: 1.45;
  color: var(--muted);
}

.display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  min-height: 56px;
  padding: 0 16px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: color-mix(in srgb, var(--surface) 80%, transparent);
  font-size: 1.35rem;
  letter-spacing: 0.12em;
  font-variant-numeric: tabular-nums;
}

.display span {
  min-width: 2ch;
}

.year {
  min-width: 4ch;
}

.placeholder {
  color: var(--muted);
}

.pad {
  display: grid;
  grid-template-columns: repeat(3, 72px);
  gap: 14px;
  justify-content: center;
  margin-top: 8px;
}

.pad button {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  border: 1px solid var(--line);
  background: color-mix(in srgb, var(--surface) 80%, transparent);
  font-size: 1.2rem;
}

.ghost {
  color: var(--muted);
}

.shake {
  animation: shake 420ms ease;
}

.error {
  color: var(--accent);
}

@keyframes shake {
  25% {
    transform: translateX(-6px);
  }
  75% {
    transform: translateX(6px);
  }
}
</style>
