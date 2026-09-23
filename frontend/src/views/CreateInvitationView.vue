<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import ActivitySelector from '@/components/ActivitySelector.vue'
import Button from '@/components/Button.vue'
import DatePicker from '@/components/DatePicker.vue'
import InvitationExperience from '@/components/InvitationExperience.vue'
import PhoneFrame from '@/components/PhoneFrame.vue'
import ProgressIndicator from '@/components/ProgressIndicator.vue'
import { api } from '@/services/api'
import { todayIso, normalizeClock } from '@/services/dates'
import { compressImage } from '@/services/images'
import { parseClockToSeconds } from '@/services/spotify'
import { useWizardStore } from '@/stores/wizard'
import type { ThemeName } from '@/types/invitation'

const steps = ['Basics', 'Story', 'Photos', 'Date', 'Style', 'Preview']
const themes: ThemeName[] = ['elegant', 'minimal', 'romantic', 'sunset', 'night', 'soft']
const wizard = useWizardStore()
const router = useRouter()
const error = ref('')
const publishing = ref(false)
const customActivity = ref('')
const customTime = ref('')

const canContinue = computed(() => {
  if (wizard.step === 0) {
    return wizard.recipientName.trim().length > 0 && wizard.senderName.trim().length > 0 && wizard.mainMessage.trim().length > 0
  }
  return true
})

function next() {
  if (!canContinue.value || publishing.value) return
  wizard.step = Math.min(steps.length - 1, wizard.step + 1)
}

function back() {
  wizard.step = Math.max(0, wizard.step - 1)
}

async function onPhotos(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || [])
  for (const file of files) {
    const compressed = await compressImage(file)
    wizard.addPhoto(compressed, URL.createObjectURL(compressed))
  }
  input.value = ''
}

async function onMemoryImage(key: string, event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const compressed = await compressImage(file)
  const memory = wizard.memories.find((item) => item.key === key)
  if (!memory) return
  if (memory.previewUrl) URL.revokeObjectURL(memory.previewUrl)
  memory.file = compressed
  memory.previewUrl = URL.createObjectURL(compressed)
  input.value = ''
}

function onMusic(event: Event) {
  const input = event.target as HTMLInputElement
  wizard.setMusic(input.files?.[0] || null)
}

function addCustomActivity() {
  const name = customActivity.value.trim()
  if (!name) return
  wizard.activities.push({ name, icon: '✨', enabled: true })
  customActivity.value = ''
}

function addCustomTime() {
  const next = normalizeClock(customTime.value)
  if (!next) return
  if (!wizard.times.includes(next)) wizard.times.push(next)
  customTime.value = ''
}

