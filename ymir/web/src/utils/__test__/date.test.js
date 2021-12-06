import { format } from "../date"
import moment from 'moment'

describe("utils: date", () => {
  it("function: format. transfer utc to local", () => {
    const time = "2021-07-05T01:37:28.242Z" // utc format
    const expected = moment(time).local().format('YYYY-MM-DD HH:mm:ss')
    expect(format(time)).toBe(expected) // local date and time
  })
})
