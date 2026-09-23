import { assetUrl } from '@/services/assets'
import { suggestedTimes } from '@/services/dates'
import type { InvitationPublic } from '@/types/invitation'

const dates = ['2026-09-25', '2026-09-26', '2026-09-27']
const times = suggestedTimes()

export const demoInvitation: InvitationPublic = {
  public_token: 'demo',
  sender_name: 'Арман',
  recipient_name: 'Камила',
  main_message: 'I have a little question for you...',
  personal_message: 'There are some things that are easier to say this way. I keep thinking about the way the evening felt last time we walked home.',
  question_text: 'Will you go out with me?',
  decline_message: 'Maybe another time?',
  theme: 'elegant',
  status: 'created',
  show_welcome: false,
  show_personal_message: false,
  show_memories: true,
  allow_multiple_activities: false,
  photos: [
    {
      id: 'demo-photo',
      url: 'https://images.unsplash.com/photo-1516589178581-6cd7833ae3b4?auto=format&fit=crop&w=1200&q=80',
      caption: 'A quiet evening',
      order: 0,
    },
  ],
  memories: [
    {
      id: 'm1',
      title: 'Remember this day?',
      description: 'I still smile when I think about it.',
      image_url: assetUrl('art/remember-this-day.png'),
      order: 0,
    },
  ],
  activities: [
    { id: 1, name: 'Выставка Леонардо да Винчи', icon: '🎨', enabled: true, order: 0 },
    { id: 2, name: 'Стрельба', icon: '🔫', enabled: true, order: 1 },
    { id: 3, name: 'Картинг', icon: '🏎️', enabled: true, order: 2 },
  ],
  available_dates: dates.map((date, index) => ({ id: index + 1, date })),
  available_times: times.map((time, index) => ({ id: index + 1, date_id: null, time: `${time}:00` })),
  has_music: true,
  music_url: null,
  youtube_id: '3gn_6HNGCtY',
  spotify_url: 'https://open.spotify.com/track/6T93nOlX56R5t2QoSfHgHn',
  music_start_sec: 0,
  music_end_sec: 0,
  greeting: '',
  unlock_code: '31082026',
  unlock_hint: 'Пароль это дата нашего первого свидания',
  finale_note_type: 'letter',
}
