import { suggestedTimes } from '@/services/dates'
import { parseClockToSeconds } from '@/services/spotify'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { InvitationPublic, ThemeName } from '@/types/invitation'

export interface WizardPhoto {
  key: string
  file: File
  previewUrl: string
  caption: string
}

export interface WizardMemory {
  key: string
  title: string
  description: string
  file: File | null
  previewUrl: string
}

const defaultActivities = [
  { name: 'Coffee', icon: '☕', enabled: true },
  { name: 'Dinner', icon: '🍝', enabled: true },
  { name: 'Movie', icon: '🎬', enabled: true },
  { name: 'Walk', icon: '🌆', enabled: true },
  { name: 'Something different', icon: '🎨', enabled: true },
]

function uid() {
  return crypto.randomUUID()
}

export const useWizardStore = defineStore('wizard', () => {
  const recipientName = ref('')
  const senderName = ref('')
  const mainMessage = ref('I have a little question for you...')
  const personalMessage = ref('')
  const questionText = ref('Will you go out with me?')
  const declineMessage = ref('Maybe another time?')
  const theme = ref<ThemeName>('elegant')
  const showWelcome = ref(true)
  const showPersonalMessage = ref(true)
  const showMemories = ref(false)
  const allowMultipleActivities = ref(false)
  const photos = ref<WizardPhoto[]>([])
  const memories = ref<WizardMemory[]>([])
  const activities = ref(defaultActivities.map((item) => ({ ...item })))
  const dates = ref<string[]>([])
  const times = ref<string[]>(suggestedTimes())
  const musicFile = ref<File | null>(null)
  const musicName = ref('')
  const spotifyUrl = ref('')
  const musicStart = ref('0:00')
  const musicEnd = ref('')
  const step = ref(0)

  const previewInvitation = computed<InvitationPublic>(() => ({
    public_token: 'preview',
    sender_name: senderName.value || 'You',
    recipient_name: recipientName.value || 'Them',
    main_message: mainMessage.value,
    personal_message: personalMessage.value,
    question_text: questionText.value,
    decline_message: declineMessage.value,
    theme: theme.value,
    status: 'created',
    show_welcome: showWelcome.value,
    show_personal_message: showPersonalMessage.value,
    show_memories: showMemories.value && memories.value.length > 0,
    allow_multiple_activities: allowMultipleActivities.value,
    photos: photos.value.map((photo, index) => ({
      id: photo.key,
      url: photo.previewUrl,
      caption: photo.caption,
      order: index,
    })),
    memories: memories.value.map((memory, index) => ({
      id: memory.key,
      title: memory.title || 'A memory',
      description: memory.description,
      image_url: memory.previewUrl || null,
      order: index,
    })),
    activities: activities.value
      .filter((item) => item.enabled && item.name.trim())
      .map((item, index) => ({
        id: index + 1,
        name: item.name,
        icon: item.icon,
        enabled: true,
        order: index,
      })),
    available_dates: dates.value.map((date, index) => ({ id: index + 1, date })),
    available_times: times.value.map((time, index) => ({
      id: index + 1,
      date_id: null,
      time: `${time}:00`,
    })),
    has_music: Boolean(musicFile.value || spotifyUrl.value),
    music_url: null,
    spotify_url: spotifyUrl.value,
    music_start_sec: parseClockToSeconds(musicStart.value),
    music_end_sec: parseClockToSeconds(musicEnd.value),
    greeting: '',
    unlock_code: '31082026',
    unlock_hint: 'Пароль это дата нашего первого свидания',
    finale_note_type: 'letter',
  }))

  function addPhoto(file: File, previewUrl: string) {
    if (photos.value.length >= 5) return
    photos.value.push({ key: uid(), file, previewUrl, caption: '' })
  }

  function removePhoto(key: string) {
    const photo = photos.value.find((item) => item.key === key)
    if (photo) URL.revokeObjectURL(photo.previewUrl)
    photos.value = photos.value.filter((item) => item.key !== key)
  }

  function addMemory() {
    if (memories.value.length >= 5) return
    memories.value.push({
      key: uid(),
      title: '',
      description: '',
      file: null,
      previewUrl: '',
    })
    showMemories.value = true
  }

  function removeMemory(key: string) {
    const memory = memories.value.find((item) => item.key === key)
    if (memory?.previewUrl) URL.revokeObjectURL(memory.previewUrl)
    memories.value = memories.value.filter((item) => item.key !== key)
    if (memories.value.length === 0) showMemories.value = false
  }

  function setMusic(file: File | null) {
    musicFile.value = file
    musicName.value = file?.name ?? ''
  }

  return {
    recipientName,
    senderName,
    mainMessage,
    personalMessage,
    questionText,
    declineMessage,
    theme,
    showWelcome,
    showPersonalMessage,
    showMemories,
    allowMultipleActivities,
    photos,
    memories,
    activities,
    dates,
    times,
    musicFile,
    musicName,
    spotifyUrl,
    musicStart,
    musicEnd,
    step,
    previewInvitation,
    addPhoto,
    removePhoto,
    addMemory,
    removeMemory,
    setMusic,
  }
})
