import { format, getDateFromTimestamp,getUnixTimeStamp, calTimeLeft, calDuration, diffTime, } from "../date"
import moment from 'moment'

describe("utils: date", () => {
  it("function: format. transfer utc to local", () => {
    const time = "2021-07-05T01:37:28.242Z" // utc format
    const expected = moment(time).local().format('YYYY-MM-DD HH:mm:ss')
    expect(format(time)).toBe(expected) // local date and time
  })
  it("function: getDateFromTimestamp. get local format date from timestamp(utc)", () => {
    const timestamp = "1625449048"
    const expected = format(moment(Number(timestamp) * 1000))
    expect(getDateFromTimestamp(timestamp)).toBe(expected)
  })
  it("function: getUnixTimeStamp. get timestamp from utc time", () => {
    const time = "2021-07-05T01:37:28.242Z"
    const expected = '1625449048'
    expect(getUnixTimeStamp(time)).toBe(expected)
  })
  it("function: calTimeLeft. calculate left time to 100%", () => {
    const time = moment().subtract({ months: 2 })
    const locale = 'zh-CN'
    const expected = '4 个月'
    expect(calTimeLeft(33, time, locale)).toBe(expected)
    expect(calTimeLeft(0, time, locale)).toBe('...')
    expect(calTimeLeft(undefined, time, locale)).toBe('...')
  })
  it("function: calDuration. humanize duration for seconds", () => {
    const senconds = 23423242 // utc format
    const expected = '9 个月'
    expect(calDuration(senconds, 'zh-CN')).toBe(expected)
    expect(calDuration(0, 'zh-CN')).toBe('')
    expect(calDuration(null, 'zh-CN')).toBe('')
  })
  it("function: diffTime. ", () => {
    const date = '2022-04-15 11:59:04'
    const date2 = '2022-04-17 08:26:34'
    const expected = 160050000
    expect(diffTime(date, date)).toBe(0)
    expect(diffTime(date2, date)).toBe(expected)
    expect(diffTime(date, date2)).toBe(-expected)
  })
})
