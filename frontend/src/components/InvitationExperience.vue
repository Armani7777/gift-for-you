<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import ActivitySelector from '@/components/ActivitySelector.vue'
import AmbientEffects from '@/components/AmbientEffects.vue'
import Button from '@/components/Button.vue'
import CuteBears from '@/components/CuteBears.vue'
import ConfirmMessage from '@/components/ConfirmMessage.vue'
import DateChoice from '@/components/DateChoice.vue'
import DatePass from '@/components/DatePass.vue'
import FinaleNote from '@/components/FinaleNote.vue'
import SoftVeilTransition from '@/components/SoftVeilTransition.vue'
import MemoryCard from '@/components/MemoryCard.vue'
import MusicDisc from '@/components/MusicDisc.vue'
import OpeningSequence from '@/components/OpeningSequence.vue'
import PhotoCard from '@/components/PhotoCard.vue'
import ProgressIndicator from '@/components/ProgressIndicator.vue'
import RoseFinale from '@/components/RoseFinale.vue'
import TimePicker from '@/components/TimePicker.vue'
import type { FinaleNotePayload } from '@/components/FinaleNote.vue'
import { isTimeStillOpen, selectableDates, selectableTimes, todayIso } from '@/services/dates'
import { api, persistReply } from '@/services/api'
import { giftImageUrls, preloadGiftAssets } from '@/services/preload'
import { formatPrettyDate, formatTime } from '@/services/share'
import type { InvitationPublic } from '@/types/invitation'

const props = withDefaults(
  defineProps<{
    invitation: InvitationPublic
    mode?: 'live' | 'demo' | 'preview'
  }>(),
  { mode: 'live' },
)

type Screen =
  | 'opening'
  | 'welcome'
  | 'message'
  | 'memories'
  | 'question'
  | 'accepted'
  | 'declined'
  | 'activity'
  | 'date'
  | 'time'
  | 'confirm'
  | 'done'

const invitation = computed(() => props.invitation)
const storyScreens = computed<Screen[]>(() => {
  const screens: Screen[] = []
  if (invitation.value.show_welcome) screens.push('welcome')
  if (invitation.value.show_personal_message && (invitation.value.personal_message || invitation.value.photos.length)) {
    screens.push('message')
  }
  if (invitation.value.show_memories && invitation.value.memories.length) screens.push('memories')
  screens.push('question')
  return screens
})

const hasActivities = computed(() => invitation.value.activities.length > 0)
const hasDates = computed(() => true)

function initialScreen(): Screen {
  if (props.mode === 'preview') return storyScreens.value[0] || 'question'
  const status = invitation.value.status
  if (status === 'declined') return 'declined'
  if (status === 'confirmed') return 'done'
  if (status === 'accepted' || status === 'planning') {
    if (hasActivities.value) return 'activity'
    if (hasDates.value) return 'date'
    if (hasTimes.value) return 'time'
    return 'confirm'
  }
  return 'opening'
}

const screen = ref<Screen>(initialScreen())
const memoryIndex = ref(0)
const selectedActivities = ref<Array<number | string>>([])
const selectedDate = ref<string[]>(invitation.value.available_dates[0] ? [] : [])
const selectedTime = ref<string | null>(null)
const busy = ref(false)
const error = ref('')
const musicOn = ref(false)
const showDisc = ref(false)
const audio = ref<HTMLAudioElement | null>(null)
const noTries = ref(0)
const showNoReason = ref(false)
const declineReason = ref('')
const noOffset = ref({ x: 0, y: 0 })
const noLines = [
  'No',
  'Are you sure?',
  'Think again…',
  'Last chance',
  'Okay, wait',
  'No',
  'Are you sure?',
  'Think again…',
  'Last chance',
  'Okay, wait',
]
const noLabel = computed(() => noLines[Math.min(noTries.value, noLines.length - 1)])

