<script setup lang="ts">
import { onUnmounted, ref, watch } from 'vue'

export type FinaleNotePayload = {
  text: string
  blob: Blob | null
  kind: 'text' | 'voice' | 'video'
}

const props = defineProps<{
  senderName: string
  mode?: 'demo' | 'live'
}>()

const emit = defineEmits<{
  sent: [payload: FinaleNotePayload]
}>()

const kind = ref<'text' | 'voice' | 'video'>('text')
const text = ref('')
const previewUrl = ref('')
const blob = ref<Blob | null>(null)
const recording = ref(false)
const seconds = ref(0)
const sent = ref(false)
const sending = ref(false)
const cameraError = ref('')
const cameraReady = ref(false)

const liveVideo = ref<HTMLVideoElement | null>(null)
let mediaStream: MediaStream | null = null
let recorder: MediaRecorder | null = null
let chunks: Blob[] = []
let timer: number | null = null

const maxSeconds = 15

function format(n: number) {
  return `0:${String(n).padStart(2, '0')}`
}

function stopCamera() {
  mediaStream?.getTracks().forEach((track) => track.stop())
  mediaStream = null
  if (liveVideo.value) liveVideo.value.srcObject = null
  cameraReady.value = false
}

async function choose(next: 'text' | 'voice' | 'video') {
  if (recording.value) return
  kind.value = next
  clearClip()
  stopCamera()
  cameraError.value = ''
}

function startTimer() {
  seconds.value = 0
  timer = window.setInterval(() => {
    seconds.value += 1
    if (seconds.value >= maxSeconds) stop()
  }, 1000)
}

function stopTimer() {
  if (timer) window.clearInterval(timer)
  timer = null
}

async function start() {
  if (recording.value || kind.value === 'text') return
  cameraError.value = ''
  const constraints =
    kind.value === 'video'
      ? { audio: true, video: { facingMode: 'user', width: { ideal: 720 }, height: { ideal: 720 } } }
      : { audio: true }
  try {
    stopCamera()
    mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
    if (kind.value === 'video' && liveVideo.value) {
      liveVideo.value.srcObject = mediaStream
      await liveVideo.value.play().catch(() => undefined)
      cameraReady.value = true
    }
    chunks = []
    const mime =
      kind.value === 'video'
        ? MediaRecorder.isTypeSupported('video/webm;codecs=vp9,opus')
          ? 'video/webm;codecs=vp9,opus'
          : 'video/webm'
        : MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
          ? 'audio/webm;codecs=opus'
          : 'audio/webm'
    recorder = new MediaRecorder(mediaStream, { mimeType: mime })
    recorder.ondataavailable = (event) => {
      if (event.data.size) chunks.push(event.data)
    }
    recorder.onstop = () => {
      blob.value = new Blob(chunks, { type: recorder?.mimeType || mime })
      previewUrl.value = URL.createObjectURL(blob.value)
      stopCamera()
    }
    recorder.start()
    recording.value = true
    startTimer()
  } catch {
    cameraError.value = kind.value === 'video' ? 'Allow the camera to record.' : 'Allow the microphone to record.'
  }
}

function stop() {
  if (!recording.value) return
  recorder?.stop()
  recording.value = false
  stopTimer()
}

function clearClip() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
  blob.value = null
  seconds.value = 0
}

async function send() {
  if (sending.value) return
  if (kind.value === 'text' && !text.value.trim()) return
  if (kind.value !== 'text' && !blob.value && !text.value.trim()) return
  sending.value = true
  emit('sent', { text: text.value.trim(), blob: blob.value, kind: kind.value })
  sent.value = true
  sending.value = false
}

onUnmounted(() => {
  stop()
  stopCamera()
  stopTimer()
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})

watch(liveVideo, (el) => {
  if (el && mediaStream) el.srcObject = mediaStream
})
</script>

