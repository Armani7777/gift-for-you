export function todayIso(now = new Date()): string {
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function upcomingDates(days = 14, now = new Date()): string[] {
  const start = new Date(now)
  start.setHours(12, 0, 0, 0)
  return Array.from({ length: days }, (_, index) => {
    const next = new Date(start)
    next.setDate(start.getDate() + index)
    return todayIso(next)
  })
}

export function suggestedTimes(): string[] {
  return ['17:00', '18:00', '18:30', '19:00', '19:30', '20:00']
}

export function hourlyTimes(fromHour = 12, toHour = 22, stepMinutes = 30): string[] {
  const times: string[] = []
  for (let minutes = fromHour * 60; minutes <= toHour * 60; minutes += stepMinutes) {
    const hour = Math.floor(minutes / 60)
    const minute = minutes % 60
    times.push(`${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`)
  }
  return times
}

export function normalizeClock(value: string): string | null {
  const match = value.trim().match(/^(\d{1,2}):(\d{2})(?::\d{2})?$/)
  if (!match) return null
  const hours = Number(match[1])
  const minutes = Number(match[2])
  if (hours > 23 || minutes > 59) return null
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
}

export function isTimeStillOpen(dateIso: string, time: string, now = new Date()): boolean {
  const clock = normalizeClock(time)
  if (!clock) return false
  if (dateIso !== todayIso(now)) return true
  const [hours, minutes] = clock.split(':').map(Number)
  const stamp = new Date(now)
  stamp.setHours(hours, minutes, 0, 0)
  return stamp >= new Date(now.getTime() + 60 * 60 * 1000)
}

export function selectableDates(configured: string[], now = new Date()): string[] {
  const today = todayIso(now)
  const chosen = configured.filter((date) => date >= today).sort()
  if (chosen.length) return chosen
  return upcomingDates(14, now)
}

export function selectableTimes(dateIso: string, configured: string[], now = new Date()): string[] {
  const extra = configured
    .map((item) => normalizeClock(item))
    .filter((item): item is string => Boolean(item))
  const source = extra.length > 0 && extra.length <= 6 ? extra : extra.length > 6 ? extra.slice(0, 6) : suggestedTimes()
  const valid = Array.from(new Set(source))
    .sort()
    .filter((time) => isTimeStillOpen(dateIso, time, now))
  if (valid.length) return valid.slice(0, 6)

  const minimum = new Date(now.getTime() + 60 * 60 * 1000)
  const fallback = new Date(minimum)
  if (minimum.getMinutes() > 0) fallback.setMinutes(0, 0, 0)
  if (fallback.getDate() !== now.getDate()) return []
  const clock = `${String(fallback.getHours()).padStart(2, '0')}:${String(fallback.getMinutes()).padStart(2, '0')}`
  return [clock]
}
