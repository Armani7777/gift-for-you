<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

const emit = defineEmits<{
  opened: []
  read: []
}>()

const visible = ref(false)
const open = ref(false)
const dismissed = ref(false)
let timer: number | null = null

onMounted(() => {
  timer = window.setTimeout(() => {
    visible.value = true
  }, 1000)
})

onUnmounted(() => {
  if (timer) window.clearTimeout(timer)
  document.body.style.removeProperty('overflow')
})

function openLetter() {
  open.value = true
  document.body.style.overflow = 'hidden'
  emit('opened')
}

function closeLetter() {
  if (!open.value) return
  open.value = false
  dismissed.value = true
  document.body.style.removeProperty('overflow')
  emit('read')
}
</script>

<template>
  <div class="msg">
    <button v-if="visible && !open && !dismissed" type="button" class="toast" @click="openLetter">
      <span class="heart" aria-hidden="true">♥</span>
      <span class="copy">
        <strong>1 new message</strong>
        <em>Tap to open</em>
      </span>
    </button>

    <Teleport to="body">
      <div v-if="open" class="overlay" @click.self="closeLetter">
        <article class="letter" role="dialog" aria-labelledby="date-message-title">
          <p id="date-message-title" class="eyebrow">A message for you</p>
          <p class="body">
            I think of you in the most random moments. Sometimes it's when I see something funny and immediately think, "I have to show you this."
          </p>
          <p class="body">
            You've become part of the little things in my day - a thought before I sleep, a smile when I check my phone, a random "I wonder what you're doing right now."
          </p>
          <p class="body">
            I don't have to try to think of you. You just appear.
          </p>
          <p class="body">
            And maybe that's how I know you've become someone special to me - not because I think about you every second, but because somehow, you keep finding your way into my ordinary moments.
          </p>
          <button type="button" class="done" @click="closeLetter">Close</button>
        </article>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.msg {
  width: min(360px, 100%);
  min-height: 64px;
  margin: 0 auto 8px;
}
.toast {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid rgba(190, 140, 160, 0.22);
  background: rgba(255, 250, 247, 0.92);
  border-radius: 18px;
  padding: 12px 16px;
  cursor: pointer;
  box-shadow: 0 10px 28px rgba(110, 61, 82, 0.08);
  animation: arrive 0.7s ease both, glow 2.4s ease-in-out 0.7s infinite;
}
.heart {
  flex: 0 0 auto;
  color: #c9848e;
  font-size: 1.05rem;
  line-height: 1;
}
.copy {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}
.copy strong {
  font-family: var(--font-sans);
  font-size: 0.95rem;
  font-weight: 500;
  color: #4a3040;
}
.copy em {
  font-family: var(--font-sans);
  font-style: normal;
  font-size: 0.75rem;
  color: #8a6574;
}
.overlay {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgba(52, 32, 40, 0.38);
  backdrop-filter: blur(8px);
}
.letter {
  width: min(420px, 100%);
  max-height: min(80dvh, 640px);
  overflow: auto;
  border: 1px solid rgba(190, 140, 160, 0.2);
  background: linear-gradient(180deg, #fffaf6, #f7ece6);
  border-radius: 24px;
  padding: 26px 24px 20px;
  text-align: left;
  box-shadow: 0 24px 48px rgba(70, 32, 46, 0.22);
  animation: unfold 0.4s ease both;
  display: grid;
  gap: 12px;
}
.eyebrow {
  margin: 0;
  font-family: var(--font-sans);
  font-size: 0.72rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #b08998;
}
.body {
  margin: 0;
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.18rem;
  line-height: 1.55;
  color: #4a3040;
}
.done {
  justify-self: center;
  margin-top: 6px;
  border: 0;
  border-radius: 999px;
  padding: 10px 22px;
  background: #6e3d52;
  color: #fffaf7;
  cursor: pointer;
}
@keyframes arrive {
  from { opacity: 0; transform: translateY(10px) scale(0.98); }
  to { opacity: 1; transform: none; }
}
@keyframes glow {
  50% { box-shadow: 0 10px 28px rgba(110, 61, 82, 0.08), 0 0 0 6px rgba(201, 132, 142, 0.08); }
}
@keyframes unfold {
  from { opacity: 0; transform: translateY(10px) scale(0.97); }
  to { opacity: 1; transform: none; }
}
</style>
