<script setup lang="ts">
const props = defineProps<{
  playing: boolean
}>()

const emit = defineEmits<{
  toggle: []
}>()
</script>

<template>
  <button class="disc-btn" type="button" :class="{ playing: props.playing }" aria-label="Toggle music" @click="emit('toggle')">
    <span class="halo" />
    <span class="vinyl">
      <span class="groove g1" />
      <span class="groove g2" />
      <span class="shine" />
      <span class="label">
        <span class="hole" />
      </span>
    </span>
  </button>
</template>

<style scoped>
.disc-btn {
  --disc: 64px;
  position: fixed;
  left: 12px;
  bottom: calc(12px + env(safe-area-inset-bottom));
  z-index: 12;
  width: var(--disc);
  height: var(--disc);
  border: 0;
  background: transparent;
  cursor: pointer;
  padding: 0;
  animation: float 4.8s ease-in-out infinite;
}
.halo {
  position: absolute;
  inset: -8px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(232, 196, 214, 0.4), transparent 68%);
  pointer-events: none;
}
.vinyl {
  position: relative;
  display: block;
  width: var(--disc);
  height: var(--disc);
  border-radius: 50%;
  background: repeating-radial-gradient(circle at 50% 50%, #141014 0 1px, #1f191f 2px, #141014 3px);
  box-shadow:
    0 8px 16px rgba(40, 18, 28, 0.24),
    inset 0 0 0 1px rgba(255, 230, 240, 0.1);
  overflow: hidden;
}
.playing .vinyl {
  animation: spin 3.8s linear infinite;
}
.groove {
  position: absolute;
  inset: 7px;
  border-radius: 50%;
  border: 1px solid rgba(255, 220, 230, 0.06);
  pointer-events: none;
}
.g2 { inset: 11px; }
.shine {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: linear-gradient(125deg, rgba(255, 255, 255, 0.26) 0%, transparent 30%, transparent 64%, rgba(255, 255, 255, 0.08) 100%);
  pointer-events: none;
}
.label {
  position: absolute;
  inset: 28%;
  border-radius: 50%;
  background:
    radial-gradient(circle at 50% 50%, #fff7f1 0 18%, #f3e4da 19% 100%);
  box-shadow: inset 0 0 0 1px rgba(255, 236, 228, 0.7);
}
.hole {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 18%;
  height: 18%;
  margin: -9% 0 0 -9%;
  border-radius: 50%;
  background: #efe6df;
  box-shadow: inset 0 0 0 1px rgba(90, 50, 60, 0.12);
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
@media (max-width: 720px) {
  .disc-btn {
    --disc: 54px;
    left: 8px;
    bottom: calc(8px + env(safe-area-inset-bottom));
  }
}
</style>
