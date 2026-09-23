<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Button from '@/components/Button.vue'
import InvitationExperience from '@/components/InvitationExperience.vue'
import { demoInvitation } from '@/data/demo'
import { compressImage } from '@/services/images'
import { parseClockToSeconds } from '@/services/spotify'
import type { InvitationPublic, ThemeName } from '@/types/invitation'

const route = useRoute()
const router = useRouter()
const canEdit = computed(() => String(route.query.edit) === '1')
const open = ref(false)
const copied = ref(false)

function queryGreeting() {
  const value = String(route.query.hi || '')
  return /^hi,?\s*beautiful!?$/i.test(value) ? '' : value
}

function iconForPlace(name: string, index: number) {
  const value = name.toLowerCase()
  if (value.includes('стрельб') || value.includes('shoot')) return '🔫'
  if (value.includes('картинг') || value.includes('kart') || value.includes('racing')) return '🏎️'
  if (value.includes('леон') || value.includes('выстав') || value.includes('museum')) return '🎨'
  const fallback = ['🎨', '🔫', '🏎️', '🎬', '☕', '🍝', '🌆', '🌸']
  return fallback[index % fallback.length]
}

const editor = reactive({
  recipientName: String(route.query.to || demoInvitation.recipient_name),
  senderName: String(route.query.from || demoInvitation.sender_name),
  questionText: String(route.query.q || demoInvitation.question_text),
  personalMessage: demoInvitation.personal_message,
  places: String(route.query.places || demoInvitation.activities.map((item) => item.name).join(', ')),
  theme: String(route.query.theme || demoInvitation.theme) as ThemeName,
  greeting: queryGreeting(),
  unlockHint: String(route.query.hint || 'Пароль это дата нашего первого свидания'),
  unlockCode: String(route.query.pin || '31082026'),
  finaleNoteType: String(route.query.note || 'letter') as 'letter' | 'review' | 'none',
  spotifyUrl: String(route.query.spotify || ''),
  musicStart: String(route.query.start || '0:00'),
  musicEnd: String(route.query.end || ''),
  musicUrl: demoInvitation.music_url || '',
  photoUrl: demoInvitation.photos[0]?.url || '',
  memoryOneUrl: demoInvitation.memories[0]?.image_url || '',
})

const invitation = computed<InvitationPublic>(() => {
  const places = editor.places
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 8)
  return {
    ...demoInvitation,
    recipient_name: editor.recipientName || demoInvitation.recipient_name,
    sender_name: editor.senderName || demoInvitation.sender_name,
    question_text: editor.questionText || demoInvitation.question_text,
    personal_message: editor.personalMessage,
    theme: editor.theme,
    show_welcome: false,
    show_personal_message: false,
    greeting: editor.greeting,
    unlock_code: editor.unlockCode,
    unlock_hint: editor.unlockHint,
    finale_note_type: editor.finaleNoteType,
    spotify_url: editor.spotifyUrl,
    music_start_sec: parseClockToSeconds(editor.musicStart),
    music_end_sec: parseClockToSeconds(editor.musicEnd),
    has_music: Boolean(editor.musicUrl || editor.spotifyUrl || demoInvitation.music_url || demoInvitation.youtube_id),
    music_url: editor.musicUrl || demoInvitation.music_url || null,
    youtube_id: demoInvitation.youtube_id,
    photos: editor.photoUrl
      ? [{ id: 'demo-photo', url: editor.photoUrl, caption: 'A quiet evening', order: 0 }]
      : [],
    memories: [
      {
        id: 'm1',
        title: 'Remember this day?',
        description: 'I still smile when I think about it.',
        image_url: editor.memoryOneUrl || null,
        order: 0,
      },
    ].filter((item) => item.image_url || item.title),
    activities: places.map((name, index) => ({
      id: index + 1,
      name,
      icon: iconForPlace(name, index),
      enabled: true,
      order: index,
    })),
  }
})

watch(
  () => ({
    to: editor.recipientName,
    from: editor.senderName,
    q: editor.questionText,
    places: editor.places,
    theme: editor.theme,
    hi: editor.greeting,
    hint: editor.unlockHint,
    pin: editor.unlockCode,
    note: editor.finaleNoteType,
    spotify: editor.spotifyUrl,
    start: editor.musicStart,
    end: editor.musicEnd,
    edit: '1',
  }),
  (query) => {
    if (!canEdit.value) return
    void router.replace({ query })
  },
  { deep: true },
)

