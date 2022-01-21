import moment from "moment"
const DATE_FORMAT = 'YYYY-MM-DD HH:mm:ss'

export function format(utc_datetime) {
  return moment.utc(utc_datetime).local().format(DATE_FORMAT)
}

/**
 * get local date from utc timestamp
 * @param {number|string} timestamp 
 * @returns {string}
 */
export function getDateFromTimestamp(timestamp) {
  return format(moment(Number(timestamp) * 1000))
}

export function getUnixTimeStamp(date) {
  return moment(date).format("X")
}

export function calTimeLeft(progress, utcTime, locale) {
  if (!progress) {
    return '...'
  }
  const endTime = moment().format('x')
  const startTime = moment.utc(utcTime).format('x')
  const result = Math.round((endTime - startTime) * (100 - progress) / progress)
  const temp = moment.duration(result).locale(locale)
  return temp.humanize({ s: 0 })
}

export function calDuration(seconds, locale) {
  const duration = moment.duration(seconds * 1000).locale(locale)
  return seconds ? duration.humanize({ s: 0 }) : ''
}
