export function formatPrettyDate(isoDate: string): string {
  const date = new Date(`${isoDate}T12:00:00`)
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  }).format(date)
}

export function formatTime(value: string): string {
  const [hours = '00', minutes = '00'] = value.split(':')
  return `${hours.padStart(2, '0')}:${minutes.padStart(2, '0')}`
}

export function invitationUrl(token: string): string {
  return `${window.location.origin}/i/${token}`
}

export function manageUrl(publicToken: string, managementToken: string): string {
  return `${window.location.origin}/manage/${publicToken}/${managementToken}`
}

export async function copyText(value: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(value)
    return true
  } catch {
    return false
  }
}

export async function shareLink(title: string, url: string): Promise<'shared' | 'copied' | 'failed'> {
  if (typeof navigator.share === 'function') {
    try {
      await navigator.share({ title, url })
      return 'shared'
    } catch (error) {
      if ((error as DOMException).name === 'AbortError') return 'failed'
    }
  }
  return (await copyText(url)) ? 'copied' : 'failed'
}

export function downloadCalendarEvent(options: {
  title: string
  date: string
  time?: string | null
  description?: string
}): void {
  const start = options.time
    ? `${options.date.replaceAll('-', '')}T${options.time.replaceAll(':', '').slice(0, 4)}00`
    : `${options.date.replaceAll('-', '')}T180000`
  const endHour = options.time ? Number(options.time.slice(0, 2)) + 2 : 20
  const end = `${options.date.replaceAll('-', '')}T${String(endHour).padStart(2, '0')}${
    options.time ? options.time.slice(3, 5) : '00'
  }00`
  const ics = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//Date Invitation//EN',
    'BEGIN:VEVENT',
    `UID:${crypto.randomUUID()}@date-invitation`,
    `DTSTAMP:${start}`,
    `DTSTART:${start}`,
    `DTEND:${end}`,
    `SUMMARY:${options.title}`,
    `DESCRIPTION:${(options.description || '').replace(/\n/g, '\\n')}`,
    'END:VEVENT',
    'END:VCALENDAR',
  ].join('\r\n')
  const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'date.ics'
  link.click()
  URL.revokeObjectURL(url)
}