const storyIndex = computed(() => Math.max(0, storyScreens.value.indexOf(screen.value)))
const availableDateValues = computed(() =>
  selectableDates(invitation.value.available_dates.map((item) => item.date)),
)
const currentMemory = computed(() => invitation.value.memories[memoryIndex.value])
const chosenDate = computed(() => selectedDate.value[0] || '')
const times = computed(() =>
  selectableTimes(
    chosenDate.value || todayIso(),
    invitation.value.available_times.map((item) => item.time),
  ),
)
const hasTimes = computed(() => times.value.length > 0)
const chosenActivityNames = computed(() =>
  invitation.value.activities
    .filter((item) => selectedActivities.value.includes(item.id))
    .map((item) => `${item.icon} ${item.name}`.trim()),
)
const chosenPlace = computed(() => chosenActivityNames.value[0] || '')
const chosenExtras = computed(() => chosenActivityNames.value.slice(1).join(' · '))

watch([chosenDate, selectedTime], () => {
  if (selectedTime.value && chosenDate.value && !isTimeStillOpen(chosenDate.value, selectedTime.value)) {
    selectedTime.value = null
  }
})

const roseMusicStarted = ref(false)
const cachedImages = giftImageUrls()
const flowerZoom = ref(false)
const showLock = ref(false)
let afterFlowerCover: (() => void) | null = null

function startFlowerZoom(action: () => void) {
  afterFlowerCover = action
  if (flowerZoom.value) {
    flowerZoom.value = false
    window.requestAnimationFrame(() => {
      flowerZoom.value = true
    })
    return
  }
  flowerZoom.value = true
}

function onFlowerCovered() {
  afterFlowerCover?.()
  afterFlowerCover = null
}

function onFlowerFinished() {
  flowerZoom.value = false
}

function onLetterBloom() {
  if (invitation.value.unlock_code) showLock.value = true
  else finishOpening()
}

function onPasswordUnlock() {
  beginMusic()
  startFlowerZoom(() => finishOpening())
}

function ensureAudio() {
  const url = invitation.value.music_url
  if (!url || audio.value) return
  audio.value = new Audio(url)
  audio.value.preload = 'auto'
  audio.value.loop = true
  audio.value.load()
}

function beginMusic() {
  if (!invitation.value.music_url) return
  showDisc.value = true
  ensureAudio()
  const player = audio.value
  if (!player) return
  const start = invitation.value.music_start_sec || 0
  if (player.currentTime < start) player.currentTime = start
  void player.play().then(() => {
    musicOn.value = true
    sessionStorage.setItem(`music:${invitation.value.public_token}`, 'on')
  }).catch(() => undefined)
}

function startRoseMusic() {
  if (roseMusicStarted.value) return
  roseMusicStarted.value = true
  if (musicOn.value) return
  beginMusic()
}

let assetsReady: Promise<unknown> = Promise.resolve()

function finishOpening() {
  void Promise.race([
    assetsReady,
    new Promise((resolve) => window.setTimeout(resolve, 1200)),
  ]).then(() => {
    go(storyScreens.value[0] || 'question')
  })
}

const hintPerfect = ref(false)
const readingMessage = ref(false)
let confirmActiveMs = 0
let confirmTimer: number | null = null
let confirmStamp = 0

function preloadImages() {
  assetsReady = preloadGiftAssets([
    ...invitation.value.memories.map((item) => item.image_url),
    ...invitation.value.photos.map((item) => item.url),
  ])
}

ensureAudio()
preloadImages()

function stopConfirmHint() {
  if (confirmTimer) window.clearInterval(confirmTimer)
  confirmTimer = null
}

function startConfirmHint() {
  stopConfirmHint()
  hintPerfect.value = false
  readingMessage.value = false
  confirmActiveMs = 0
  confirmStamp = performance.now()
  confirmTimer = window.setInterval(() => {
    const now = performance.now()
    if (!readingMessage.value) {
      confirmActiveMs += now - confirmStamp
      if (confirmActiveMs >= 5000) {
        hintPerfect.value = true
        stopConfirmHint()
      }
    }
    confirmStamp = now
  }, 200)
}

function onMessageOpened() {
  readingMessage.value = true
  confirmStamp = performance.now()
}

function onMessageRead() {
  readingMessage.value = false
  confirmStamp = performance.now()
  hintPerfect.value = true
  stopConfirmHint()
}