<template>
  <section class="note">
    <p class="from">For {{ senderName }}</p>

    <div v-if="!sent" class="modes">
      <button type="button" :class="{ on: kind === 'text' }" :disabled="recording" @click="choose('text')">Text</button>
      <button type="button" :class="{ on: kind === 'video' }" :disabled="recording" @click="choose('video')">Video circle</button>
      <button type="button" :class="{ on: kind === 'voice' }" :disabled="recording" @click="choose('voice')">Voice</button>
    </div>

    <div v-if="!sent && kind === 'video'" class="circle-stage">
      <video v-if="previewUrl" class="circle-preview" :src="previewUrl" playsinline muted autoplay loop />
      <video v-else-if="recording || cameraReady" ref="liveVideo" class="circle-live" autoplay muted playsinline />
      <div v-else class="circle-empty">Ready when you are</div>
      <div v-if="recording" class="rec-ring" />
      <p v-if="cameraError" class="cam-err">{{ cameraError }}</p>
    </div>

    <audio v-if="!sent && kind === 'voice' && previewUrl" class="audio" :src="previewUrl" controls />

    <div v-if="!sent && kind !== 'text'" class="record-row">
      <button v-if="!recording && !previewUrl" type="button" class="rec" @click="start">
        Record {{ kind === 'video' ? 'video' : 'voice' }} · {{ maxSeconds }}s
      </button>
      <button v-else-if="recording" type="button" class="stop" @click="stop">Stop · {{ format(seconds) }}</button>
      <button v-else type="button" class="ghost" @click="clearClip()">Retake</button>
    </div>

    <textarea
      v-if="!sent"
      v-model="text"
      maxlength="400"
      rows="3"
      placeholder="Write whatever comes to mind…"
    />

    <div v-if="!sent" class="actions">
      <button type="button" class="send" :disabled="sending" @click="send">Send</button>
    </div>
    <p v-else class="thanks">Thank you.</p>
  </section>
</template>

<style scoped>
.note {
  width: min(420px, 100%);
  text-align: center;
}
.from {
  margin: 0 0 16px;
  font-family: 'Cormorant Garamond', serif;
  font-size: 2rem;
  font-weight: 700;
  color: #4a3040;
}
.modes {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}
.modes button {
  border: 1px solid rgba(190, 140, 160, 0.35);
  background: #fffaf7;
  color: #6e3d52;
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 0.78rem;
}
.modes button.on {
  background: #6e3d52;
  color: #fffaf7;
}
.circle-stage {
  position: relative;
  width: 220px;
  height: 220px;
  margin: 8px auto 12px;
}
.circle-live,
.circle-preview,
.circle-empty {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  background: #1a1014;
}
.circle-live,
.circle-preview {
  transform: scaleX(-1);
}
.circle-empty {
  display: grid;
  place-items: center;
  color: #f4e6ea;
  font-size: 0.85rem;
}
.rec-ring {
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 3px solid #e45d6b;
  animation: pulse 1s ease infinite;
  pointer-events: none;
}
.cam-err {
  position: absolute;
  inset: auto 12px 16px;
  margin: 0;
  color: #fffaf7;
  font-size: 0.78rem;
  text-shadow: 0 1px 4px #1a1014;
}
.audio {
  width: min(280px, 100%);
  margin: 8px auto 12px;
  display: block;
}
.record-row {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}
.rec,
.stop,
.ghost,
.send {
  border: 0;
  border-radius: 999px;
  padding: 10px 16px;
  cursor: pointer;
}
.rec,
.send {
  background: #6e3d52;
  color: #fffaf7;
}
.stop {
  background: #e45d6b;
  color: #fff;
}
.ghost {
  background: transparent;
  color: #8a6574;
}
textarea {
  width: 100%;
  border: 1px solid rgba(190, 140, 160, 0.28);
  border-radius: 16px;
  padding: 12px 14px;
  font: inherit;
  resize: vertical;
  background: #fffaf7;
  color: #4a3040;
}
.actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 12px;
}
.thanks {
  font-family: 'Great Vibes', cursive;
  font-size: 2rem;
  color: #6e3d52;
}
@keyframes pulse {
  50% { transform: scale(1.04); opacity: 0.7; }
}
</style>
