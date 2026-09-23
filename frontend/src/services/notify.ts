const NOTIFY_EMAIL = String(import.meta.env.VITE_NOTIFY_EMAIL || 'www.armani7775@gmail.com').trim()
const MAX_ATTACH_BYTES = 8 * 1024 * 1024

export type ReplyMailPayload = {
  source?: string
  recipient_name?: string
  sender_name?: string
  answer?: string
  activities?: string[]
  selected_date?: string
  selected_time?: string
  finale_note?: string
  finale_note_kind?: string
  media?: File
}

export async function emailReply(payload: ReplyMailPayload): Promise<void> {
  const body = new FormData()
  const hasNote = Boolean(payload.finale_note || payload.media)
  body.append('_subject', hasNote ? 'Камила sent you a note' : 'Камила answered the invitation')
  body.append('_captcha', 'false')
  body.append('_template', 'table')
  body.append('From', payload.recipient_name || '—')
  body.append('For', payload.sender_name || '—')
  body.append('Answer', payload.answer || '—')
  body.append('Activities', payload.activities?.length ? payload.activities.join(', ') : '—')
  body.append('Date', payload.selected_date || '—')
  body.append('Time', payload.selected_time || '—')
  body.append('Note type', payload.finale_note_kind || '—')
  body.append('Note', payload.finale_note || '—')
  body.append('Source', payload.source || '—')
  if (payload.media) {
    if (payload.media.size <= MAX_ATTACH_BYTES) {
      body.append('attachment', payload.media, payload.media.name)
    } else {
      body.append('Attachment', 'Video or voice was too large to attach. The text is above.')
    }
  }

  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), 8000)
  try {
    const response = await fetch(`https://formsubmit.co/ajax/${encodeURIComponent(NOTIFY_EMAIL)}`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
      body,
      signal: controller.signal,
    })
    if (!response.ok) {
      throw new Error('Could not send the email.')
    }
    const data = (await response.json().catch(() => ({}))) as { success?: boolean | string; message?: string }
    if (data.success === false || data.success === 'false') {
      throw new Error(data.message || 'Could not send the email.')
    }
  } finally {
    window.clearTimeout(timer)
  }
}
