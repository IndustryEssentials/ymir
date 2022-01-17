import { format, getDateFromTimestamp,getUnixTimeStamp, calTimeLeft, calDuration, } from "../date"
import moment from 'moment'

describe("utils: date", () => {
  it("function: format. transfer utc to local", () => {
    const time = "2021-07-05T01:37:28.242Z" // utc format
    const expected = moment(time).local().format('YYYY-MM-DD HH:mm:ss')
    expect(format(time)).toBe(expected) // local date and time
  })
  it("function: getDateFromTimestamp. transfer utc to local", () => {
    const timestamp = "1642226485" // utc format
    const expected = moment(timestamp * 1000).local().format('YYYY-MM-DD HH:mm:ss')
    expect(getDateFromTimestamp(timestamp)).toBe(expected) // local date and time

    expect(getDateFromTimestamp())
  })
  it("function: getUnixTimeStamp. transfer utc to local", () => {
    const time = "2021-07-05T01:37:28.242Z" // utc format
    const expected = moment(time).local().format('YYYY-MM-DD HH:mm:ss')
    expect(format(time)).toBe(expected) // local date and time
  })
  it("function: calTimeLeft. transfer utc to local", () => {
    const time = "2021-07-05T01:37:28.242Z" // utc format
    const expected = moment(time).local().format('YYYY-MM-DD HH:mm:ss')
    expect(format(time)).toBe(expected) // local date and time
  })
  it("function: calDuration. transfer utc to local", () => {
    const time = "2021-07-05T01:37:28.242Z" // utc format
    const expected = moment(time).local().format('YYYY-MM-DD HH:mm:ss')
    expect(format(time)).toBe(expected) // local date and time
  })
})
