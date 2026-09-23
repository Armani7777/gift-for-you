export type ThemeName = 'minimal' | 'romantic' | 'sunset' | 'night' | 'soft' | 'elegant'

export type InvitationStatus =
  | 'created'
  | 'opened'
  | 'accepted'
  | 'declined'
  | 'planning'
  | 'confirmed'

export type ResponseAnswer = 'accepted' | 'declined'

export interface Photo {
  id: number | string
  url: string | null
  caption: string
  order: number
}

export interface Memory {
  id: number | string
  title: string
  description: string
  image_url: string | null
  order: number
}

export interface Activity {
  id: number | string
  name: string
  icon: string
  enabled: boolean
  order: number
}

export interface AvailableDate {
  id: number | string
  date: string
}

export interface AvailableTime {
  id: number | string
  date_id: number | null
  time: string
}

export interface InvitationPublic {
  public_token: string
  sender_name: string
  recipient_name: string
  main_message: string
  personal_message: string
  question_text: string
  decline_message: string
  theme: ThemeName
  status: InvitationStatus
  show_welcome: boolean
  show_personal_message: boolean
  show_memories: boolean
  allow_multiple_activities: boolean
  photos: Photo[]
  memories: Memory[]
  activities: Activity[]
  available_dates: AvailableDate[]
  available_times: AvailableTime[]
  has_music: boolean
  music_url: string | null
  youtube_id?: string
  spotify_url?: string
  music_start_sec?: number
  music_end_sec?: number
  greeting?: string
  unlock_code?: string
  unlock_hint?: string
  finale_note_type?: 'letter' | 'review' | 'none'
}

export interface RecipientResponse {
  answer: ResponseAnswer
  selected_activities?: Activity[]
  selected_activity_ids?: Array<number | string>
  selected_date: string | null
  selected_time: string | null
  decline_reason?: string
  finale_note?: string
  finale_note_kind?: string
  finale_note_media_url?: string | null
  confirmed_at: string | null
}

export interface GuestReply {
  id: number
  session_key: string
  source: string
  public_token: string
  recipient_name: string
  sender_name: string
  answer: string
  activities: string[]
  selected_date: string
  selected_time: string
  finale_note: string
  finale_note_kind: string
  media_url: string | null
  created_at: string
  updated_at: string
}

export interface InvitationManage extends InvitationPublic {
  management_token: string
  opened_at: string | null
  responded_at: string | null
  created_at: string
  response: RecipientResponse | null
}

export interface CreatedInvitation {
  public_token: string
  management_token: string
  status: InvitationStatus
}

export interface CreateInvitationPayload {
  sender_name: string
  recipient_name: string
  main_message: string
  personal_message: string
  question_text: string
  decline_message: string
  theme: ThemeName
  show_welcome: boolean
  show_personal_message: boolean
  show_memories: boolean
  allow_multiple_activities: boolean
  activities: Array<{ name: string; icon: string; enabled: boolean }>
  available_dates: string[]
  available_times: Array<{ time: string }>
  memories: Array<{ title: string; description: string }>
  greeting?: string
  unlock_code?: string
  unlock_hint?: string
  finale_note_type?: 'letter' | 'review' | 'none'
  spotify_url?: string
  music_start_sec?: number
  music_end_sec?: number
}