async function publish() {
  if (publishing.value) return
  publishing.value = true
  error.value = ''
  try {
    const created = await api.createInvitation({
      sender_name: wizard.senderName.trim(),
      recipient_name: wizard.recipientName.trim(),
      main_message: wizard.mainMessage.trim(),
      personal_message: wizard.personalMessage.trim(),
      question_text: wizard.questionText.trim() || 'Will you go out with me?',
      decline_message: wizard.declineMessage.trim(),
      theme: wizard.theme,
      show_welcome: wizard.showWelcome,
      show_personal_message: wizard.showPersonalMessage,
      show_memories: wizard.showMemories && wizard.memories.length > 0,
      allow_multiple_activities: wizard.allowMultipleActivities,
      activities: wizard.activities.filter((item) => item.name.trim()),
      available_dates: wizard.dates,
      available_times: wizard.times.map((time) => ({ time })),
      greeting: '',
      unlock_code: '31082026',
      unlock_hint: 'Пароль это дата нашего первого свидания',
      finale_note_type: 'letter',
      spotify_url: wizard.spotifyUrl.trim(),
      music_start_sec: parseClockToSeconds(wizard.musicStart),
      music_end_sec: parseClockToSeconds(wizard.musicEnd) || undefined,
      memories: wizard.memories.map((item) => ({
        title: item.title.trim() || 'A memory',
        description: item.description.trim(),
      })),
    })

    for (const photo of wizard.photos) {
      await api.uploadPhoto(created.public_token, created.management_token, photo.file, photo.caption)
    }

    if (wizard.memories.some((item) => item.file)) {
      const managed = await api.getManaged(created.public_token, created.management_token)
      for (const [index, memory] of wizard.memories.entries()) {
        const createdMemory = managed.memories[index]
        if (memory.file && createdMemory && typeof createdMemory.id === 'number') {
          await api.uploadMemoryImage(created.public_token, created.management_token, createdMemory.id, memory.file)
        }
      }
    }

    if (wizard.musicFile) {
      await api.uploadMusic(created.public_token, created.management_token, wizard.musicFile)
    }

    await router.push({
      name: 'manage',
      params: { token: created.public_token, managementToken: created.management_token },
      query: { fresh: '1' },
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not publish the invitation.'
  } finally {
    publishing.value = false
  }
}
</script>

<template>
  <main class="wizard page-shell">
    <header class="head">
      <p class="eyebrow">Create invitation</p>
      <ProgressIndicator :current="wizard.step + 1" :total="steps.length" />
      <h1>{{ steps[wizard.step] }}</h1>
    </header>

    <section v-if="wizard.step === 0" class="stack">
      <label class="field">
        <span>Recipient name</span>
        <input v-model="wizard.recipientName" maxlength="80" autocomplete="off" />
      </label>
      <label class="field">
        <span>Your name</span>
        <input v-model="wizard.senderName" maxlength="80" autocomplete="off" />
      </label>
      <label class="field">
        <span>Main message</span>
        <input v-model="wizard.mainMessage" maxlength="240" />
      </label>
    </section>

    <section v-else-if="wizard.step === 1" class="stack">
      <label class="field">
        <span>Personal message</span>
        <textarea v-model="wizard.personalMessage" maxlength="1200" />
      </label>
      <label class="field">
        <span>The question</span>
        <input v-model="wizard.questionText" maxlength="240" />
      </label>
      <label class="field">
        <span>If they say no</span>
        <input v-model="wizard.declineMessage" maxlength="240" />
      </label>
      <label class="check">
        <input v-model="wizard.showWelcome" type="checkbox" />
        Show welcome screen
      </label>
      <label class="check">
        <input v-model="wizard.showPersonalMessage" type="checkbox" />
        Show personal message
      </label>
    </section>

    <section v-else-if="wizard.step === 2" class="stack">
      <label class="field">
        <span>Photos, up to 5</span>
        <input type="file" accept="image/*" multiple @change="onPhotos" />
      </label>
      <div v-for="photo in wizard.photos" :key="photo.key" class="item">
        <img :src="photo.previewUrl" alt="" />
        <div class="stack">
          <input v-model="photo.caption" placeholder="Caption" />
          <Button variant="ghost" @click="wizard.removePhoto(photo.key)">Remove</Button>
        </div>
      </div>
      <Button variant="secondary" @click="wizard.addMemory">Add a memory card</Button>
      <div v-for="memory in wizard.memories" :key="memory.key" class="item">
        <div class="stack">
          <input v-model="memory.title" placeholder="Remember this day?" />
          <input v-model="memory.description" placeholder="A short note" />
          <input type="file" accept="image/*" @change="onMemoryImage(memory.key, $event)" />
          <Button variant="ghost" @click="wizard.removeMemory(memory.key)">Remove memory</Button>
        </div>
      </div>
    </section>

    <section v-else-if="wizard.step === 3" class="stack">
      <p class="muted">Choose the days and times they can pick from.</p>
      <DatePicker :selected="wizard.dates" multiple :min-date="todayIso()" @change="wizard.dates = $event" />
      <div class="times">
        <button
          v-for="time in wizard.times"
          :key="time"
          type="button"
          class="time"
          @click="wizard.times = wizard.times.filter((item) => item !== time)"
        >
          {{ time }} ×
        </button>
      </div>
      <label class="field">
        <span>Add a 24-hour time</span>
        <input v-model="customTime" placeholder="19:30" inputmode="numeric" />
      </label>
      <Button variant="ghost" @click="addCustomTime">Add time</Button>
      <ActivitySelector
        :options="wizard.activities.map((item, index) => ({ ...item, id: index, order: index }))"
        :selected="wizard.activities.map((item, index) => (item.enabled ? index : -1)).filter((id) => id >= 0)"
        multiple
        @change="
          (ids) =>
            wizard.activities.forEach((item, index) => {
              item.enabled = ids.includes(index)
            })
        "
      />
      <label class="check">
        <input v-model="wizard.allowMultipleActivities" type="checkbox" />
        Allow more than one activity
      </label>
      <label class="field">
        <span>Custom activity</span>
        <input v-model="customActivity" @keydown.enter.prevent="addCustomActivity" />
      </label>
      <Button variant="ghost" @click="addCustomActivity">Add activity</Button>
    </section>

    <section v-else-if="wizard.step === 4" class="stack">
      <div class="themes">
        <button
          v-for="item in themes"
          :key="item"
          type="button"
          class="theme"
          :class="{ selected: wizard.theme === item }"
          @click="wizard.theme = item"
        >
          {{ item }}
        </button>
      </div>
      <label class="field">
        <span>Optional music file</span>
        <input type="file" accept="audio/*" @change="onMusic" />
        <small v-if="wizard.musicName" class="muted">{{ wizard.musicName }}</small>
      </label>
      <label class="field">
        <span>Spotify track URL</span>
        <input v-model="wizard.spotifyUrl" placeholder="https://open.spotify.com/track/..." />
      </label>
      <label class="field">
        <span>Play from (m:ss)</span>
        <input v-model="wizard.musicStart" placeholder="0:45" />
      </label>
      <label class="field">
        <span>Play until (m:ss)</span>
        <input v-model="wizard.musicEnd" placeholder="1:20" />
      </label>
      <p class="muted">The rose starts the song. Upload a file if you want an exact clip; Spotify opens a player.</p>
    </section>

    <section v-else class="preview">
      <PhoneFrame label="Mobile preview">
        <InvitationExperience :invitation="wizard.previewInvitation" mode="preview" />
      </PhoneFrame>
    </section>

    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <footer class="nav">
      <Button variant="ghost" :disabled="wizard.step === 0 || publishing" @click="back">Back</Button>
      <Button v-if="wizard.step < steps.length - 1" :disabled="!canContinue" @click="next">Continue</Button>
      <Button v-else :disabled="publishing || !canContinue" @click="publish">
        {{ publishing ? 'Publishing…' : 'Publish' }}
      </Button>
    </footer>
  </main>
</template>

<style scoped>
.wizard {
  max-width: 640px;
  margin: 0 auto;
  display: grid;
  gap: 24px;
}

.head h1 {
  margin: 12px 0 0;
  font-family: var(--font-serif);
  font-size: 2rem;
  font-weight: 500;
}

.check {
  display: flex;
  gap: 10px;
  align-items: center;
}

.item {
  display: grid;
  grid-template-columns: 92px 1fr;
  gap: 12px;
  align-items: start;
}

.item img {
  width: 92px;
  height: 92px;
  object-fit: cover;
  border-radius: 16px;
}

.themes {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.theme {
  min-height: 48px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: var(--surface);
  text-transform: capitalize;
}

.theme.selected {
  border-color: var(--accent);
  background: var(--accent-soft);
}

.times {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.time {
  min-height: 40px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--surface);
  padding: 0 12px;
}

.preview {
  display: grid;
  justify-items: center;
}

.preview :deep(.experience) {
  min-height: 560px;
  padding: 0;
}

.preview :deep(.frame) {
  min-height: 560px;
  border: 0;
  box-shadow: none;
}

.nav {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  position: sticky;
  bottom: 0;
  padding-bottom: env(safe-area-inset-bottom);
  background: linear-gradient(to top, var(--bg), transparent);
}

.error {
  color: var(--accent);
}
</style>
