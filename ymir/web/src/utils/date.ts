import moment from "moment"
const DATE_FORMAT = 'YYYY-MM-DD HH:mm:ss'

export function format(utc_datetime: string | number | moment.Moment) {
  return moment.utc(utc_datetime).local().format(DATE_FORMAT)
}

/**
 * get local date from utc timestamp
 * @param {number|string} timestamp 
 * @returns {string}
 */
export function getDateFromTimestamp(timestamp: number | string) {
  const ts: number = Number(timestamp) * 1000
  return format(moment(ts))
}

export function getUnixTimeStamp(date: string) {
  return moment(date).format("X")
}

export function calTimeLeft(progress: number, time: string, locale: string) {
  if (!progress) {
    return '...'
  }
  const endTime = Number(moment().format('x'))
  const startTime = Number(moment(time).format('x'))
  const result = Math.round((endTime - startTime) * (100 - progress) / progress)
  const temp = moment.duration(result).locale(locale)
  return temp.humanize({ s: 0 })
}

export function calDuration(seconds: number, locale: string) {
  const duration = moment.duration(seconds * 1000).locale(locale)
  return seconds ? duration.humanize({ s: 0 }) : ''
}

/**
 * get diff from tow time
 * @param a local time
 * @param b local time
 * @returns {number}
 */
export function diffTime(a: string, b: string) {
  return moment(a).diff(moment(b))
}
