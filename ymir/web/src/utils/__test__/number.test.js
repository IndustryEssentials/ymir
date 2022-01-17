import { format, getDateFromTimestamp,getUnixTimeStamp, calTimeLeft, calDuration, } from "../number"
import moment from 'moment'

describe("utils: number", () => {
  it("function: humanize. humanize number.", () => {
    const numbers = [
      {},
    ]
    const expected = moment(time).local().format('YYYY-MM-DD HH:mm:ss')
    expect(format(time)).toBe(expected) // local date and time
  })
  it("function: randomNumber. transfer utc to local", () => {
    const time = "2021-07-05T01:37:28.242Z" // utc format
    const expected = moment(time).local().format('YYYY-MM-DD HH:mm:ss')
    expect(format(time)).toBe(expected) // local date and time
  })
  it("function: randomBetween. transfer utc to local", () => {
    const time = "2021-07-05T01:37:28.242Z" // utc format
    const expected = moment(time).local().format('YYYY-MM-DD HH:mm:ss')
    expect(format(time)).toBe(expected) // local date and time
  })
})
