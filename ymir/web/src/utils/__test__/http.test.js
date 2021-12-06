import { status200 } from "../http"

describe("utils: http", () => {
  it("is a fuction that judge http status == 200", () => {
    expect(status200(200)).toBe(true)
    expect(status200(404)).toBe(false)
  })
})