async function onImage(event: Event, key: 'photoUrl' | 'memoryOneUrl') {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const compressed = await compressImage(file)
  editor[key] = URL.createObjectURL(compressed)
  input.value = ''
}

function onMusic(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (editor.musicUrl) URL.revokeObjectURL(editor.musicUrl)
  editor.musicUrl = URL.createObjectURL(file)
  input.value = ''
}

async function copyDemoLink() {
  try {
    const url = `${window.location.origin}/demo`
    await navigator.clipboard.writeText(url)
    copied.value = true
    window.setTimeout(() => {
      copied.value = false
    }, 1600)
  } catch {
    copied.value = false
  }
}
</script>

<template>
  <div class="demo">
    <InvitationExperience :invitation="invitation" mode="demo" />
    <button v-if="canEdit" type="button" class="edit" @click="open = !open">
      {{ open ? 'Close' : 'Edit demo' }}
    </button>
    <aside v-if="canEdit && open" class="panel">
      <p class="eyebrow">Demo details</p>
      <label class="field">
        <span>Recipient name</span>
        <input v-model="editor.recipientName" />
      </label>
      <label class="field">
        <span>Your name</span>
        <input v-model="editor.senderName" />
      </label>
      <label class="field">
        <span>Question</span>
        <input v-model="editor.questionText" />
      </label>
      <label class="field">
        <span>Personal message</span>
        <textarea v-model="editor.personalMessage" rows="3" />
      </label>
      <label class="field">
        <span>Places / activities</span>
        <input v-model="editor.places" placeholder="Coffee, Dinner, Walk" />
      </label>
      <label class="field">
        <span>Theme</span>
        <select v-model="editor.theme">
          <option v-for="theme in ['elegant', 'minimal', 'romantic', 'sunset', 'night', 'soft']" :key="theme" :value="theme">
            {{ theme }}
          </option>
        </select>
      </label>
      <label class="field">
        <span>Greeting (optional)</span>
        <input v-model="editor.greeting" :placeholder="`Hi, ${editor.recipientName || 'Камила'}`" />
      </label>
      <label class="field">
        <span>Password hint</span>
        <input v-model="editor.unlockHint" />
      </label>
      <label class="field">
        <span>Password (DDMMYYYY)</span>
        <input v-model="editor.unlockCode" maxlength="8" inputmode="numeric" />
      </label>
      <label class="field">
        <span>After the rose</span>
        <select v-model="editor.finaleNoteType">
          <option value="letter">Write a letter</option>
          <option value="review">Leave a review</option>
          <option value="none">Nothing extra</option>
        </select>
      </label>
      <label class="field">
        <span>Spotify track URL</span>
        <input v-model="editor.spotifyUrl" placeholder="https://open.spotify.com/track/..." />
      </label>
      <div class="clip">
        <label class="field">
          <span>Play from</span>
          <input v-model="editor.musicStart" placeholder="0:45" />
        </label>
        <label class="field">
          <span>Play until</span>
          <input v-model="editor.musicEnd" placeholder="1:20" />
        </label>
      </div>
      <label class="field">
        <span>Audio file for the exact clip</span>
        <input type="file" accept="audio/*" @change="onMusic" />
        <small class="muted">The rose uses this file with your start/end times. Spotify alone opens a player.</small>
      </label>
      <label class="field">
        <span>Story photo</span>
        <input type="file" accept="image/*" @change="onImage($event, 'photoUrl')" />
      </label>
      <label class="field">
        <span>Memory photo</span>
        <input type="file" accept="image/*" @change="onImage($event, 'memoryOneUrl')" />
      </label>
      <Button block @click="copyDemoLink">{{ copied ? 'Link copied' : 'Copy demo link' }}</Button>
    </aside>
  </div>
</template>

<style scoped>
.demo {
  min-height: 100dvh;
}

.edit {
  position: fixed;
  top: max(12px, env(safe-area-inset-top));
  right: 12px;
  z-index: 20;
  min-height: 44px;
  border: 1px solid var(--line);
  background: var(--surface);
  border-radius: 999px;
  padding: 0 14px;
}

.panel {
  position: fixed;
  z-index: 21;
  top: max(64px, calc(env(safe-area-inset-top) + 52px));
  right: 12px;
  width: min(92vw, 340px);
  max-height: calc(100dvh - 90px);
  overflow: auto;
  display: grid;
  gap: 12px;
  padding: 16px;
  border-radius: 20px;
  background: var(--surface);
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
}

.clip {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.muted {
  color: var(--muted);
}
</style>
