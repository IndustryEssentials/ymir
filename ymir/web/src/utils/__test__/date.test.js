import { format, getDateFromTimestamp,getUnixTimeStamp, calTimeLeft, calDuration, } from "../date"
import moment from 'moment'

describe("utils: date", () => {
  it("function: format. transfer utc to local", () => {
    const time = "2021-07-05T01:37:28.242Z" // utc format
    const expected = moment(time).local().format('YYYY-MM-DD HH:mm:ss')
    expect(format(time)).toBe(expected) // local date and time
  })
  it("function: getDateFromTimestamp. get local format date from timestamp(utc)", () => {
    const timestamp = "1625449048"
    const expected = '2021-07-05 09:37:28'
    expect(getDateFromTimestamp(timestamp)).toBe(expected)
  })
  it("function: getUnixTimeStamp. get timestamp from utc time", () => {
    const time = "2021-07-05T01:37:28.242Z"
    const expected = '1625449048'
    expect(getUnixTimeStamp(time)).toBe(expected)
  })
  it("function: calTimeLeft. calculate left time to 100%", () => {
    const time = moment().subtract({ months: 6 })
    const locale = 'zh-CN'
    const expected = '6 个月'
    expect(calTimeLeft(51, time, locale)).toBe(expected)
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
})