onMounted(async () => {
  if (props.mode === 'live') {
    try {
      await api.openInvitation(invitation.value.public_token)
    } catch {
      /* opening is best-effort */
    }
  }
})

function go(next: Screen) {
  error.value = ''
  screen.value = next
  if (next === 'confirm') startConfirmHint()
  else stopConfirmHint()
}

function continueStory() {
  const index = storyScreens.value.indexOf(screen.value)
  go(storyScreens.value[index + 1] || 'question')
}

async function answer(choice: 'accepted' | 'declined') {
  if (busy.value) return
  busy.value = true
  error.value = ''
  try {
    if (props.mode === 'live') {
      await api.submitResponse(
        invitation.value.public_token,
        choice,
        choice === 'declined' ? declineReason.value : '',
      )
    }
    if (choice === 'accepted') afterAccept()
    else go('declined')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not save your answer.'
  } finally {
    busy.value = false
  }
}

function moveNo() {
  const x = Math.round(Math.random() * 170 - 85)
  const y = Math.round(20 + Math.random() * 100)
  noOffset.value = { x, y }
}

function dodgeNo(event: Event) {
  if (showNoReason.value || busy.value) return
  event.preventDefault()
  event.stopPropagation()
  noTries.value += 1
  if (noTries.value >= 10) {
    showNoReason.value = true
    noOffset.value = { x: 0, y: 80 }
    return
  }
  moveNo()
}

function teaseNo(event: PointerEvent) {
  if (event.pointerType === 'touch' || showNoReason.value) return
  moveNo()
}

function afterAccept() {
  if (hasActivities.value) return go('activity')
  if (hasDates.value) return go('date')
  if (hasTimes.value) return go('time')
  return go('confirm')
}

function afterActivity() {
  if (!selectedActivities.value.length) {
    error.value = 'Choose what sounds good.'
    return
  }
  if (hasDates.value) return go('date')
  if (hasTimes.value) return go('time')
  return go('confirm')
}

function afterDate() {
  if (!chosenDate.value) {
    error.value = 'Please pick a day.'
    return
  }
  if (hasTimes.value) return go('time')
  return go('confirm')
}

function afterTime() {
  if (!selectedTime.value) {
    error.value = 'Please pick a time.'
    return
  }
  if (chosenDate.value && !isTimeStillOpen(chosenDate.value, selectedTime.value)) {
    error.value = 'Please pick a later time.'
    return
  }
  go('confirm')
}

function replySessionKey() {
  const key = `reply-session:${invitation.value.public_token}`
  let value = sessionStorage.getItem(key)
  if (!value) {
    value = crypto.randomUUID()
    sessionStorage.setItem(key, value)
  }
  return value
}

function replyBase() {
  return {
    session_key: replySessionKey(),
    source: props.mode === 'live' ? 'live' : 'demo',
    public_token: invitation.value.public_token,
    recipient_name: invitation.value.recipient_name,
    sender_name: invitation.value.sender_name,
    answer: 'accepted',
    activities: chosenActivityNames.value,
    selected_date: chosenDate.value,
    selected_time: selectedTime.value || '',
  }
}

async function saveAndConfirm() {
  if (busy.value) return
  busy.value = true
  error.value = ''
  go('done')
  if (props.mode !== 'preview') {
    void persistReply(replyBase()).catch(() => undefined)
  }
  if (props.mode === 'live') {
    const dateId = invitation.value.available_dates.find((item) => item.date === chosenDate.value)?.id
    void api
      .savePlan(invitation.value.public_token, {
        activity_ids: selectedActivities.value.map((id) => Number(id)).filter((id) => Number.isFinite(id)),
        date_id: typeof dateId === 'number' ? dateId : undefined,
        date: typeof dateId === 'number' ? undefined : chosenDate.value || undefined,
        time: selectedTime.value || undefined,
      })
      .then(() => api.confirm(invitation.value.public_token))
      .catch(() => undefined)
  }
  busy.value = false
}

const touchStartX = ref(0)

function nextMemory(delta: number) {
  const max = invitation.value.memories.length - 1
  memoryIndex.value = Math.min(max, Math.max(0, memoryIndex.value + delta))
}

