<script setup lang="ts">
defineProps<{
  label?: string
}>()
</script>

<template>
  <div class="phone">
    <div class="bezel">
      <div class="notch" aria-hidden="true" />
      <div class="screen">
        <slot />
      </div>
    </div>
    <p v-if="label" class="label">{{ label }}</p>
  </div>
</template>

<style scoped>
.phone {
  width: min(100%, 340px);
}

.bezel {
  background: #1c1814;
  border-radius: 36px;
  padding: 12px;
  box-shadow: var(--shadow);
}

.notch {
  width: 92px;
  height: 10px;
  border-radius: 999px;
  background: #0d0b09;
  margin: 0 auto 10px;
}

.screen {
  background: var(--bg);
  border-radius: 26px;
  overflow: hidden;
  min-height: 520px;
}

.label {
  text-align: center;
  color: var(--muted);
  font-size: 0.85rem;
}

@media (max-width: 720px) {
  .notch {
    display: none;
  }

  .bezel {
    background: transparent;
    padding: 0;
    box-shadow: none;
  }

  .screen {
    min-height: auto;
    border-radius: 24px;
  }
}
</style>
