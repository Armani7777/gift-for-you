<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'primary' | 'ghost' | 'secondary'
    type?: 'button' | 'submit'
    disabled?: boolean
    block?: boolean
  }>(),
  {
    variant: 'primary',
    type: 'button',
    disabled: false,
    block: false,
  },
)
</script>

<template>
  <button
    :type="type"
    class="btn"
    :class="[variant, { block }]"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>

<style scoped>
.btn {
  min-height: 48px;
  padding: 0 22px;
  border-radius: 999px;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 550;
  letter-spacing: 0.01em;
  transition: transform 160ms ease, background 160ms ease, opacity 160ms ease;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn:not(:disabled):active {
  transform: scale(0.98);
}

.block {
  width: 100%;
}

.primary {
  background: var(--accent);
  color: #fff;
}

[data-theme="night"] .primary,
[data-theme="minimal"] .primary {
  color: var(--bg);
}

.ghost {
  background: transparent;
  color: var(--text);
  border-color: var(--line);
}

.secondary {
  background: var(--accent-soft);
  color: var(--accent);
}
</style>