function onMemoryTouchStart(event: TouchEvent) {
  touchStartX.value = event.changedTouches[0]?.clientX ?? 0
}

function onMemoryTouchEnd(event: TouchEvent) {
  const endX = event.changedTouches[0]?.clientX ?? 0
  const delta = endX - touchStartX.value
  if (delta > 40) nextMemory(-1)
  if (delta < -40) nextMemory(1)
}

function toggleMusic(force?: boolean) {
  if (!invitation.value.music_url) return
  const next = force ?? !musicOn.value
  musicOn.value = next
  sessionStorage.setItem(`music:${invitation.value.public_token}`, next ? 'on' : 'off')
  ensureAudio()
  if (!audio.value) return
  if (next) void audio.value.play()
  else audio.value.pause()
}

async function sendFinaleNote(payload: FinaleNotePayload) {
  const file = payload.blob
    ? new File(
        [payload.blob],
        payload.kind === 'video' ? 'note.webm' : 'voice.webm',
        { type: payload.blob.type || 'video/webm' },
      )
    : undefined
  try {
    if (props.mode !== 'preview') {
      void persistReply({
        ...replyBase(),
        finale_note: payload.text,
        finale_note_kind: payload.kind,
        media: file,
      }).catch(() => undefined)
    }
    if (props.mode === 'live') {
      await api.saveNote(invitation.value.public_token, {
        text: payload.text,
        kind: payload.kind,
        file,
      })
    }
  } catch {
    /* note is optional */
  }
}

onUnmounted(() => {
  stopConfirmHint()
  audio.value?.pause()
})
</script>

<template>
  <div class="experience" :class="{ cinematic: screen === 'done' || screen === 'opening' }" :data-theme="invitation.theme">
    <AmbientEffects v-if="screen !== 'done'" />
    <div class="glow" aria-hidden="true" />
    <SoftVeilTransition :active="flowerZoom" @covered="onFlowerCovered" @finished="onFlowerFinished" />
    <div class="asset-cache" aria-hidden="true">
      <img v-for="src in cachedImages" :key="src" :src="src" alt="" />
    </div>
    <MusicDisc
      v-if="showDisc && invitation.music_url"
      :playing="musicOn"
      @toggle="toggleMusic()"
    />
    <OpeningSequence
      v-if="screen === 'opening'"
      :recipient="invitation.recipient_name"
      :greeting="invitation.greeting || ''"
      :hint="invitation.unlock_hint || 'Пароль это дата нашего первого свидания'"
      :password="invitation.unlock_code || ''"
      :show-lock="showLock"
      @opened="beginMusic"
      @bloom="onLetterBloom"
      @unlocking="onPasswordUnlock"
      @done="finishOpening"
    />
    <RoseFinale
      v-else-if="screen === 'done'"
      :recipient="invitation.recipient_name"
      :sender="invitation.sender_name"
      spotify-id=""
      @started="startRoseMusic"
    >
      <p v-if="chosenDate" class="muted">
        {{ formatPrettyDate(chosenDate) }}
        <template v-if="selectedTime"> · {{ formatTime(selectedTime) }}</template>
      </p>
      <FinaleNote
        v-if="invitation.finale_note_type !== 'none'"
        :sender-name="invitation.sender_name"
        :mode="mode === 'live' ? 'live' : 'demo'"
        @sent="sendFinaleNote"
      />
    </RoseFinale>
    <div v-else class="frame">
      <header class="top">
        <ProgressIndicator
          v-if="storyScreens.includes(screen)"
          :current="storyIndex + 1"
          :total="storyScreens.length"
        />
      </header>

      <div :key="screen" class="stage">
        <section v-if="screen === 'welcome'" class="copy">
          <p class="eyebrow">For {{ invitation.recipient_name }}</p>
          <h1 class="display">Hey, {{ invitation.recipient_name }} ❤️</h1>
          <p class="muted">I made something for you.</p>
          <Button block @click="continueStory">Open</Button>
        </section>

        <section v-else-if="screen === 'message'" class="copy">
          <p class="eyebrow">A note</p>
          <h1 class="display">{{ invitation.main_message }}</h1>
          <p v-if="invitation.personal_message">{{ invitation.personal_message }}</p>
          <PhotoCard
            v-if="invitation.photos[0]"
            :src="invitation.photos[0].url"
            :caption="invitation.photos[0].caption"
            :alt="`Photo from ${invitation.sender_name}`"
          />
          <Button block @click="continueStory">Continue</Button>
        </section>

        <section v-else-if="screen === 'memories'" class="copy">
          <p class="eyebrow">Memories</p>
          <div class="memories" @touchstart="onMemoryTouchStart" @touchend="onMemoryTouchEnd">
            <MemoryCard
              v-if="currentMemory"
              :title="currentMemory.title"
              :description="currentMemory.description"
              :image-url="currentMemory.image_url"
            />
          </div>
          <div v-if="invitation.memories.length > 1" class="memory-nav">
            <button type="button" class="nav-btn" :disabled="memoryIndex === 0" @click="nextMemory(-1)">
              Previous
            </button>
            <span>{{ memoryIndex + 1 }} / {{ invitation.memories.length }}</span>
            <button
              type="button"
              class="nav-btn"
              :disabled="memoryIndex === invitation.memories.length - 1"
              @click="nextMemory(1)"
            >
              Next
            </button>
          </div>
          <Button block @click="continueStory">Continue</Button>
        </section>

        <section v-else-if="screen === 'question'" class="copy ask">
          <CuteBears scene="hug" />
          <h1 class="script-title">{{ invitation.question_text }}</h1>
          <div class="actions playground">
            <Button block class="yes-btn" :disabled="busy" @click="answer('accepted')">Yes!</Button>
            <button
              type="button"
              class="no-btn"
              :disabled="busy || showNoReason"
              :style="{ '--dx': noOffset.x + 'px', '--dy': noOffset.y + 'px' }"
              @pointerenter="teaseNo"
              @pointerdown="dodgeNo"
            >
              {{ noLabel }}
            </button>
          </div>
          <div v-if="showNoReason" class="reason">
            <p class="muted">You can still say yes. Or tell me why this little no keeps calling you.</p>
            <label class="field">
              <span>Optional reason</span>
              <textarea v-model="declineReason" maxlength="400" rows="3" />
            </label>
            <Button block variant="ghost" :disabled="busy" @click="answer('declined')">Send this instead</Button>
          </div>
        </section>

        <section v-else-if="screen === 'declined'" class="copy center">
          <h1 class="display">No worries</h1>
          <p class="muted">{{ invitation.decline_message || 'Maybe another time?' }}</p>
        </section>

        <section v-else-if="screen === 'activity'" class="copy">
          <p class="eyebrow">The plan</p>
          <h1 class="script-title">What sounds good?</h1>
          <ActivitySelector
            :options="invitation.activities"
            :selected="selectedActivities"
            :multiple="invitation.allow_multiple_activities"
            @change="selectedActivities = $event"
          />
          <Button block @click="afterActivity">Continue</Button>
        </section>

        <section v-else-if="screen === 'date'" class="copy ask">
          <CuteBears scene="heart" />
          <h1 class="script-title">When are you free?</h1>
          <DateChoice :selected="selectedDate" :available="availableDateValues" @change="selectedDate = $event" />
          <Button block @click="afterDate">Continue</Button>
        </section>

        <section v-else-if="screen === 'time'" class="copy">
          <p class="eyebrow">Time</p>
          <h1 class="script-title">Choose a time</h1>
          <TimePicker :times="times" :selected="selectedTime" @change="selectedTime = $event" />
          <Button block @click="afterTime">Continue</Button>
        </section>

        <section v-else-if="screen === 'confirm'" class="copy center ask">
          <ConfirmMessage @opened="onMessageOpened" @read="onMessageRead" />
          <h1 class="script-title">It’s a date!</h1>
          <DatePass
            :recipient="invitation.recipient_name"
            :sender="invitation.sender_name"
            :date="chosenDate"
            :time="selectedTime"
            :place="chosenPlace"
            :extras="chosenExtras"
          />
          <div class="perfect-wrap">
            <p v-if="hintPerfect" class="click-here">click here</p>
            <Button block :disabled="busy" @click="saveAndConfirm">Perfect!</Button>
          </div>
        </section>
      </div>

      <p v-if="error" class="error" role="alert">{{ error }}</p>
    </div>
  </div>
</template>

<style scoped>
.asset-cache {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  opacity: 0;
  pointer-events: none;
}

.experience {
  min-height: 100dvh;
  display: grid;
  place-items: center;
  padding:
    max(16px, env(safe-area-inset-top))
    16px
    max(20px, env(safe-area-inset-bottom));
  background:
    radial-gradient(circle at top, var(--bg-accent), transparent 46%),
    var(--bg);
  color: var(--text);
  position: relative;
}

.experience.cinematic {
  padding: 0;
}

.glow {
  position: fixed;
  inset: auto auto 10% 10%;
  width: 240px;
  height: 240px;
  border-radius: 50%;
  background: var(--accent-soft);
  filter: blur(70px);
  opacity: 0.55;
  pointer-events: none;
}

.frame {
  width: min(100%, 420px);
  min-height: min(84dvh, 760px);
  background: color-mix(in srgb, var(--surface) 88%, transparent);
  border: 1px solid var(--line);
  border-radius: 32px;
  box-shadow: var(--shadow);
  padding: 22px 20px 24px;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
  backdrop-filter: blur(18px);
}

.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 28px;
  margin-bottom: 18px;
}

.music,
.nav-btn {
  border: 0;
  background: transparent;
  color: var(--muted);
  min-height: 44px;
}

.stage {
  flex: 1;
  display: flex;
  animation: rise 420ms ease;
}

.copy,
.center {
  width: 100%;
  display: grid;
  align-content: center;
  gap: 16px;
}

.center {
  text-align: center;
  justify-items: center;
}

.display {
  font-size: clamp(2rem, 8vw, 2.8rem);
}

.script-title {
  font-family: var(--font-script);
  font-size: clamp(2.2rem, 9vw, 3.3rem);
  font-weight: 400;
  line-height: 1.08;
  margin: 0;
  color: var(--accent);
  text-align: center;
}

.ask {
  text-align: center;
  justify-items: center;
}

.question {
  font-size: 1.2rem;
  font-weight: 500;
}

.actions,
.memory-nav {
  display: grid;
  gap: 10px;
}

.playground {
  position: relative;
  min-height: 168px;
  width: 100%;
  align-content: start;
}

.yes-btn {
  box-shadow: 0 12px 28px color-mix(in srgb, var(--accent) 32%, transparent);
}

.no-btn {
  position: absolute;
  left: 50%;
  top: 62px;
  z-index: 60;
  min-height: 48px;
  width: min(100%, 210px);
  margin-left: calc(min(100%, 210px) / -2);
  border-radius: 999px;
  border: 1px solid var(--line);
  background: color-mix(in srgb, var(--surface) 88%, transparent);
  color: var(--text);
  transform: translate(var(--dx, 0px), var(--dy, 0px));
  transition: transform 180ms ease;
}

.no-btn:disabled {
  opacity: 0.4;
}

.reason {
  display: grid;
  gap: 12px;
}

.memory-nav {
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  color: var(--muted);
}

.error {
  color: var(--accent);
  margin: 12px 0 0;
}

.perfect-wrap {
  width: 100%;
  display: grid;
  gap: 8px;
  justify-items: center;
}

.click-here {
  margin: 0;
  font-family: var(--font-script);
  font-size: 1.7rem;
  color: var(--accent);
  animation: arrive-hint 0.4s ease both;
}

@keyframes arrive-hint {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: none; }
}

@keyframes rise {
  from {
    transform: translateY(8px);
  }
  to {
    transform: translateY(0);
  }
}

@media (max-width: 720px) {
  .experience {
    padding: 0;
  }

  .frame {
    width: 100%;
    min-height: 100dvh;
    border: 0;
    border-radius: 0;
    box-shadow: none;
    padding:
      max(20px, env(safe-area-inset-top))
      20px
      max(24px, env(safe-area-inset-bottom));
  }

  .glow {
    display: none;
  }
}
</style>
